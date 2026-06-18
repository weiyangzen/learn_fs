# Group Research: group_1640_qemu_sources_virtualization_qemu_block_io_c_sources_virtualization__4e1576042746

Scope confirmed against `Docs/research_subset_a.md`: all listed files are under `sources/virtualization/qemu`, which is included in subset A. Each source file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/io.c -->
# File Research: sources/virtualization/qemu/block/io.c

## Role

`block/io.c` is QEMU's central block-layer I/O implementation. It sits between block users and individual `BlockDriver` implementations, enforcing request validation, alignment, serialization, drain/quiesce semantics, dirty tracking, copy-on-read, zero/discard behavior, flushing, block-status traversal, copy-range delegation, truncation, VM-state I/O, zoned operations, and registered-buffer propagation.

This file is not a protocol or format driver. It is the shared I/O policy layer that normalizes requests before they reach drivers such as raw, qcow2, iSCSI, file-posix, linux-aio, and io_uring.

## Major Responsibilities

- Maintains parent drain notifications through `bdrv_parent_drained_begin()`, `bdrv_parent_drained_end()`, and `bdrv_parent_drained_poll()`.
- Refreshes inherited and driver-specific `BlockLimits` with `bdrv_refresh_limits()`.
- Tracks copy-on-read enablement with an atomic reference count via `bdrv_enable_copy_on_read()` and `bdrv_disable_copy_on_read()`.
- Implements top-level and all-node drain operations through `bdrv_drained_begin()`, `bdrv_drained_end()`, `bdrv_drain()`, `bdrv_drain_all_begin()`, `bdrv_drain_all_end()`, and related helpers.
- Tracks active requests in `BdrvTrackedRequest` lists so overlapping serializing requests wait instead of racing.
- Validates offsets, byte counts, I/O vectors, and maximum request sizes through `bdrv_check_qiov_request()`, `bdrv_check_request()`, and internal 32-bit bounded checks.
- Routes aligned reads, writes, compressed writes, write-zeroes, flushes, discards, ioctls, zoned operations, VM-state I/O, copy-range, and truncation requests to block drivers.
- Handles unaligned read/write padding with bounce buffers and read-modify-write cycles.
- Walks backing/filter chains for block allocation status and zero detection.

## Drain and Quiesce Model

The drain path prevents new activity and waits for in-flight operations to complete. `bdrv_do_drained_begin()` increments `bs->quiesce_counter`; on the first transition it notifies parents and calls `drv->bdrv_drain_begin` if present. If polling is requested, it waits while parent callbacks or `bs->in_flight` indicate work remains.

Coroutine callers cannot directly run the drain body, so `bdrv_co_yield_to_drain()` schedules a bottom half and yields. This prevents recursive coroutine entry and ensures drain operations run from an appropriate main-loop/global-state context. `bdrv_drain_all_begin()` applies this across all BDS nodes, while `bdrv_drain_all_begin_nopoll()` only quiesces and leaves polling to the caller.

Record/replay mode short-circuits all-node drains because waiting on the block queue can be non-terminating under replay semantics.

## Request Tracking and Serialization

`tracked_request_begin()` inserts a request into `bs->tracked_requests`; `tracked_request_end()` removes it and wakes any waiters. Requests can become serializing via `tracked_request_set_serialising()` or `bdrv_make_request_serialising()`, which expands the overlap range to an alignment boundary such as the cluster size.

`bdrv_find_conflicting_request()` detects overlapping serializing requests and makes the current coroutine wait on the conflicting request's queue. It asserts against reentrant self-waits, because a block driver issuing nested overlapping requests would deadlock. This is especially important for:
- copy-on-read cluster allocation,
- unaligned write read-modify-write,
- truncate preallocation/growth regions,
- explicit `BDRV_REQ_SERIALISING` write requests.

## Alignment, Padding, and Bounce Buffers

The block layer enforces `bs->bl.request_alignment`. Misaligned requests are padded by `bdrv_pad_request()` using `BdrvRequestPadding`.

For writes, padding requires read-modify-write: `bdrv_padding_rmw_read()` reads head/tail regions, then the write path merges caller data with preserved bytes. For reads, padding expands the request and copies back into the original iovec in `bdrv_padding_finalize()` if vector elements had to be collapsed.

`bdrv_create_padded_qiov()` ensures the padded vector never exceeds `IOV_MAX`; if needed it collapses initial vector elements into a temporary aligned bounce buffer. This avoids invalid vector submission while preserving the caller-visible layout.

## Read Path

`bdrv_co_preadv_part()` is the public coroutine read entry point. It:
- checks medium presence,
- validates request and qiov bounds,
- applies copy-on-read if `bs->copy_on_read` is nonzero,
- pads the request if required,
- tracks the request,
- calls `bdrv_aligned_preadv()`.

`bdrv_aligned_preadv()` handles copy-on-read serialization and dispatch. It fragments large reads by `bs->bl.max_transfer`, reads beyond EOF as zeroes, and strips copy-on-read once handled.

`bdrv_co_do_copy_on_readv()` implements copy-on-read. It rounds the affected area to subcluster or cluster boundaries, checks allocation, reads unallocated data through a bounce buffer, writes it back to the image using normal write or write-zeroes, then copies the requested bytes to the caller unless the request is a prefetch.

## Write and Zero-Write Path

`bdrv_co_pwritev_part()` validates and pads writes, tracks the request, and dispatches either normal writes or `BDRV_REQ_ZERO_WRITE`.

`bdrv_aligned_pwritev()` prepares the write with `bdrv_co_write_req_prepare()`, checks read-only/bitmap permissions, serializes if needed, updates write thresholds, detects all-zero buffers when `detect_zeroes` is enabled, and then dispatches one of:
- `bdrv_co_do_pwrite_zeroes()` for zero writes,
- `bdrv_driver_pwritev_compressed()` for compressed writes,
- `bdrv_driver_pwritev()` for regular writes.

Large writes are split by `max_transfer`; emulated FUA is applied only on the final chunk when the driver cannot support FUA natively.

`bdrv_co_do_pwrite_zeroes()` first tries the driver's efficient `bdrv_co_pwrite_zeroes` operation, honoring `BDRV_REQ_MAY_UNMAP`, `BDRV_REQ_NO_FALLBACK`, and FUA semantics. If unsupported and fallback is allowed, it writes an aligned zero-filled bounce buffer. It invalidates block-status cache ranges that overlap the zero write.

`bdrv_co_do_zero_pwritev()` handles unaligned zero writes by doing padding-specific read-modify-write for edge regions and efficient aligned zero writes for the middle.

## Driver Dispatch

Driver-facing helpers normalize old and new block driver APIs:
- `bdrv_driver_preadv()` supports `bdrv_co_preadv_part`, `bdrv_co_preadv`, `bdrv_aio_preadv`, or legacy sector-based `bdrv_co_readv`.
- `bdrv_driver_pwritev()` supports `bdrv_co_pwritev_part`, `bdrv_co_pwritev`, `bdrv_aio_pwritev`, or legacy sector-based `bdrv_co_writev`.
- `bdrv_driver_pwritev_compressed()` supports compressed write APIs.
- `CoroutineIOCompletion` bridges callback-style AIO into coroutine waits.

This file therefore preserves compatibility between coroutine-native drivers and older callback/sector-oriented drivers.

## Flush, Discard, and Cache Effects

`bdrv_co_flush()` coalesces concurrent flushes with `bs->active_flush_req`, uses `write_gen`/`flushed_gen` to skip redundant disk flushes, honors `BDRV_O_NO_FLUSH`, and recursively flushes writable children. It supports driver-level all-in-one flush, flush-to-OS, flush-to-disk, and legacy AIO flush.

`bdrv_flush_all()` flushes every BDS, including unreachable nodes, except under replay mode.

`bdrv_co_pdiscard()` validates discard support, respects `BDRV_O_UNMAP`, invalidates block-status cache, fragments requests based on `pdiscard_alignment` and `max_pdiscard`, tolerates rejected unaligned head/tail discards, and updates dirty/request tracking through the write-finish path.

## Block Status and Zero Detection

`bdrv_co_do_block_status()` is the core status query. It:
- clamps to image length,
- falls back to allocated data for drivers without block-status support,
- rounds queries to request alignment,
- uses block-status cache for protocol nodes with no children,
- handles filter nodes through `BDRV_BLOCK_RAW`,
- synthesizes allocation/zero status from backing chains,
- optionally recurses into underlying files to refine zero status.

`bdrv_co_common_block_status_above()` walks filter/COW chains above a base node. Public helpers include:
- `bdrv_co_block_status_above()`,
- `bdrv_co_block_status()`,
- `bdrv_co_is_zero_fast()`,
- `bdrv_co_is_all_zeroes()`,
- `bdrv_co_is_allocated()`,
- `bdrv_co_is_allocated_above()`.

`bdrv_co_is_all_zeroes()` has a fast block-status probe and a small allocated-head fallback read capped by `MAX_ZERO_CHECK_BUFFER`.

## Copy Range and Registered Buffers

`bdrv_register_buf()` and `bdrv_unregister_buf()` recursively propagate host buffer registration to drivers and children. Registration rollback unwinds already-registered children if a later registration fails.

`bdrv_co_copy_range_internal()` implements both source-recursive and destination-recursive copy-range delegation. It validates source and destination, rejects encrypted nodes and missing driver callbacks, tracks either a read or write request, and delegates to `bdrv_co_copy_range_from` or `bdrv_co_copy_range_to`.

## Truncate and Resize

`bdrv_co_truncate()` validates permissions and size, serializes newly grown regions, handles backing-file exposure by forcing zero-fill when growth would reveal backing data, calls driver/filter truncate, refreshes total sectors, updates dirty bitmaps, and notifies parents through resize callbacks.

## Other Interfaces

The file also provides:
- VM-state read/write helpers and buffer wrappers,
- synchronous AIO cancellation wrappers,
- `bdrv_co_ioctl()`,
- zoned block operations: report, management, append,
- aligned memory allocation helpers,
- in-flight cancellation dispatch,
- snapshot-specific read/status/discard helpers.

## Important Invariants

- Requests must not exceed `BDRV_MAX_LENGTH`; many driver-facing requests are further capped by `BDRV_REQUEST_MAX_BYTES`.
- Alignment-sensitive drivers receive aligned requests after padding or fragmentation.
- `bs->in_flight` is incremented around operations that must be visible to drain.
- Request serialization prevents overlapping cluster allocation, RMW, truncate, and explicit serializing writes from racing.
- Dirty bitmap and parent resize notifications are updated only after write/truncate success paths that change visible state.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/io.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/io_uring.c -->
# File Research: sources/virtualization/qemu/block/io_uring.c

## Role

`block/io_uring.c` provides QEMU's Linux `io_uring` coroutine submission backend for block/file I/O. It converts QEMU raw AIO request types into liburing SQEs, waits for CQE completion through QEMU's AioContext infrastructure, and resumes the submitting coroutine.

## Core Data Structure

`LuringRequest` is stack allocated by `luring_co_submit()` and carries:
- submitting coroutine,
- target `QEMUIOVector`,
- file descriptor,
- byte offset,
- request type,
- request flags,
- result,
- short-I/O progress,
- resubmission iovec,
- `CqeHandler`.

Because the request lives on the coroutine stack, completion wakes the same coroutine rather than invoking an arbitrary user callback.

## Submission

`luring_co_submit()` initializes `LuringRequest`, sets its CQE handler, calls `aio_add_sqe()`, and yields while `req.ret == -EINPROGRESS`. Completion sets `req.ret` and wakes the coroutine unless it is already entered.

`luring_prep_sqe()` builds the actual SQE:
- `QEMU_AIO_WRITE`: uses `io_uring_prep_writev2` with `RWF_DSYNC` for FUA when available, otherwise writev/write.
- `QEMU_AIO_ZONE_APPEND`: currently submits writev at the supplied offset.
- `QEMU_AIO_READ`: uses readv/read depending on vector count.
- `QEMU_AIO_FLUSH`: uses `io_uring_prep_fsync(..., IORING_FSYNC_DATASYNC)`.

Single-element iovecs use non-vectored read/write because the code notes those are faster according to the man page.

## Completion and Retry Behavior

`luring_cqe_handler()` translates CQE results to QEMU status:
- `-EINTR` and `-EAGAIN` are immediately resubmitted. The comment says `-EAGAIN` is not expected for regular files or host block devices but is known with Linux SCSI.
- Full read/write completion returns `0`.
- Short reads and writes are resubmitted with `luring_resubmit_short_io()`.
- Read EOF pads the remaining buffer with zeroes and succeeds.
- Write returning zero, or zone append returning fewer bytes than requested, becomes `-ENOSPC`.

`luring_resubmit_short_io()` advances `total_done`, builds a sliced `resubmit_qiov`, and submits another SQE for the remaining range.

## FUA Support

`luring_has_fua()` returns true only when QEMU was built with `HAVE_IO_URING_PREP_WRITEV2`. Without that API, FUA must not be requested through this backend; the write path asserts that `RWF_DSYNC` is zero.

## Integration Points

This file is selected by Meson when `linux_io_uring` is available. Higher-level block code, usually through raw/file backends, calls `luring_co_submit()` for coroutine-style I/O.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/io_uring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/iscsi-opts.c -->
# File Research: sources/virtualization/qemu/block/iscsi-opts.c

## Role

`block/iscsi-opts.c` registers static QEMU command-line/configuration options for the iSCSI block driver. It is separate from `iscsi.c` so global `-iscsi` options can be registered when libiscsi support is present.

## Registered Option List

The file defines `qemu_iscsi_opts` with `.name = "iscsi"` and these options:
- `user`: CHAP username.
- `password`: CHAP password.
- `password-secret`: secret object ID containing the CHAP password.
- `header-digest`: HeaderDigest setting, with accepted textual forms listed in help.
- `initiator-name`: initiator IQN name.
- `timeout`: request timeout in seconds, where default `0` means no timeout.

## Initialization

`iscsi_block_opts_init()` calls `qemu_add_opts(&qemu_iscsi_opts)`. The file uses:
- `block_init(iscsi_block_opts_init)` to register at block initialization time.
- `module_opts("iscsi")` to associate the option set with the iSCSI module.

## Relationship to `iscsi.c`

`iscsi.c` later reads these options through `qemu_find_opts("iscsi")` and merges target-specific/default settings into runtime QDict options. This file only declares the user-visible option schema; it does not open connections or implement I/O.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/iscsi-opts.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/iscsi.c -->
# File Research: sources/virtualization/qemu/block/iscsi.c

## Role

`block/iscsi.c` implements QEMU's iSCSI and iSER block protocol drivers using libiscsi. It connects to a remote target/LUN, probes SCSI capacity and capabilities, exposes the LUN as a `BlockDriverState`, and implements read, write, flush, discard, write-zeroes, block-status, SG_IO passthrough, copy-range via SCSI XCOPY, cache invalidation, reopen, truncate, and AioContext attach/detach.

## Main State

`IscsiLun` stores the driver instance state:
- libiscsi context,
- current AioContext,
- LUN number and SCSI device type,
- logical block size and block count,
- event masks and timers,
- mutex protecting libiscsi service/submission,
- logical block provisioning and block limit VPD data,
- saved device designator for XCOPY,
- zero block buffer for WRITE SAME,
- allocation bitmap/cache state,
- cluster size estimate,
- RW command width selection,
- write protection, provisioning, FUA, and WRITE SAME capability flags,
- request timeout/reconnect flag.

`IscsiTask` represents a coroutine-submitted SCSI command and carries status, retry state, returned `scsi_task`, coroutine pointer, error code/string, and retry timer.

On Linux, `IscsiAIOCB` supports asynchronous SG_IO passthrough and cancellation.

## Event Loop and Retry Model

libiscsi is integrated into QEMU's AioContext with fd handlers:
- `iscsi_set_events()` maps libiscsi's wanted `POLLIN`/`POLLOUT` events to QEMU fd handlers.
- `iscsi_process_read()` and `iscsi_process_write()` call `iscsi_service()` under the LUN mutex.
- `iscsi_timed_check_events()` periodically services timeout logic and triggers reconnect after timed-out requests.
- `iscsi_nop_timed_event()` sends NOP-Out probes and marks the connection for reconnect after too many in-flight NOPs.

`iscsi_co_generic_cb()` is the shared coroutine completion callback. It handles retryable statuses:
- `SCSI_STATUS_BUSY`,
- `SCSI_STATUS_TIMEOUT`,
- `SCSI_STATUS_TASK_SET_FULL`,
- check condition mapped to `EAGAIN`.

Retries use exponential random backoff based on `iscsi_retry_times`. Timeout status schedules retry after two event intervals and requests reconnect. The callback releases the LUN mutex before waking the coroutine to avoid direct wakeup deadlocks.

## Alignment and Sector Conversion

The driver converts between QEMU 512-byte sectors and target logical blocks with `sector_lun2qemu()` and `sector_qemu2lun()`. It rejects byte or sector requests not aligned to the target's logical block size. This is critical because SCSI READ/WRITE/UNMAP/WRITE SAME commands operate in LUN block units, not arbitrary bytes.

## Allocation Map and Sparse Zero Optimization

The driver maintains an optional allocation map when the target supports logical block provisioning and reports zeroes for unallocated blocks (`lbprz`). It uses:
- `allocmap`: whether a cluster is allocated,
- `allocmap_valid`: whether QEMU's knowledge is valid,
- `cluster_size`: guessed from optimal unmap granularity.

Reads can avoid network I/O when a valid cache entry says the range is unallocated and reads as zero. For larger reads over suspect unallocated areas, `iscsi_co_readv()` first calls `iscsi_co_block_status()` to query `GET LBA STATUS`; if the full request is zero, it fills the iovec locally.

Writes mark affected clusters allocated on success and invalid on failure. Discards and unmap-like zero writes invalidate or update the map depending on the command and flags. Reopen and cache invalidation reset allocation state.

## Read, Write, Flush

`iscsi_co_readv()` submits SCSI READ(10) or READ(16), using iov APIs when supported by the libiscsi version. It consults the allocation map first and zero-fills locally when safe.

`iscsi_co_writev()` submits SCSI WRITE(10) or WRITE(16), optionally with FUA if the target advertises DPOFUA. It validates max transfer assumptions, updates allocation map state, and reports libiscsi/SCSI errors through QEMU error reporting.

`iscsi_co_flush()` sends SYNCHRONIZE CACHE(10). The driver registers this as `.bdrv_co_flush_to_disk`.

## Block Status, Discard, and Zero Writes

`iscsi_co_block_status()` defaults to allocated data if logical block provisioning is absent or status query fails. When supported, it sends GET LBA STATUS and maps deallocated/anchored provisioning descriptors to non-data, and to `BDRV_BLOCK_ZERO` when the target has `lbprz`.

`iscsi_co_pdiscard()` implements UNMAP if `lbpu` is advertised. It silently tolerates check condition for target alignment dissatisfaction and invalidates the allocation map for the discarded range.

`iscsi_co_pwrite_zeroes()` implements WRITE SAME(10/16), optionally with UNMAP. It chooses WRITE SAME(16) when needed for unmap support or when normal RW uses 16-byte commands. If the target rejects WRITE SAME with invalid operation/code-field sense, the driver disables `has_write_same` and returns `-ENOTSUP`.

## SG_IO Passthrough on Linux

Under `__linux__`, the driver implements `.bdrv_aio_ioctl`:
- non-`SG_IO` requests emulate `SG_GET_VERSION_NUM` and `SG_GET_SCSI_ID`,
- `SG_IO` builds a libiscsi `scsi_task` from the user CDB,
- supports direct buffers or iovec transfer,
- maps check condition sense data back into `sg_io_hdr_t`,
- supports async cancellation with iSCSI task management abort.

This is important for non-disk/ROM SCSI device types, which are exposed as sg-compatible devices.

## Opening and Probing

`iscsi_parse_filename()` parses URLs of the form `iscsi://[user%password@]host[:port]/target/lun`, sets runtime QDict options, applies `-iscsi` defaults, and honors URL credentials if provided.

`iscsi_open()`:
- absorbs runtime options,
- validates transport/portal/target,
- creates libiscsi context using an initiator name from options, VM UUID, or VM name,
- initializes TCP/iSER transport,
- applies target name, CHAP, session type, header digest, and timeout,
- connects to the LUN,
- performs standard inquiry to determine device type,
- performs MODE SENSE for write protection and DPOFUA,
- applies auto-read-only if needed,
- reads capacity,
- marks non-disk/non-ROM devices as SG devices,
- probes supported VPD pages for logical block provisioning, block limits, and device identification,
- attaches AioContext handlers/timers,
- initializes allocation map if useful,
- sets supported zero/FUA flags.

`iscsi_close()` detaches the AioContext, logs out, destroys the libiscsi context, frees designator/zero/bitmap memory, destroys the mutex, and clears instance state.

## Limits and Reopen/Truncate

`iscsi_refresh_limits()` exports target-derived constraints:
- request alignment equals at least the LUN block size,
- max transfer derives from READ/WRITE(10/16) and block limits,
- discard maximum/alignment derives from UNMAP limits,
- write-zeroes maximum/alignment derives from WRITE SAME and provisioning limits,
- optimal transfer is rounded down to a power of two.

`iscsi_reopen_prepare()` refuses read-write reopen on write-protected LUNs. `iscsi_reopen_commit()` rebuilds the allocation map when cache.direct status changes.

`iscsi_co_truncate()` cannot actually resize iSCSI devices. It refreshes capacity and allows no-op/non-exact shrink-style checks, but rejects exact size changes and growth.

## Copy Range via XCOPY

The driver supports copy range between compatible iSCSI-backed nodes using SCSI EXTENDED COPY:
- both source and destination must be this driver's copy-range implementation,
- both LUNs need saved device designators,
- offsets and length must be aligned,
- block sizes must match,
- transfer length must fit XCOPY's 16-bit block count.

Helper functions build target descriptors, block-to-block segment descriptors, the parameter header, and the EXTENDED COPY task. `iscsi_co_copy_range_to()` submits the command to the destination LUN and traces the result.

## Driver Registration

The file registers `bdrv_iscsi` unconditionally when built with libiscsi. With libiscsi API support for transports, it also registers `bdrv_iser`. Both drivers expose the same operations and strong runtime options.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/iscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/linux-aio.c -->
# File Research: sources/virtualization/qemu/block/linux-aio.c

## Role

`block/linux-aio.c` implements QEMU's Linux native AIO backend using `libaio`. It provides coroutine submission for raw read/write/flush-like operations, batches pending requests, handles kernel completion events through an `eventfd`, resubmits short reads/writes, and integrates with QEMU's AioContext polling and bottom-half mechanisms.

## Core Structures

`qemu_laiocb` is the per-request state:
- submitting coroutine,
- `LinuxAioState`,
- kernel `struct iocb`,
- result,
- offset and byte count,
- original and resubmission iovecs,
- fd, request type, flags,
- device-specific max batch,
- queue linkage.

`LaioQueue` tracks pending and in-flight requests, queue blockage, and recursion depth.

`LinuxAioState` owns:
- QEMU AioContext,
- kernel `io_context_t`,
- event notifier,
- request queue,
- completion bottom half,
- nested completion iteration indices.

## Submission Queue

Requests enter through `laio_co_submit()`, which stack-allocates `qemu_laiocb`, calls `laio_do_submit()`, and yields until completion.

`laio_do_submit()` prepares the kernel iocb:
- `QEMU_AIO_WRITE`: `io_prep_pwritev2` with `RWF_DSYNC` for FUA when built with support, otherwise `io_prep_pwritev`.
- `QEMU_AIO_ZONE_APPEND`: `io_prep_pwritev`.
- `QEMU_AIO_READ`: `io_prep_preadv`.
- `QEMU_AIO_FLUSH`: `io_prep_fdsync`.

The iocb is tied to the backend eventfd with `io_set_eventfd()`, queued, and submitted immediately if batch thresholds are met. Otherwise `defer_call()` schedules deferred submission.

`ioq_submit()` submits batches up to `MAX_EVENTS` and the configured max batch. It handles:
- `-EAGAIN` by leaving the queue blocked,
- other submission errors by failing the first pending request,
- partial successful submission by splitting the pending queue,
- immediate completion processing when requests are in flight.

`IOQ_SUBMIT_MAX_DEPTH` caps recursive submit/completion cycles caused by synchronous completions and nested event loops.

## Completion Handling

The backend reads the kernel AIO ring directly through `io_getevents_peek()`, `io_getevents_commit()`, and `io_getevents_advance_and_peek()`. The comments note this copies Linux's AIO ring ABI and uses a read memory barrier paired with kernel completion ordering.

`qemu_laio_process_completions()` supports nested event loops by storing iteration indices in `LinuxAioState`, scheduling a completion BH before processing, and resetting indices once done.

`qemu_laio_process_completion()` converts kernel results:
- exact completion returns `0`,
- short read/write resubmits the remaining tail through `laio_resubmit_short_io()`,
- read EOF zero-fills the rest of the iovec,
- write zero-byte completion and zone-append short/nonfull completion become `-ENOSPC`,
- cancellation result `-ECANCELED` is preserved.

The coroutine is awakened unless it is already entered, avoiding recursive coroutine entry.

## AioContext Integration

`laio_attach_aio_context()` creates the completion BH and registers the event notifier with callback, poll, and poll-ready hooks. `laio_detach_aio_context()` removes the notifier and deletes the BH.

`qemu_laio_completion_cb()` processes completions when the eventfd fires. `qemu_laio_poll_cb()` lets QEMU poll readiness by peeking at the ring. `qemu_laio_poll_ready()` processes completions from polling paths.

## Initialization and Capability Checks

`laio_init()` allocates state, initializes the event notifier, creates the kernel AIO context with `MAX_EVENTS`, and initializes the queue. `laio_cleanup()` cleans up the event notifier, destroys the kernel AIO context, and frees state.

`laio_has_fdsync()` probes whether the host kernel accepts `IO_CMD_FDSYNC` by submitting a one-entry fdsync command to a temporary AIO context.

`laio_has_fua()` returns true only when built with `HAVE_IO_PREP_PWRITEV2`, because FUA is represented through `RWF_DSYNC`.

## Important Constraints

- Queue depth is capped at `MAX_EVENTS` per backend.
- Submissions may be batched globally by `aio_max_batch` and per-device by `dev_max_batch`.
- The code assumes access from the AioContext home thread; queue structures are not separately locked.
- FUA support depends on build-time availability of `io_prep_pwritev2`.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/linux-aio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/meson.build -->
# File Research: sources/virtualization/qemu/block/meson.build

## Role

`block/meson.build` declares the QEMU block subsystem source composition. It decides which block core files, image format drivers, protocol drivers, platform backends, optional modules, generated coroutine wrappers, and subdirectories are included in the build.

## Core Block Sources

The build always adds generated headers and the main block source set including files such as:
- block accounting, backend, copy, jobs, dirty bitmap, graph lock, throttling, mirroring, stream, snapshots,
- core I/O file `io.c`,
- qcow2 implementation files,
- raw format,
- NBD, null, quorum, preallocation, write threshold.

Compression dependencies `zstd` and `zlib` are attached to this core source set.

## Conditional Format and Feature Sources

The file gates optional image formats/features by Meson options:
- `qcow1` adds `qcow.c`,
- `vdi`, `vhdx`, `vmdk`, `vpc`, `cloop`, `bochs`, `vvfat`, `dmg`, `qed`, `parallels`,
- `replication`,
- TCG-only `blkreplay.c`.

Platform-specific local file backends are selected:
- Windows uses `file-win32.c` and `win32-aio.c`.
- Non-Windows uses `file-posix.c` plus `coref` and `iokit`.

Linux-only `nvme.c` is added when `host_os == 'linux'`.

## Optional Protocol/Backend Sources Relevant to This Group

This build file wires the other researched files as follows:
- `iscsi-opts.c` is added to `block_ss` when `libiscsi` is available.
- `iscsi.c` is part of the `block_modules` map when `libiscsi` is found.
- `linux-aio.c` is added when `libaio` is found.
- `io_uring.c` is added when `linux_io_uring` is found.

This means iSCSI driver code may be built as a block module depending on module settings, while the option registration file is part of the block source set when libiscsi exists.

## Module Construction

`block_modules` is a dictionary of optional block protocol modules. The file iterates over:
- blkio,
- curl,
- iscsi,
- nfs,
- ssh,
- rbd.

For each found dependency, it creates a source set and adds the module's source. If `enable_modules` is true, module sources are collected in `modsrc`.

DMG decompression helpers are treated as special block modules:
- `dmg-lzfse`,
- `dmg-bz2`.

## Generated Files

The build defines `module_block.h` using `scripts/modules/module_block.py`, with module source files as input. This generated header is added to `block_ss`.

It also defines `block-gen.c` using `scripts/block-coroutine-wrapper.py`, generated from block I/O headers and `coroutines.h`. This generated C file provides coroutine wrapper plumbing for declared block APIs and is added to the block source set.

## Subdirectories and Final Registration

The build adds `stream.c` after generated wrapper setup, adds `qapi-system.c` to `system_ss`, descends into `export` and `monitor`, and finally appends the `block_modules` dictionary into the global `modules` map under the key `block`.

## Build-System Significance

For this work item, `meson.build` is the linkage map showing how the core I/O layer (`io.c`), Linux async backends (`linux-aio.c`, `io_uring.c`), and iSCSI protocol support (`iscsi-opts.c`, `iscsi.c`) enter QEMU builds based on host platform and detected dependencies.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/meson.build -->