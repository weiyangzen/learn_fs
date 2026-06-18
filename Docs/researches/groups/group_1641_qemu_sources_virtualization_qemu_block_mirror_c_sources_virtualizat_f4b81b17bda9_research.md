# Group Research: group_1641_qemu_sources_virtualization_qemu_block_mirror_c_sources_virtualizat_f4b81b17bda9

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/mirror.c -->
# File Research: sources/virtualization/qemu/block/mirror.c

## Purpose
Implements QEMU block mirroring and active commit jobs. It copies data from a source block graph node to a target, tracks concurrent guest writes through a temporary `mirror_top` filter, and completes by either leaving the synchronized target available or replacing a graph node with it.

## Main Entry Points
- `mirror_start()` starts a regular mirror job for `drive-mirror`/blockdev mirror workflows.
- `commit_active_start()` starts active commit by using the same mirror machinery with the base image as target.
- `mirror_start_job()` validates source/target topology, inserts the `mirror_top` filter, creates the dirty bitmap, takes permissions, configures job state, and starts the job.
- `mirror_run()` is the job coroutine: validates sizes, initializes bitmaps/buffers, performs initial dirty discovery/zeroing, runs background copy iterations, transitions to READY, drains, and exits.
- `mirror_iteration()` selects dirty extents, decides copy vs zero vs discard from block status, launches copy operations, and rate-limits progress.
- `mirror_complete()`, `mirror_cancel()`, `mirror_pause()`, `mirror_change()`, and `mirror_query()` implement job lifecycle control.
- `bdrv_mirror_top_*()` implements the temporary filter node’s read/write/zero/discard/flush behavior while the job is active.

## Internal Mechanics
`MirrorBlockJob` owns the target `BlockBackend`, the inserted filter node, source/base references, dirty bitmap, optional COW and zero bitmaps, in-flight bitmap, copy buffers, active-write counters, replacement target, error policies, and copy mode. Copy work is represented by `MirrorOp` objects stored in `ops_in_flight`; conflicting ranges wait on per-operation coroutine queues to preserve ordering.

Background mirroring clears dirty bits before checking block status, records a pseudo-op to block conflicting guest writes, marks chunks in flight, and then issues copy, zero, or discard operations. Read-copy operations use a fixed pool of granularity-sized aligned buffers; completion returns buffers to the free list, updates progress, and wakes waiters. Write failures re-mark ranges dirty and apply the configured block error policy.

The `mirror_top` filter provides consistent reads from the source while intercepting writes. In background copy mode it forwards guest writes to the source and marks the dirty bitmap. In write-blocking mode it prepares an active write op, forwards the write to the source, then synchronously writes the same range to the target, updating dirty/zero bitmaps and progress.

Completion drains the source, waits for all mirror and active writes, flushes the target, optionally adjusts target backing, replaces the selected graph node, removes the filter, unblocks replacement blockers, and restores read-only state for active commit error paths.

## Dependencies
Uses QEMU block job internals, block graph locks and permissions, dirty bitmap APIs, block backend I/O, coroutine queues, QEMU bitmaps, rate limiting, error-action policy, tracepoints, and block graph replacement/drain helpers.

## Risks and Notes
The code is highly concurrency-sensitive: correctness depends on dirty bitmap ordering, in-flight bitmap coverage, pseudo-op wakeups, and graph drain sections matching the current block graph. Active write mode intentionally uses bounce buffers because guest memory may change while the same data must be written to both source and target. Completion can fail late if the requested replacement node no longer has a safe relationship to the source. The dirty bitmap is manually managed by `mirror_top` rather than normal block-layer dirty tracking so the job can switch between background and write-blocking copy modes.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/mirror.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/monitor/bitmap-qmp-cmds.c -->
# File Research: sources/virtualization/qemu/block/monitor/bitmap-qmp-cmds.c

## Purpose
Implements QMP commands and shared helpers for QEMU block dirty bitmap management.

## Main Entry Points
- `block_dirty_bitmap_lookup()` validates node and bitmap names, locates the `BlockDriverState`, and returns the named bitmap.
- `qmp_block_dirty_bitmap_add()` creates a transient or persistent dirty bitmap with validated/default granularity and optional disabled state.
- `block_dirty_bitmap_remove()` checks busy/read-only state, removes persistent bitmap metadata when needed, and optionally releases the bitmap.
- `qmp_block_dirty_bitmap_remove()`, `qmp_block_dirty_bitmap_clear()`, `qmp_block_dirty_bitmap_enable()`, and `qmp_block_dirty_bitmap_disable()` expose simple QMP operations.
- `block_dirty_bitmap_merge()` merges local or external source bitmaps into a destination bitmap with rollback backup support.
- `qmp_block_dirty_bitmap_merge()` exposes merge through QMP.

## Internal Mechanics
The file is a thin validation and orchestration layer over the dirty-bitmap subsystem. It normalizes common lookup errors, enforces bitmap name/granularity rules, checks bitmap state flags before mutating, and handles persistent bitmap storage separately from in-memory release. Merge supports a list containing either local bitmap names on the destination node or external `{ node, name }` references. The first merge can create an `HBitmap` backup, and failures restore the destination from that backup.

## Dependencies
Uses QEMU block dirty bitmap APIs, block node lookup, QAPI-generated block command types, `HBitmap`, `QDict`/QAPI variant types, and QEMU error reporting.

## Risks and Notes
The merge rollback backup is only created once and reused for the whole batch, so the function treats the requested merge list as an atomic operation from the destination bitmap’s perspective. Persistent remove can fail before the in-memory bitmap is released, preserving metadata consistency. Bitmap operations rely on `bdrv_dirty_bitmap_check()` flag policies, so busy/read-only behavior is centralized in the block layer rather than reimplemented here.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/monitor/bitmap-qmp-cmds.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/monitor/block-hmp-cmds.c -->
# File Research: sources/virtualization/qemu/block/monitor/block-hmp-cmds.c

## Purpose
Implements human monitor protocol commands for block device management, block jobs, NBD server control, qemu-io access, and informational block/snapshot output. Most commands translate HMP arguments into QMP calls or block-layer helpers.

## Main Entry Points
- `hmp_drive_add()` and `hmp_drive_add_node()` hot-add legacy drives or node-owned block graphs.
- `hmp_drive_del()` removes a node or legacy drive/backend after checking blockers and ownership.
- `hmp_commit()`, `hmp_drive_mirror()`, `hmp_drive_backup()`, `hmp_block_stream()`, and block job control functions call the corresponding block job/QMP operations.
- `hmp_snapshot_blkdev*()` and `hmp_info_snapshots()` handle external/internal snapshots and snapshot listing.
- `hmp_nbd_server_start()`, `hmp_nbd_server_add()`, `hmp_nbd_server_remove()`, and `hmp_nbd_server_stop()` manage QEMU’s NBD export server.
- `hmp_block_resize()`, `hmp_block_set_io_throttle()`, `hmp_eject()`, and `hmp_change_medium()` adapt HMP arguments to QMP block device commands.
- `hmp_qemu_io()` runs qemu-io commands against a named backend, qdev block backend, or node.
- `hmp_info_block()`, `hmp_info_blockstats()`, and `hmp_info_block_jobs()` format query results for the monitor.

## Internal Mechanics
The command handlers parse `QDict` monitor arguments, build QAPI structs such as `DriveMirror`, `DriveBackup`, `NbdServerAddOptions`, and `BlockIOThrottle`, then delegate to QMP/block APIs. Informational functions call QMP query commands and print user-facing summaries through `monitor_printf()`.

`hmp_qemu_io()` is the most unusual path: it may operate directly on an existing `BlockBackend`, or create a temporary backend for a node. Its comments explicitly document incomplete permission restoration because qemu-io commands can change permissions and issue asynchronous operations whose lifetime extends beyond the monitor command.

Snapshot listing builds per-image queues of snapshot entries, detects snapshots present on all disks, prints global snapshots, then prints partial non-loadable snapshots per image.

## Dependencies
Uses monitor/HMP infrastructure, QMP block and block-export commands, QAPI block types, block backend and graph APIs, qemu-io command support, socket parsing, QemuOpts, machine defaults, snapshot APIs, and monitor formatting helpers.

## Risks and Notes
Most functions are compatibility adapters, so behavioral correctness depends on the underlying QMP command. `hmp_drive_del()` distinguishes node deletion from legacy drive deletion and refuses unsupported deletion of blockdev-add devices through the legacy path. `hmp_qemu_io()` deliberately leaves some permissions extended, which is a known tradeoff for legacy monitor semantics and asynchronous qemu-io behavior. `hmp_nbd_server_start -a` starts the server first, then exports all inserted block devices, and stops the server again if adding any export fails.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/monitor/block-hmp-cmds.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/monitor/meson.build -->
# File Research: sources/virtualization/qemu/block/monitor/meson.build

## Purpose
Adds the block monitor command sources to the appropriate QEMU Meson source sets.

## Main Entry Points
- `system_ss.add(files('block-hmp-cmds.c'))` builds HMP block monitor commands into the system emulator source set.
- `block_ss.add(files('bitmap-qmp-cmds.c'))` builds dirty bitmap QMP command helpers into the block source set.

## Internal Mechanics
This is a two-line build manifest with no conditional logic. It separates HMP system-emulator monitor code from block-layer QMP bitmap command code.

## Dependencies
Depends on QEMU’s Meson source-set variables `system_ss` and `block_ss`.

## Risks and Notes
The split is intentional: HMP commands are system-emulator-facing, while bitmap QMP helpers belong with block code and can be shared by block command infrastructure.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/monitor/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/nbd.c -->
# File Research: sources/virtualization/qemu/block/nbd.c

## Purpose
Implements QEMU’s NBD client block driver for `nbd`, `nbd+tcp`, and `nbd+unix` protocols. It parses NBD URLs/options, negotiates exports, translates block I/O to NBD commands, handles structured replies and block status, supports TLS, reconnects after transient disconnects, and participates in yank/cancel handling.

## Main Entry Points
- `nbd_open()` initializes state, parses options, registers yank support, creates the client connection, performs negotiation, and enables retry.
- `nbd_co_do_establish_connection()` connects and negotiates with the NBD server, registers yank, applies negotiated export information, and switches the channel to nonblocking coroutine mode.
- `nbd_co_send_request()` allocates one of 16 request slots, handles reconnect attempts, serializes request sending, and writes optional payload data.
- `nbd_receive_replies()` and `nbd_co_receive_one_chunk()` demultiplex replies by cookie and validate simple/structured reply headers.
- `nbd_client_co_preadv()`, `nbd_client_co_pwritev()`, `nbd_client_co_pwrite_zeroes()`, `nbd_client_co_flush()`, `nbd_client_co_pdiscard()`, and `nbd_client_co_block_status()` implement block driver I/O callbacks.
- `nbd_parse_filename()`, `nbd_parse_uri()`, `nbd_process_options()`, and `nbd_config()` map filename and QDict options into a `SocketAddress` and connection parameters.
- `nbd_close()`, `nbd_cancel_in_flight()`, `nbd_yank()`, and timer callbacks manage shutdown, cancellation, and reconnect/open timeout behavior.

## Internal Mechanics
`BDRVNBDState` stores the current `QIOChannel`, negotiated `NBDExportInfo`, request slot table, in-flight count, reconnect/open timers, send and receive coroutine mutexes, socket/TLS/export options, and the `NBDClientConnection`.

Requests use cookies derived from request slot indexes. Sending is protected by `send_mutex`; receiving is protected by `receive_mutex`. If a coroutine receives another request’s cookie, it wakes the owning coroutine and waits until its own reply is available. Structured replies are consumed chunk-by-chunk with an iterator that records fatal channel errors separately from per-request NBD errors.

The read path supports simple replies, `OFFSET_DATA`, and `OFFSET_HOLE`, including zero-filling holes and padding reads beyond an unaligned server EOF. Block status requests parse narrow and extended status chunks, clamp noncompliant lengths, map `NBD_STATE_HOLE`/`NBD_STATE_ZERO` to QEMU block status flags, and optionally expose `x-dirty-bitmap`/`qemu:allocation-depth` behavior.

Reconnect uses a state machine: connected, connecting with wait, connecting without wait, and quit. After socket `-EIO`, existing requests can pause for `reconnect-delay`; after that timer expires, delayed and future requests fail until a connection succeeds. Open timeout uses a separate timer during initial open.

## Dependencies
Uses QEMU NBD protocol/client helpers, QIO channels, QAPI socket/TLS visitors, QCrypto TLS credentials, block driver APIs, coroutine mutexes/queues, timers, yank infrastructure, QDict option parsing, GLib URI parsing, and tracepoints.

## Risks and Notes
The driver has strict concurrency invariants around `requests_lock`, `send_mutex`, `receive_mutex`, request cookies, and `s->reply.cookie`; protocol violations usually poison the channel. Reconnect only retries after errors treated as socket I/O failures, not semantic protocol errors. Open and reconnect timers must be deleted before drain/close, and the code asserts that no timers survive context changes. The block layer still uses sector-rounded sizes in places, so the driver explicitly handles tail reads/status beyond the advertised NBD export size.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/nbd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/nfs.c -->
# File Research: sources/virtualization/qemu/block/nfs.c

## Purpose
Implements QEMU’s native NFS block driver backed by libnfs. It opens a file inside an NFS export, integrates libnfs asynchronous I/O with QEMU’s AioContext, and exposes block read/write/flush/truncate/create/stat behavior.

## Main Entry Points
- `nfs_parse_filename()` and `nfs_parse_uri()` convert `nfs://host/path?...` URLs into QDict/QAPI options.
- `nfs_file_open()` opens the NFS file and sets total sectors and zero-init support.
- `nfs_client_open()` initializes libnfs, applies UID/GID/TCP/readahead/pagecache/debug options, mounts the export, opens or creates the file, and records size/stat metadata.
- `nfs_co_preadv()`, `nfs_co_pwritev()`, and `nfs_co_flush()` issue libnfs async operations and yield the current coroutine until callbacks schedule it again.
- `nfs_file_co_create()` and `nfs_file_co_create_opts()` create and size NFS-backed images.
- `nfs_file_co_truncate()`, `nfs_co_get_allocated_file_size()`, `nfs_reopen_prepare()`, `nfs_refresh_filename()`, `nfs_dirname()`, and `nfs_refresh_limits()` implement metadata and block driver support.
- `nfs_attach_aio_context()` and `nfs_detach_aio_context()` move libnfs fd handlers between AioContexts.

## Internal Mechanics
`NFSClient` stores the libnfs context, open file handle, currently registered poll events, AioContext, mutex, cached stat data, server/path, and runtime tuning values. `nfs_set_events()` translates libnfs requested events into QEMU `aio_set_fd_handler()` read/write callbacks. Those callbacks call `nfs_service()` under the client mutex and refresh event registration.

Each coroutine request creates an `NFSRPC` task containing the sleeping coroutine and optional stat/iovec storage. Libnfs callbacks store the result, copy data for older libnfs APIs when needed, report errors, and use `aio_co_schedule()` rather than direct wakeup so the coroutine does not re-enter while the mutex is still held.

Reads may allocate a bounce buffer for multi-iovec requests on libnfs API v2 and zero-pad short reads. Writes allocate/copy a contiguous buffer when libnfs cannot consume the provided iovec directly and require the full byte count to succeed.

## Dependencies
Uses libnfs, QEMU block driver APIs, AioContext fd handlers, coroutine scheduling, QAPI block-core visitors, QDict option conversion, GLib URI parsing, QemuOpts create options, trace/error-report helpers, and optional libnfs feature macros for readahead, pagecache, debug, unmount, and Windows differences.

## Risks and Notes
The file is built around libnfs async callbacks plus a mutex; the callback intentionally schedules rather than directly wakes coroutines to avoid deadlock on immediate follow-up requests. Reopen does not reconnect to the NFS server; it only validates mode/cache constraints and refreshes stat data for read-only reopen. Readahead/pagecache options are rejected with `cache.direct=on` and prevent later reopening with `BDRV_O_NOCACHE`. `nfs_dirname()` refuses to synthesize a base directory when UID/GID query parameters are needed, because dropping those parameters would change semantics.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/null.c -->
# File Research: sources/virtualization/qemu/block/null.c

## Purpose
Implements QEMU’s synthetic null block drivers: `null-co` for coroutine callbacks and `null-aio` for AIO callbacks. These drivers provide a configurable-size block node that discards writes, optionally returns zeroes on reads, and can emulate completion latency.

## Main Entry Points
- `null_open()` parses `size`, `latency-ns`, and `read-zeroes` runtime options and sets FUA write support.
- `null_co_parse_filename()` and `null_aio_parse_filename()` accept only `null-co://` or `null-aio://` respectively.
- `null_co_getlength()`, `null_co_preadv()`, `null_co_pwritev()`, and `null_co_flush()` implement coroutine-mode operations.
- `null_aio_preadv()`, `null_aio_pwritev()`, and `null_aio_flush()` implement AIO-mode operations through `NullAIOCB`.
- `null_co_block_status()` reports all requested bytes as offset-valid and optionally zero.
- `null_refresh_filename()` reconstructs exact filenames when only ignorable options are present.
- `bdrv_null_init()` registers both drivers.

## Internal Mechanics
`BDRVNullState` stores virtual length, optional latency, and read-zero behavior. Coroutine operations optionally sleep for `latency-ns` and otherwise complete successfully. AIO operations allocate a `NullAIOCB`; with latency they complete from a realtime timer, otherwise from a replay-safe bottom-half event. Reads fill the destination iovec with zeroes only when `read-zeroes=on`; otherwise read buffers are left untouched.

The block status callback reports a direct mapping to itself and adds `BDRV_BLOCK_ZERO` when configured. Allocated file size is always zero, reflecting that no storage is consumed.

## Dependencies
Uses QEMU block driver APIs, QemuOpts/QDict option parsing, coroutine sleep, AIO callbacks/timers, replay bottom-half scheduling, QEMUIOVector helpers, module registration, and block status flags.

## Risks and Notes
`latency-ns` must be nonnegative. `latency-ns` is deliberately excluded from strong runtime options and ignored when reconstructing an exact filename, while `size` and `read-zeroes` are strong runtime options. The driver supports FUA flags but does not persist anything; it is useful for tests, benchmarking plumbing, and sink-like block nodes rather than durable storage.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/null.c -->