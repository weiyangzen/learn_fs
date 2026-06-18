# Group Research: group_1639_qemu_sources_virtualization_qemu_block_export_vduse_blk_c_sources_v_68fb39b593d7

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/qemu` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/vduse-blk.c -->
# File Research: sources/virtualization/qemu/block/export/vduse-blk.c

## Purpose
Implements QEMU's `vduse-blk` block export driver, exposing a `BlockBackend` as a virtio-blk device through Linux VDUSE. It is a transport frontend around the shared virtio-blk request handler in `virtio-blk-handler.c`.

## Main Types
- `VduseBlkExport`: embeds `BlockExport`, owns `VirtioBlkHandler`, `VduseDev`, queue count, reconnect-log filename, atomic in-flight count, and virtqueue started state.
- `VduseBlkReq`: wraps a popped `VduseVirtqElement` with its `VduseVirtq`.

## Core Flow
1. `vduse_blk_exp_create()` validates export options:
   - `num-queues > 0`
   - `queue-size` power-of-two, greater than 2, within `VIRTQUEUE_MAX_SIZE`
   - `logical-block-size` via `check_block_size()`
   - rejects block export multi-threading.
2. It fills `VirtioBlkHandler` with backend, serial, logical block size, and writability.
3. It builds `virtio_blk_config` including capacity, queue topology, block size, discard and write-zeroes limits.
4. It creates a `VduseDev`, sets a reconnect log file under the temp dir, configures each queue, registers the device fd with the AioContext, adds AIO context notifiers, and installs `BlockDevOps`.
5. Queue kicks are delivered through eventfd handlers. `vduse_blk_vq_handler()` pops requests, increments the in-flight export reference counter, and runs each request in a coroutine.
6. `vduse_blk_virtio_process_req()` delegates request execution to `virtio_blk_process_req()` and, on success, pushes completion and decrements the in-flight counter.

## Draining and Lifetime
- Uses `vduse_blk_inflight_inc()` / `vduse_blk_inflight_dec()` to keep the export alive while requests are running.
- `vduse_blk_drained_begin()` disables queue fd handlers and marks queues stopped.
- `vduse_blk_drained_end()` re-enables queues and injects an eventfd kick to avoid missing reconnect activity.
- `vduse_blk_drained_poll()` waits while `inflight > 0`.
- `blk_set_disable_request_queuing(exp->blk, true)` is important because queued backend requests could prevent the in-flight counter from reaching zero during drain.

## Resize and Config Updates
- `vduse_blk_resize()` updates only the virtio config `capacity` field via `vduse_dev_update_config()`.

## Cleanup
- `vduse_blk_exp_delete()` asserts no in-flight requests, detaches fd handlers, removes AIO notifiers, destroys the VDUSE device, unlinks reconnect log unless destruction returns `-EBUSY`, and frees strings.
- `vduse_blk_exp_request_shutdown()` stops virtqueues.

## Notable Edge Case
- If `virtio_blk_process_req()` returns a negative error, `vduse_blk_virtio_process_req()` frees the request and returns without pushing completion and without calling `vduse_blk_inflight_dec()`. Since the in-flight count was incremented before coroutine entry, malformed requests appear able to leak the in-flight reference. This differs from the vhost-user frontend, which decrements in the error path.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/vduse-blk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/vduse-blk.h -->
# File Research: sources/virtualization/qemu/block/export/vduse-blk.h

## Purpose
Small public header for the VDUSE block export driver.

## Contents
- Header guard `VDUSE_BLK_H`.
- Includes `block/export.h`.
- Declares:
  - `extern const BlockExportDriver blk_exp_vduse_blk;`

## Role
Allows the block export registration layer to reference the `vduse-blk` export driver implemented in `vduse-blk.c`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/vduse-blk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/vhost-user-blk-server.c -->
# File Research: sources/virtualization/qemu/block/export/vhost-user-blk-server.c

## Purpose
Implements QEMU's `vhost-user-blk` block export server. It exposes a QEMU block backend as a virtio-blk device over the vhost-user protocol, using `VuServer`/libvhost-user infrastructure and the shared `VirtioBlkHandler`.

## Main Types
- `VuBlkReq`: request wrapper containing `VuVirtqElement`, `VuServer`, and queue pointer.
- `VuBlkExport`: embeds `BlockExport`, `VuServer`, `VirtioBlkHandler`, optional socket channel pointer, and cached `virtio_blk_config`.

## Request Flow
1. `vu_blk_process_vq()` pops descriptors from a `VuVirtq`.
2. Each request is assigned its server and queue, then run in a coroutine.
3. The server in-flight counter is incremented before coroutine entry.
4. `vu_blk_virtio_process_req()` calls `virtio_blk_process_req()`.
5. On success, `vu_blk_req_complete()` pushes the used descriptor and notifies the queue.
6. On both success and negative handler errors, the server in-flight counter is decremented.

## Virtio/vhost-user Interface
`vu_blk_iface` provides:
- `get_features`: advertises virtio-blk size, segment, topology, block size, flush, discard, write-zeroes, write-cache config, MQ, VERSION_1, indirect descriptors, event index, and vhost-user protocol features. Adds read-only when export is not writable.
- `queue_set_started`: installs or removes queue handler.
- `get_protocol_features`: supports config protocol feature.
- `get_config`: copies cached `virtio_blk_config`.
- `set_config`: only accepts frontend writes to `wce`, then calls `blk_set_enable_write_cache()`.
- `process_msg`: intercepts `VHOST_USER_NONE` disconnect and triggers the device panic handler instead of letting generic processing exit abruptly.

## Creation
`vu_blk_exp_create()`:
- Parses `logical-block-size`, defaulting to 512.
- Parses `num-queues`, defaulting to 1 and rejecting zero.
- Rejects multi-threaded block export mode.
- Initializes `VirtioBlkHandler`.
- Initializes virtio-blk config with capacity, block size, queue count, discard and write-zeroes limits.
- Registers AIO context notifiers and block device ops.
- Starts `vhost_user_server_start()` with provided socket address and queue count.

## Draining and Resize
- `vu_blk_drained_begin()` marks the server quiescing and detaches it from the AioContext.
- `vu_blk_drained_end()` clears quiescing and reattaches.
- `vu_blk_drained_poll()` waits while `co_trip` exists or requests are in flight.
- `vu_blk_exp_resize()` refreshes capacity and sends a config-change message.

## Cleanup
- `vu_blk_exp_request_shutdown()` stops the vhost-user server.
- `vu_blk_exp_delete()` removes AIO context notifiers and frees the handler serial.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/vhost-user-blk-server.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/vhost-user-blk-server.h -->
# File Research: sources/virtualization/qemu/block/export/vhost-user-blk-server.h

## Purpose
Small public header for the vhost-user block export driver.

## Contents
- Header guard `VHOST_USER_BLK_SERVER_H`.
- Includes `block/export.h`.
- Declares:
  - `extern const BlockExportDriver blk_exp_vhost_user_blk;`

## Role
Allows `block/export/export.c` or equivalent registration code to reference the vhost-user block export driver implemented in `vhost-user-blk-server.c`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/vhost-user-blk-server.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/virtio-blk-handler.c -->
# File Research: sources/virtualization/qemu/block/export/virtio-blk-handler.c

## Purpose
Shared virtio-blk request processor used by the VDUSE and vhost-user block export frontends. It translates virtqueue iovecs into QEMU `BlockBackend` coroutine operations.

## Request Validation
- Requires at least one output iovec for `virtio_blk_outhdr`.
- Requires at least one input iovec with space for trailing status byte.
- Strips the output header from the front of the output iovec list.
- Strips the status byte from the back of the input iovec list.
- Returns negative `-EINVAL` for structurally malformed requests.

## Range Checking
`virtio_blk_sect_range_ok()` enforces:
- Request size is 512-byte-sector aligned.
- Sector count is within `BDRV_REQUEST_MAX_SECTORS`.
- Byte offset is aligned to configured logical block size.
- Request range fits inside backend geometry from `blk_co_get_geometry()`.

## Supported Commands
- `VIRTIO_BLK_T_IN`: reads from backend into input iovecs.
- `VIRTIO_BLK_T_OUT`: writes output iovecs to backend if handler is writable.
- `VIRTIO_BLK_T_FLUSH`: calls `blk_co_flush()`.
- `VIRTIO_BLK_T_GET_ID`: copies handler serial into input iovecs, capped by `VIRTIO_BLK_ID_BYTES`.
- `VIRTIO_BLK_T_DISCARD`: validates one discard/write-zeroes descriptor, rejects unsupported flags, then calls `blk_co_pdiscard()`.
- `VIRTIO_BLK_T_WRITE_ZEROES`: validates descriptor and calls `blk_co_pwrite_zeroes()`, optionally with `BDRV_REQ_MAY_UNMAP`.
- Unknown commands return `VIRTIO_BLK_S_UNSUPP`.

## Status Handling
The function writes a virtio status byte into the request's final input buffer:
- `VIRTIO_BLK_S_OK` on success.
- `VIRTIO_BLK_S_IOERR` on backend/range/writable failures.
- `VIRTIO_BLK_S_UNSUPP` for unsupported commands or unsupported flags.

## Return Value
Returns the total input iovec length including the status byte so the transport frontend can push the used length back to the virtqueue.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/virtio-blk-handler.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/export/virtio-blk-handler.h -->
# File Research: sources/virtualization/qemu/block/export/virtio-blk-handler.h

## Purpose
Defines the shared virtio-blk export handler interface used by transport-specific export drivers.

## Contents
- Includes `system/block-backend.h`.
- Defines virtio sector constants:
  - `VIRTIO_BLK_SECTOR_BITS = 9`
  - `VIRTIO_BLK_SECTOR_SIZE = 512`
- Defines maximum discard and write-zeroes sector counts, both `32768`.
- Defines `VirtioBlkHandler`:
  - `BlockBackend *blk`
  - `char *serial`
  - `uint32_t logical_block_size`
  - `bool writable`
- Declares:
  - `virtio_blk_process_req(...)`

## Role
Provides a transport-neutral contract: frontends supply virtqueue iovecs and handler configuration, and the implementation performs virtio-blk command decoding and backend I/O.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/export/virtio-blk-handler.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/file-posix.c -->
# File Research: sources/virtualization/qemu/block/file-posix.c

## Purpose
POSIX implementation of QEMU's raw `file`, `host_device`, and platform-specific `host_cdrom` block protocol drivers. It is the main Unix host file/device backend for block I/O, covering regular files, block devices, character devices, SCSI generic passthrough, direct I/O alignment, page-cache handling, sparse allocation queries, discard/write-zeroes, copy offload, zoned devices, permissions, and file creation.

## Main State
`BDRVRawState` stores:
- Host file descriptor and open flags.
- File/device type.
- Locking mode and current/shared block permissions.
- Byte-lock bookkeeping for QEMU permission enforcement.
- Reopen/permission-change fd state.
- AIO backend flags: Linux AIO, io_uring, AIO batch size, `fdatasync` support.
- Capabilities for discard, write-zeroes, fallocate.
- Alignment state: request alignment, buffer alignment, forced alignment.
- Live migration cache-drop options.
- Discard statistics.
- Optional persistent reservation manager.

`RawPosixAIOData` is the thread-pool/native-AIO work packet for read/write, flush, ioctl, copy-range, truncate, zone report, and zone management operations.

## Opening and Options
`raw_open_common()` handles most open logic for both regular files and host devices:
- Parses `filename`, `aio`, `aio-max-batch`, `locking`, `pr-manager`, `drop-cache`, and `x-check-cache-dropped`.
- Supports `aio=threads`, `aio=native`, and, when built, `aio=io_uring`.
- Requires `cache.direct=on` for Linux native AIO.
- Checks io_uring availability when requested.
- Applies auto-read-only logic via `raw_parse_flags()`.
- Opens the path, checks writable block-device state with `BLKROGET`, validates file type, initializes discard/write-zeroes capabilities, and sets block-layer supported flags.
- Rejects non-regular files for the `file` driver and non-device files for host-device mode.
- For zoned devices, rejects buffered I/O because host page cache cannot preserve required write ordering.

## Alignment Handling
- Probes logical block size through available ioctls.
- Probes physical block size when possible.
- Detects direct-I/O request and memory alignment by issuing trial reads.
- Special-cases NFS as byte-aligned for direct I/O.
- Falls back to conservative alignment when probing cannot provide exact data.
- Exposes `min_mem_alignment`, `opt_mem_alignment`, request alignment, discard alignment, and write-zeroes alignment to the block layer.

## Permission and Locking Model
The driver maps QEMU block permissions to byte-range locks:
- Permission lock bytes start at `RAW_LOCK_PERM_BASE`.
- Shared-permission lock bytes start at `RAW_LOCK_SHARED_BASE`.
- `raw_apply_lock_bytes()` locks/unlocks bytes.
- `raw_check_lock_bytes()` probes conflicting locks from other processes.
- `raw_handle_perm_lock()` implements prepare/commit/abort around permission updates.
- Reopen can duplicate or reopen the fd and transfer locks to the replacement fd in `raw_check_perm()` / `raw_set_perm()`.

## I/O Path
`raw_co_prw()` is the central read/write path:
- Checks fd validity.
- For zoned writes/appends, serializes through zone write-pointer mutex and updates tracked write pointers.
- Uses io_uring when enabled and aligned.
- Uses Linux AIO when enabled, available, and aligned.
- Falls back to the coroutine thread pool.
- Thread-pool read/write uses `preadv/pwritev` when available, otherwise linearizes iovecs into aligned buffers.
- Short reads are zero-filled; short writes return error.
- FUA write requests are followed by flush when the selected backend cannot provide native FUA.

## Flush and Page Cache
- `raw_co_flush_to_disk()` uses io_uring, Linux AIO fdatasync, or thread-pool `qemu_fdatasync()`.
- Failed buffered `fdatasync()` marks `page_cache_inconsistent`, causing future flushes to fail permanently because dirty pages may have been lost.
- `raw_co_invalidate_cache()` flushes and uses `posix_fadvise(..., DONTNEED)` on Linux when `drop-cache` is enabled and not using `O_DIRECT`.
- Optional `x-check-cache-dropped` verifies cache eviction via `mincore()`.

## Allocation, Creation, and Truncation
- `raw_co_create()` creates files with optional `nocow`, preallocation, and extent-size hint.
- Uses permission locks during creation to prevent conflicting resize/write access.
- Supports preallocation modes `off`, `full`, and optionally `falloc`.
- Uses `FS_NOCOW_FL` where available for btrfs-like behavior.
- Uses `FS_IOC_FSSETXATTR` to set extent-size hints when supported.
- `raw_regular_truncate()` delegates blocking truncate/preallocate work to the thread pool.
- `find_allocation()` uses `SEEK_DATA`/`SEEK_HOLE` where available.
- `raw_co_block_status()` reports data/zero extents and treats unknown sparse info conservatively as data.

## Discard, Write Zeroes, and Copy Offload
- Regular-file discard uses `fallocate(PUNCH_HOLE|KEEP_SIZE)` where available, or macOS `F_PUNCHHOLE`.
- Block-device discard uses `BLKDISCARD`.
- Block-device write-zeroes uses `BLKZEROOUT` when allowed.
- Regular-file write-zeroes tries `FALLOC_FL_ZERO_RANGE`, hole punching plus reallocation, or fallocate extension.
- `BDRV_REQ_MAY_UNMAP` selects the unmap-capable write-zeroes path.
- Discard successes/failures and discarded bytes are tracked in file-specific stats.
- `raw_co_copy_range_to()` uses host `copy_file_range()` only when both source and destination are the raw POSIX driver.

## Zoned Device Support
When `CONFIG_BLKZONED` is enabled:
- Reads zoned model and limits from sysfs.
- Tracks zone size, number of zones, max open/active zones, max append sectors, and write granularity.
- Maintains in-memory zone write pointers.
- Implements zone report using `BLKREPORTZONE`.
- Implements open/close/finish/reset through Linux zone ioctls.
- Implements zone append through the normal write path with write-pointer updates.
- Resets or refreshes tracked write pointers after zone-management operations and failed writes.

## Host Device Support
When `HAVE_HOST_BLOCK_DEVICE` is enabled:
- `hdev_probe_device()` recognizes character and block devices.
- `hdev_open()` opens device mode, detects Linux SCSI generic devices, and disables dm-multipath SG_IO retry logic for SG devices.
- Linux SG_IO supports persistent reservations via `PRManager` for `PERSISTENT_RESERVE_IN/OUT`.
- dm-multipath retry handling probes paths with `DM_MPATH_PROBE_PATHS`, retries transient `EAGAIN`, and classifies SG_IO path errors.
- Host-device block ops reuse raw read/write/flush/copy/truncate/length paths and add block-size and geometry probes.
- Host-device discard/write-zeroes set a block-device flag so ioctl paths are used.

## CD-ROM Support
- Linux `host_cdrom` opens with `O_NONBLOCK`, detects CD drives via `CDROM_DRIVE_STATUS`, supports inserted/eject/close-tray/lock-door ioctls, and exposes SG_IO.
- FreeBSD `host_cdrom` opens through raw device logic, unlocks the door, can reopen after media changes, and supports inserted/eject/lock operations.
- macOS helper code maps `/dev/cdrom` to an ejectable optical media BSD path using IOKit and emits unmount/remount guidance when needed.

## Registered Drivers
- Always registers `bdrv_file`.
- Registers `bdrv_host_device` when host block devices are enabled.
- Registers `bdrv_host_cdrom` on Linux and FreeBSD variants when available.
- Registration order intentionally matters because later drivers are probed first.

## Important Interactions
- This file is a foundational backend for higher-level block formats and exports.
- Export drivers in this group ultimately depend on these raw file/device protocol drivers when their `BlockBackend` points at local host storage.
- Permission locking is advisory and only works between cooperating QEMU-like processes using the same byte-lock convention.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/file-posix.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/file-win32.c -->
# File Research: sources/virtualization/qemu/block/file-win32.c

## Purpose
Windows implementation of QEMU's raw `file` and `host_device` block protocol drivers.

## Main State
- `BDRVRawState` stores Windows `HANDLE`, detected type (`file`, `cd`, `harddisk`), drive path, and optional `QEMUWin32AIOState`.
- `RawWin32AIOData` carries thread-pool AIO work: handle, iovecs, byte count, offset, and operation type.
- `BDRVRawReopenState` carries a replacement handle during reopen.

## I/O Model
- For native Windows AIO, `raw_aio_preadv()` and `raw_aio_pwritev()` use `win32_aio_submit()`.
- Otherwise, operations use `thread_pool_submit_aio()` with `aio_worker()`.
- Thread-pool read/write loops over iovecs and uses `ReadFile`/`WriteFile` with an `OVERLAPPED` offset.
- Short reads are treated as EOF and zero-fill the remaining guest buffer.
- Flush uses `FlushFileBuffers()`.

## Opening
`raw_open()`:
- Parses `filename`, `aio`, and `locking`.
- Rejects `locking=on` on Windows.
- Computes access flags and `FILE_FLAG_OVERLAPPED`/`FILE_FLAG_NO_BUFFERING` based on AIO and cache mode.
- Tracks a drive root path for alignment and filesystem queries.
- Opens with `CreateFile(..., OPEN_EXISTING, ...)`.
- Initializes Win32 AIO when requested.
- Marks truncate extension as zero-initialized via `BDRV_REQ_ZERO_WRITE`.

## Alignment and Length
- `raw_probe_alignment()` uses disk geometry, `GetDiskFreeSpace()`, or fallback 512-byte alignment. CD-ROMs use 2048.
- `raw_co_getlength()` handles regular files, CD media size, and hard-disk geometry.
- Allocated size uses `GetCompressedFileSizeA()` if available, then falls back to `_stati64()`.

## Create/Truncate/Reopen
- `raw_co_create()` creates/truncates a sparse file and rejects preallocation and nocow.
- `raw_co_truncate()` uses `SetFilePointer()` and `SetEndOfFile()`, rejecting preallocation.
- Reopen only supports files, not devices; it opens a replacement handle, attaches it to AIO if needed, then commits or aborts.

## Host Device Support
- `find_cdrom()` locates a CD-ROM drive.
- `find_device_type()` classifies `\\.\PhysicalDrive*`, drive letters, fixed/removable drives, and CD-ROMs.
- `hdev_probe_device()` gives priority to `/dev/cdrom` and Windows drive syntax.
- `hdev_open()` maps `/dev/cdrom` and bare drive letters to Windows device paths, rejects native AIO for host devices, opens with `CreateFile()`, and sets type.
- Host-device driver uses the same read/write/flush/length code as regular file driver and marks variable length.

## Registered Drivers
- `bdrv_file`: `file` protocol for regular Windows files.
- `bdrv_host_device`: `host_device` protocol for Windows drives/devices.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/file-win32.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/filter-compress.c -->
# File Research: sources/virtualization/qemu/block/filter-compress.c

## Purpose
Implements the `compress` block filter driver. It forces writes through the child with `BDRV_REQ_WRITE_COMPRESSED`, allowing compression-capable underlying formats to receive compressed-write requests.

## Open Behavior
- Opens a single `file` child with `bdrv_open_file_child()`.
- Under graph read lock, checks that the child has a driver and that `block_driver_can_compress()` is true.
- Fails with `-ENOTSUP` if the underlying format does not support compression.
- Exposes supported write flags as `BDRV_REQ_WRITE_UNCHANGED` plus child FUA if available.
- Exposes supported zero flags as `BDRV_REQ_WRITE_UNCHANGED` plus child FUA, may-unmap, and no-fallback flags if available.

## I/O Behavior
- `compress_co_getlength()` forwards to child length.
- `compress_co_preadv_part()` forwards reads unchanged.
- `compress_co_pwritev_part()` forwards writes with `BDRV_REQ_WRITE_COMPRESSED` added.
- Zero writes and discards are forwarded unchanged.
- Eject and lock-medium operations are forwarded to the child.

## Limits
- `compress_refresh_limits()` asks the child for `BlockDriverInfo`; if it has a nonzero cluster size, it sets request alignment to that cluster size.

## Driver Registration
- Registers `bdrv_compress` with format name `compress`.
- Marks `.is_filter = true`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/filter-compress.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/graph-lock.c -->
# File Research: sources/virtualization/qemu/block/graph-lock.c

## Purpose
Implements QEMU block graph locking: a reader/writer mechanism protecting block graph topology mutations such as adding/removing nodes and edges.

## Main State
- `graph_lock`: dummy lock object used for thread-safety analysis annotations.
- `aio_context_list_lock`: protects the list of AioContext graph-lock counters and orphaned reader count.
- `has_writer`: atomic flag indicating a writer is active or trying to become active.
- `wrlock_quiesced_counter`: tracks write locks taken through drained sections.
- `orphaned_reader_count`: preserves reader counts when an AioContext is unregistered while readers exist.
- `reader_queue`: coroutine queue for graph readers waiting on a writer.
- `BdrvGraphRWlock`: per-AioContext reader counter plus list linkage.

## AioContext Registration
- `register_aiocontext()` allocates a per-context `BdrvGraphRWlock` and inserts it into the global list.
- `unregister_aiocontext()` transfers its reader count to `orphaned_reader_count`, removes it, and frees it.
- `reader_count()` sums orphaned readers plus all per-context atomic reader counts.

## Writer Lock
`bdrv_graph_wrlock()`:
- Global-state, non-coroutine only.
- Drains all block devices when not already in a quiesced write-lock section.
- Alternates `has_writer` off while polling to avoid deadlock with callbacks that need read locks.
- Sets `has_writer = 1`, uses a memory barrier, and loops until total reader count is zero.
- Ends the temporary drain after lock acquisition when applicable.

`bdrv_graph_wrlock_drained()`:
- Begins a drained section first, increments `wrlock_quiesced_counter`, then takes the write lock.

`bdrv_graph_wrunlock()`:
- Clears `has_writer` under `aio_context_list_lock`.
- Wakes all queued readers.
- Polls bottom halves on the main AioContext so scheduled graph cleanup can run.
- Ends a drained section if the write lock was acquired through the drained helper.

## Reader Lock
`bdrv_graph_co_rdlock()`:
- Coroutine-only.
- Increments the current AioContext reader count.
- Uses a memory barrier before checking `has_writer`.
- Fast path proceeds when no writer is active.
- Slow path synchronizes with writer/unlock using `aio_context_list_lock`, decrements its reader count, kicks waiters, and sleeps on `reader_queue`.

`bdrv_graph_co_rdunlock()`:
- Decrements the reader count with release semantics.
- Uses a memory barrier and always calls `aio_wait_kick()` because a writer may be polling with `has_writer` temporarily cleared.

## Main-Loop Read Lock Stubs
- `bdrv_graph_rdlock_main_loop()` and `bdrv_graph_rdunlock_main_loop()` assert global-state, non-coroutine context.
- In this implementation, main-loop readability is effectively asserted rather than counted.

## Assertions
- `assert_bdrv_graph_readable()` checks, in debug graph-lock builds, that the caller is either in the main thread or there is an active reader.
- `assert_bdrv_graph_writable()` requires main thread and `has_writer`.

## Concurrency Notes
The design avoids cacheline bouncing by keeping reader counters per AioContext, while writer acquisition pays the cost of summing all counters. The orphaned-reader mechanism prevents counter loss when coroutines migrate or AioContexts are deleted.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/graph-lock.c -->