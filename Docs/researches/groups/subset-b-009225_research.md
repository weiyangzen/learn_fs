# subset-b-009225 Research

Grouped research report for the requested fio source files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/rados.c -->
# sources/test-tools/fio/engines/rados.c

## Purpose
`rados.c` implements fio's `rados` ioengine for benchmarking Ceph object storage through the low-level librados API. It is diskless from fio's perspective: fio file names become RADOS object names, object sizes are synthesized from job size and file count, and open/invalidate hooks are no-ops because the engine owns all storage access through a Ceph pool.

## Important APIs, Types, And Functions
The engine state is `struct rados_data`, holding the `rados_t` cluster handle, `rados_ioctx_t`, completion event array, pthread condition/mutex pair, completion list, and scheduled/completed counters. Per-I/O state is `struct fio_rados_iou`, attached to `io_u->engine_data`, with a completion handle and optional write op for TRIM. `struct rados_options` exposes `clustername`, `pool`, `clientname`, `conf`, `busy_poll`, and `touch_objects`.

`_fio_setup_rados_data()` allocates shared state and completion storage. `_fio_rados_connect()` creates the Ceph client, reads config, connects, opens the pool IO context, sizes fio files, and optionally touches objects. `_fio_rados_disconnect()` tears handles down. `fio_rados_queue()` submits `rados_aio_write`, `rados_aio_read`, or zeroing write-op TRIM requests. `complete_callback()` records completions into a protected list. `fio_rados_getevents()` drains completed `fio_rados_iou` nodes into `aio_events`.

## Control Flow
Fio calls `.setup`, which allocates `rados_data`, forces thread mode, connects to Ceph, creates/touches objects, and records synthetic file sizes. Each `io_u` receives a `fio_rados_iou` in `.io_u_init`. On `.queue`, the engine creates a librados completion, submits async operation by object name and offset, increments `ops_scheduled`, and returns `FIO_Q_QUEUED`. Librados invokes `complete_callback`, which appends the per-I/O node and signals waiters. `.getevents` waits until `min` events exist, releases librados completion/write-op resources, and returns event count; `.event` maps event indexes back to fio `io_u`s.

## State And Persistence
State is process-local except for Ceph objects. The engine creates/touches objects on connect and unconditionally removes all job objects during cleanup via `_fio_rados_rm_objects()`, so benchmark data is transient. Completion state is protected by `completed_lock`; `ops_scheduled` and `ops_completed` gate cleanup so resources are not destroyed before callbacks finish.

## Dependencies And Integration Points
This file depends on `librados`, pthreads, fio ioengine hooks, `flist`, fio logging/error helpers, and option grouping from `optgroup.h`. It registers a `FIO_DISKLESSIO` engine named `rados` using `register_ioengine()`.

## Risks
`busy_poll` is accepted but not used by `getevents`, which always waits on the condition variable when completions are absent. Cleanup removes every object named in the fio job, so accidental use against existing objects is destructive. `fio_rados_io_u_init()` does not check `calloc` failure before dereferencing. Error cleanup in `_fio_rados_connect()` can leave a created cluster handle if failure happens before `rados_create` succeeds. Timeouts passed to `getevents` are ignored.

## Test Signals
Useful tests include a missing pool/name config failure, read/write/TRIM submission against a test Ceph pool, cleanup waiting with in-flight callbacks, and ensuring object removal behavior is explicit. Unit-style tests can exercise option parsing and allocation-failure paths, but full confidence needs an integration Ceph cluster.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/rados.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/rbd.c -->
# sources/test-tools/fio/engines/rbd.c

## Purpose
`rbd.c` implements fio's `rbd` ioengine for benchmarking Ceph RADOS Block Device images through librbd. It turns a configured RBD image into a fio file-like target, discovers image size with `rbd_stat`, and submits async read/write/discard/flush operations through librbd completions.

## Important APIs, Types, And Functions
`struct fio_rbd_iou` is per-`io_u` state with the librbd completion and two completion flags. `struct rbd_data` stores Ceph cluster, pool IO context, RBD image handle, event arrays, optional poll eventfd, and connection state. `struct rbd_options` exposes cluster, image, pool, client, busy-poll, and optional encryption settings.

`_fio_setup_rbd_data()` allocates engine arrays. `_fio_rbd_connect()` opens the Ceph cluster, pool, image, configures cache behavior for direct I/O, optionally loads encryption, and optionally installs RBD poll notification. `_fio_rbd_finish_aiocb()` maps librbd completion return values into fio error/resid state. `rbd_iter_events()` polls completion state either through `rbd_poll_io_events()` plus eventfd or by scanning fio's in-flight `io_u`s and waiting oldest-first. `fio_rbd_queue()` submits `rbd_aio_read`, `rbd_aio_write`, `rbd_aio_discard`, or `rbd_aio_flush`.

## Control Flow
`.setup` allocates state, forces thread mode because librbd cannot cross fork boundaries, connects in the main context, gets image size, and creates a synthetic fio file if necessary. `.init` reconnects only if setup did not already leave `connected` true. Each I/O creates a librbd completion with `_fio_rbd_finish_aiocb` as callback, submits based on `ddir`, then returns queued. `.getevents` loops until at least `min` completions are discovered, optionally busy-spinning when `busy_poll` is enabled. `.event` returns entries from `aio_events`.

## State And Persistence
The RBD image is persistent; the engine does not create or delete images. It may alter client-side cache behavior and may load image encryption. Completion state is stored in each `fio_rbd_iou` and released when observed. `sort_events` is a temporary oldest-first wait list for non-poll mode.

## Dependencies And Integration Points
Dependencies include `librbd`, `librados`, optional `CONFIG_RBD_ENCRYPTION`, optional `CONFIG_RBD_POLL`, Linux `poll/eventfd`, and fio's ioengine lifecycle. The engine registers as `rbd` with fio's option group `FIO_OPT_G_RBD`.

## Risks
The non-poll path scans all in-flight `io_u`s and depends on callback-updated flags without explicit atomics, so portability depends on fio/librbd threading assumptions. Poll mode decrements the eventfd semaphore best-effort and logs but continues on read failure. Encryption options are accepted even when unsupported, but then fail connect. `fio_rbd_io_u_free()` does not release an outstanding completion if an I/O is freed unexpectedly; normal completion release happens in `fri_check_complete()`.

## Test Signals
Test coverage should include image open failures, encryption option rejection/loading, direct-I/O cache disable behavior, read/write/discard/flush completion, busy-poll versus blocking behavior, and poll-notification builds. Full tests require a Ceph cluster with an RBD image; allocation and option parsing can be unit-tested in isolation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/rbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/rdma.c -->
# sources/test-tools/fio/engines/rdma.c

## Purpose
`rdma.c` implements fio's `rdma` ioengine using RDMA CM and libibverbs. It supports memory semantics (`write`, `read`) and channel semantics (`send`, `recv`) over InfiniBand, RoCE, or iWARP. It models the writer as the client and the reader as the server, so jobs are unidirectional and diskless.

## Important APIs, Types, And Functions
`enum rdma_io_mode` defines protocol mode. `struct rdmaio_options` holds host, bind, port, and verb. `struct remote_u` and `struct rdma_info_blk` are control-message payloads for exchanging mode, depth, max block size, and remote memory keys/addresses. `struct rdma_io_u_data` stores per-`io_u` send/recv work requests and SGE. `struct rdmaio_data` owns CM IDs, event channel, PD, CQ, QP, registered control buffers, remote memory table, queued/flight/completed I/O arrays, and random selection state.

Key functions include `fio_rdmaio_setup_connect()` and `fio_rdmaio_setup_listen()` for CM setup, `fio_rdmaio_setup_qp()` for verbs resources, `fio_rdmaio_setup_control_msg_buffers()` for registered control messages, `fio_rdmaio_connect()`/`accept()` for handshakes, `fio_rdmaio_post_init()` for registering fio buffers, `fio_rdmaio_prep()` for per-I/O WR setup, `fio_rdmaio_commit()` for posting queued WRs, and `cq_event_handler()`/`fio_rdmaio_getevents()` for completions.

## Control Flow
`.setup` creates a synthetic file and allocates engine state. `.init` rejects mixed read/write and random workloads, parses legacy `host/port/proto` syntax, checks `RLIMIT_MEMLOCK`, creates RDMA CM resources, and either listens as a server for read jobs or resolves/connects as a client for write jobs. `.post_init` registers each fio buffer as an MR and populates the control message. `.open_file` completes the client/server handshake. `.queue` only stages `io_u`s; `.commit` posts sends or receives and moves accepted requests to the flight array. CQ completions move matching flight entries to the completed array, and `.event` pops them FIFO-style.

## State And Persistence
All state is volatile RDMA connection and memory-registration state. No file data is persisted by fio. For memory semantic tests, the server exports registered local buffers and the client chooses remote buffers randomly for RDMA read/write. Close sends a finish notification for memory semantics before disconnecting.

## Dependencies And Integration Points
The engine integrates with `rdma/rdma_cma.h`, libibverbs, fio buffer MR fields (`io_u->mr`), fio file/open lifecycle, and fio's queue/commit asynchronous model. Flags include `FIO_DISKLESSIO`, `FIO_UNIDIR`, `FIO_PIPEIO`, and `FIO_ASYNCIO_SETS_ISSUE_TIME`.

## Risks
Resource cleanup is incomplete: `fio_rdmaio_cleanup()` only frees `rdmaio_data`; many arrays/MRs/control MRs are not explicitly freed in the cleanup path. `get_next_channel_event()` does not ack unexpected events before returning, which may leak CM events. `fio_rdmaio_setup_listen()` uses `htonl(*o->bindname)` instead of parsing the bind address, which looks suspicious. CQ event accounting (`cq_event_num`) is delicate and can underflow/over-adjust. The engine relies on read/write role conventions that can surprise users.

## Test Signals
Meaningful validation requires paired client/server jobs over real RDMA hardware or software RDMA. Important cases are all four verbs, max block size negotiation failure, memlock limit failure, legacy filename parsing, disconnect/finish notification, and completion matching under iodepth. Static tests should inspect cleanup leaks and bind address handling.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/sg.c -->
# sources/test-tools/fio/engines/sg.c

## Purpose
`sg.c` implements fio's Linux SCSI generic ioengine. It builds SCSI CDBs for read, write, write-and-verify, write-same, verify, write-stream, unmap/TRIM, and sync-cache commands, then executes them through either block-device `SG_IO` ioctl or sg character-device read/write command queues.

## Important APIs, Types, And Functions
`struct sg_options` exposes high-priority polling, FUA flags, write mode, and stream ID. `struct sgio_cmd` stores a 16-byte CDB plus sense buffer per depth slot. `struct sgio_trim` batches multiple fio TRIM `io_u`s into one UNMAP command. `struct sgio_data` owns command storage, event array, pollfd array, saved fd flags, read buffer, block size, type-check state, and trim queues.

Core helpers are endian setters/getters, `sgio_hdr_init()`, `fio_sgio_rw_lba()`, `fio_sgio_prep()`, `fio_sgio_unmap_setup()`, `fio_sgio_doio()`, `fio_sgio_getevents()`, `fio_sgio_commit()`, `fio_sgio_read_capacity()`, `fio_sgio_type_check()`, stream open/close helpers, and `fio_sgio_errdetails()`.

## Control Flow
`.init` allocates per-depth command, event, sg header, and TRIM batching structures, then forces `override_sync`. `.open_file` uses `generic_open_file`, performs one-time type/block-size detection, and opens a stream when requested. `.prep` translates fio direction, offset, and transfer length into an SG header and CDB. `.queue` decides synchronous versus async operation based on direct/sync settings and direction. Block devices use `ioctl(SG_IO)` synchronously. Character devices use write/read of `sg_io_hdr`, asynchronously unless direct/sync/sync-command mode forces immediate readback. Async TRIM ranges are batched and submitted in `.commit`; `.getevents` polls sg fds and expands one UNMAP completion back to all batched fio `io_u`s.

## State And Persistence
The engine mutates target SCSI devices directly. Stream IDs may be opened and closed around a job. Async state is held in `trim_queues`, `events`, and sg driver queues. For block devices, `.type_check` disables `.getevents`, `.event`, and `.commit` because all I/O completes synchronously through ioctl.

## Dependencies And Integration Points
The implementation depends on Linux SG interfaces (`sg_io_hdr`, `SG_IO`, `SG_GET_VERSION_NUM`), block ioctls, fio raw I/O flags, generic file open/close, fio error-detail hooks, and fio's special accounting functions for engines that sometimes complete synchronously inside `.queue`.

## Risks
The engine has high device risk: malformed CDBs or wrong options can modify real SCSI media. Mixed `/dev/sdX` and `/dev/sgY` jobs are called out as problematic because type checking mutates global engine hooks after the first file. Async TRIM batching depends on `current_queue` and per-index maps; incorrect queue accounting would misattribute completions. `fio_sgio_getevents()` restores nonblocking flags only in the `min == 0` path. Error-detail strings are allocated and must be freed by the caller.

## Test Signals
Tests should cover block-device sync mode, sg-character async mode, all write modes' CDB bytes, 10-byte versus 16-byte LBA transitions, UNMAP batching, stream open/close, error-detail formatting from synthetic headers, and builds without `FIO_HAVE_SGIO`. Integration should run only against disposable SCSI targets or emulators.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/sg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/skeleton_external.c -->
# sources/test-tools/fio/engines/skeleton_external.c

## Purpose
`skeleton_external.c` is a sample external fio ioengine, intended to be compiled as a shared object and loaded through fio's external engine mechanism. It demonstrates the shape of an exported `struct ioengine_ops` without registering via `register_ioengine()`.

## Important APIs, Types, And Functions
`struct fio_skeleton_options` demonstrates engine-private options and includes a padding pointer because fio option offsets cannot be zero. The `options` array defines a dummy `FIO_OPT_STR_SET` option. Stub hooks include `fio_skeleton_init`, `prep`, `queue`, `getevents`, `event`, `cleanup`, `open`, `close`, and zoned block device helpers (`get_zoned_model`, `report_zones`, `reset_wp`, `get_max_open_zones`).

## Control Flow
The file does not perform real I/O. `fio_skeleton_queue()` runs `fio_ro_check()` and returns `FIO_Q_COMPLETED`. `open` and `close` delegate to generic file helpers. Zoned hooks report `ZBD_NONE` or success/no data. The exported `ioengine` symbol is meant to be found via `dlsym(..., "ioengine")`, which is the key difference from built-in engines.

## State And Persistence
No engine state is allocated or persisted. The dummy option toggles an integer in fio's per-engine option area but is otherwise unused.

## Dependencies And Integration Points
The sample depends on fio's public ioengine structures, generic file helpers, option parser structures, and ZBD types from included fio headers. It integrates by exporting `struct ioengine_ops ioengine` rather than constructor-style register/unregister functions.

## Risks
Because this is a skeleton, copying it unchanged creates an engine that silently completes I/O without transferring data. The comments are useful, but the async hooks return no events and would be invalid for a real queued engine without additional state. The sample also does not demonstrate allocation-failure handling or timeout behavior.

## Test Signals
Build it as a shared object with the documented compiler flags and confirm fio can load the `ioengine` symbol and parse `dummy`. Functional tests should be limited to verifying it is a template, not a real data-moving engine.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/skeleton_external.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/solarisaio.c -->
# sources/test-tools/fio/engines/solarisaio.c

## Purpose
`solarisaio.c` implements fio's native Solaris asynchronous I/O engine using `aioread`, `aiowrite`, and `aiowait` from `<sys/asynch.h>`.

## Important APIs, Types, And Functions
`struct solarisaio_data` contains an array of completed `io_u` pointers, a pending completion count, an in-flight count, and a maximum depth capped to `MAXASYNCHIO`. `fio_solarisaio_prep()` initializes `io_u->resultp` and attaches engine data. `wait_for_event()` calls `aiowait`, converts Solaris `aio_result_t` back to the enclosing `io_u`, sets residual/error state, stores it in the event array, and decrements in-flight count. Queueing uses `aioread`/`aiowrite`; sync directions use `fsync`/`fdatasync`.

## Control Flow
`.init` allocates state and caps depth to the OS limit. `.prep` marks each request in progress. `.queue` refuses sync operations while async requests are outstanding, refuses more async work once `nr == max_depth`, and submits reads or writes at `io_u->offset`. `.getevents` converts fio's timeout to `timeval`, repeatedly calls `wait_for_event()` until `min` completions are pending, then returns and clears the pending count. `.event` indexes the completion array.

## State And Persistence
State is per-thread and volatile. Data persists only through the target file descriptors opened by generic fio file handling. Optional `USE_SIGNAL_COMPLETIONS` installs a SIGIO handler that calls `wait_for_event(NULL)`.

## Dependencies And Integration Points
The engine depends on Solaris-specific async I/O APIs, generic fio file open/close/size hooks, fio barriers, and optional signal delivery. It registers a built-in engine named `solarisaio`.

## Risks
The pending-event counter is manipulated without a lock; comments assume integer operations are atomic, but signal-driven completion mode requires only a write barrier between event storage and count update. Timeout behavior is weak: if `min` is nonzero and no events arrive, `getevents` can repeatedly call `aiowait` with the same timeout. The signal handler calls nontrivial code, including logging/exit paths in error cases.

## Test Signals
Testing requires Solaris or compatible APIs. Useful cases are depth capping, read/write completion residuals, sync refusal while async I/O is in flight, timeout behavior, and signal-completion builds.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/solarisaio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/splice.c -->
# sources/test-tools/fio/engines/splice.c

## Purpose
`splice.c` implements fio's synchronous Linux splice/vmsplice ioengine. It measures data paths that move bytes through pipes using `splice(2)` and `vmsplice(2)` rather than ordinary `read`/`write`.

## Important APIs, Types, And Functions
`struct spliceio_data` owns a pipe and two feature flags: whether `vmsplice` to user memory is usable and whether the mmap-assisted path works. `fio_splice_read_old()` splices file data into a pipe and reads the pipe into the user buffer. `fio_splice_read()` uses `splice` into a pipe then `vmsplice` into the fio buffer, optionally via a temporary mapping. `fio_splice_write()` vmsplices the fio buffer into a pipe and splices to the file. `fio_spliceio_queue()` dispatches directions and maps return counts to fio completion state.

## Control Flow
`.init` allocates state, creates a pipe, and optimistically enables modern vmsplice paths. `.queue` handles reads, writes, TRIM, and sync directions synchronously. Read first tries the vmsplice-to-user path; if the kernel returns `EBADF`, it disables that capability and retries the old pipe-read path. Write waits for pipe writability, moves buffer pages into the pipe, then drains them to the file at the target offset. `.cleanup` closes pipe fds and frees state.

## State And Persistence
Engine state is limited to pipe descriptors and capability flags. Data persists in the underlying file for writes. The mmap-assisted read path temporarily maps over `io_u->xfer_buf` and unmaps before returning.

## Dependencies And Integration Points
The engine depends on Linux `splice`, `vmsplice`, `pipe`, `poll`, `mmap`, fio generic file helpers, `SPLICE_DEF_SIZE`, and synchronous engine accounting through `FIO_SYNCIO | FIO_PIPEIO`.

## Risks
Return-value sign handling is inconsistent: some helpers return `-errno`, but `fio_spliceio_queue()` sets `io_u->error = errno` rather than `-ret`, so stale `errno` could be reported. The mmap path maps at `io_u->xfer_buf`, which is unusual and can fail or interact badly with buffer ownership. Partial splice/vmsplice behavior needs careful residual handling. Unsupported filesystem/device paths surface as `EINVAL`.

## Test Signals
Tests should cover read fallback from vmsplice to old mode, write path through pipe, short transfers, TRIM/sync delegation, unsupported filesystem error messaging, and cleanup after pipe creation failure. Integration tests need Linux kernels/filesystems with splice support.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/sync.c -->
# sources/test-tools/fio/engines/sync.c

## Purpose
`sync.c` implements fio's synchronous POSIX file I/O engines: `sync`, `psync`, `vsync`, and conditionally `pvsync`/`pvsync2`. It covers sequential `read`/`write` with `lseek`, positioned `pread`/`pwrite`, vectorized `readv`/`writev`, and newer `preadv2`/`pwritev2` flags.

## Important APIs, Types, And Functions
`struct syncio_data` stores vector I/O arrays, queued `io_u`s, queued byte count, last offset/file/direction for coalescing, and a random state for probabilistic `RWF_HIPRI`. `fio_syncio_prep()` manages `lseek` for the `sync` engine using `fio_file->engine_pos`. `fio_io_end()` centralizes residual/error handling and last-position update. Queue functions implement `pvsync`, `pvsync2`, `psync`, and `sync`. The `vsync` path uses `fio_vsyncio_queue()`, `fio_vsyncio_commit()`, `getevents()`, and `event()` to batch contiguous operations into one vector call.

## Control Flow
Simple engines complete inside `.queue`: they perform read/write/TRIM/sync directly and return `FIO_Q_COMPLETED`. `sync` calls `.prep` first to seek if the requested offset differs from the cached file position. `vsync` queues only adjacent same-file/same-direction requests; non-appendable requests return `FIO_Q_BUSY` so fio commits the current vector and retries. `fio_vsyncio_commit()` marks submissions, seeks to the first offset, calls `readv` or `writev`, stores a completion count, clears the queue, and distributes residuals/errors across queued `io_u`s.

## State And Persistence
State is per-thread. File data persists through normal file descriptors. `fio_file->engine_pos` caches current position for the `sync` engine. `pvsync2` can set `RWF_HIPRI`, `RWF_DONTCACHE`, `RWF_NOWAIT`, and `RWF_ATOMIC` when supported/configured.

## Dependencies And Integration Points
The file uses POSIX `read`, `write`, `pread`, `pwrite`, `readv`, `writev`, optional `preadv2`/`pwritev2`, fio generic file helpers, trim/sync helpers, and fio ioengine registration. `FIO_SYNCFS` indicates syncfs integration, and `pvsync2` advertises `FIO_ATOMICWRITES`.

## Risks
`fio_vsyncio_init()` does not check allocation failures for `sd`, `iovecs`, or `io_us`. `fio_vsyncio_end()` casts remaining byte counts through unsigned `this_io`, so unusual partial/error returns should be reviewed carefully. `RWF_NOWAIT` and `RWF_DONTCACHE` behavior depends on kernel/filesystem support and may produce expected transient errors. Vector batching only works for exact adjacency, file, and direction matches.

## Test Signals
Tests should cover each registered engine, partial read/write residuals, seek caching, TRIM and sync direction delegation, vector coalescing and busy retry, pwritev2 flag combinations, `RWF_ATOMIC` when `oatomic` is set, and conditional build paths for `CONFIG_PWRITEV` and `FIO_HAVE_PWRITEV2`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/windowsaio.c -->
# sources/test-tools/fio/engines/windowsaio.c

## Purpose
`windowsaio.c` implements fio's Windows asynchronous I/O engine using overlapped I/O and I/O Completion Ports. It supports either a background completion thread or direct dequeueing in `getevents`.

## Important APIs, Types, And Functions
`struct fio_overlapped` wraps `OVERLAPPED`, the owning `io_u`, and a completion flag. `struct windowsaio_data` stores the completion event array, IOCP handle, optional completion thread handle, event handle, and thread-running flag. `struct windowsaio_options` exposes `no_completion_thread`.

Important functions include `fio_windowsaio_init()` for IOCP/event/thread creation, `fio_windowsaio_open_file()` for Windows handle creation and IOCP association, `fio_windowsaio_queue()` for `ReadFile`/`WriteFile`/`FlushFileBuffers`, `fio_windowsaio_getevents_nothread()` for `GetQueuedCompletionStatusEx`, `fio_windowaio_getevents_thread()` for scanning completion flags signaled by `IoCompletionRoutine()`, and per-`io_u` init/free wrappers.

## Control Flow
`.init` allocates engine data and creates an IOCP. Unless `no_completion_thread` is set, it launches `IoCompletionRoutine`, optionally applying fio CPU affinity. `.open_file` chooses flags from direct/sync/fadvise/create options, opens the file with `FILE_FLAG_OVERLAPPED`, optionally invalidates cache by opening non-buffered, and associates the handle with the IOCP. `.queue` fills the overlapped offset, submits read or write, treats `ERROR_IO_PENDING` as queued, and handles sync directions by flushing immediately. Completion is either consumed directly from the IOCP in `.getevents` or marked by the helper thread and later harvested by scanning in-flight `io_u`s.

## State And Persistence
State is per fio thread and uses Windows kernel handles. File data persists normally. Each `io_u` owns a persistent `fio_overlapped` object for reuse across submissions.

## Dependencies And Integration Points
The engine depends on Win32 APIs, fio's Windows file fields (`fio_file->hFile`), generic size lookup, `win_to_posix_error`, option parsing, and fio's async event hooks.

## Risks
`fio_windowsaio_cleanup()` always waits on and closes `wd->iothread`; in no-completion-thread mode that handle may be unset. The background thread and cleanup coordinate through a plain Boolean and 250 ms polling. Direct-dequeue mode uses `GetLastError()` after `GetQueuedCompletionStatusEx`, but per-entry errors are usually in the overlapped status. Manual TRIM is unsupported. Cache invalidation is best effort and depends on no other open handles.

## Test Signals
Windows integration tests should exercise threaded and no-thread modes, direct/sync/fadvise open flags, read/write completion residuals, flush directions, invalid path/open failures, cleanup in both modes, and async error conversion. Unit-level tests can validate timeout wrap logic in `timeout_expired()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/windowsaio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/xnvme.c -->
# sources/test-tools/fio/engines/xnvme.c

## Purpose
`xnvme.c` implements fio's `xnvme` ioengine using the xNVMe C API for NVMe devices, including backend selection, asynchronous queues, vectored I/O, metadata/protection information handling, zoned namespace operations, and FDP RUH fetching.

## Important APIs, Types, And Functions
`struct xnvme_fioe_fwrap` wraps each fio file with an xNVMe device, geometry, queue, LBA/metadata sizing, and fio file pointer. `struct xnvme_fioe_data` stores the completion queue, completion/error counters, round-robin file indexes, open/allocation counts, optional iovec arrays, and flexible file wrappers. `struct xnvme_fioe_request` stores per-I/O PI context and metadata buffer. Options select xNVMe backend/memory/async/sync/admin interfaces, namespace ID, subnqn, iovec mode, metadata size, and PI checks/tags.

Core paths include `xnvme_opts_from_fioe()`, `_dev_open()`, `_verify_options()`, `xnvme_fioe_init()`, xNVMe buffer allocation/free hooks, per-`io_u` init/free, `xnvme_fioe_queue()`, `cb_pool()`, `xnvme_fioe_getevents()`, and ZBD/FDP helpers.

## Control Flow
`.init` requires `--thread=1`, allocates `xnvme_fioe_data`, completion/iovec arrays, and opens every fio file under a global mutex because xNVMe setup is serialized. `_dev_open()` opens the device, initializes an async queue, captures geometry, adjusts LBA/metadata sizes for PI action, validates fio block sizes/verify compatibility, and marks file size known. `.queue` computes SLBA/NLB, gets an xNVMe command context, populates NVMe read/write command fields, optionally generates PI metadata for writes, uses scalar or vectored `xnvme_cmd_pass*`, and returns queued/busy/completed. `cb_pool()` verifies completions and PI on reads, appends `io_u` to `iocq`, and releases the context. `.getevents` round-robins device queues with `xnvme_queue_poke()` until `min` completions are available.

## State And Persistence
Device handles and queues are per thread but protected during open/close and pre-init helper operations by `g_serialize`. Data persists on NVMe targets. Metadata buffers are allocated per `io_u` when requested. Zoned helper calls sometimes open temporary devices before engine initialization and sometimes reuse initialized wrappers.

## Dependencies And Integration Points
Dependencies include `libxnvme`, fio verify, ZBD types, data placement/FDP types, pthreads, and fio raw/diskless/memalign flags. The engine registers `xnvme` with hooks for memory allocation, eventing, file size, ZBD model/report/reset, max open zones, and FDP RUHS.

## Risks
Several error paths assert false after runtime I/O failures, which is harsh for production benchmarking. `_dev_close()` calls `xnvme_queue_term()` when `dev` is set but does not separately check `queue`. `_dev_open()` compares `f->fileno > nallocated` rather than `>=`, which should be reviewed. `getevents` can spin indefinitely if completions never arrive and timeout is ignored. PI/metadata validation is complex and tied to geometry; block-size and verify combinations need careful testing.

## Test Signals
Tests should cover backend option construction, block-size validation, PI action/check combinations, vectored and non-vectored I/O, metadata buffers, busy queue handling, multi-file queue polling, zoned model/report/reset conversion, max-open-zone overflow behavior, FDP RUH fetch, and cleanup after partial init failure. Real validation requires xNVMe-capable devices or emulation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/xnvme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/err.h -->
# sources/test-tools/fio/err.h

## Purpose
`err.h` provides Linux-kernel-style pointer/error helpers for returning either a valid pointer or a small negative errno encoded in a pointer-sized value.

## Important APIs, Types, And Functions
`MAX_ERRNO` is `4095`, matching the conventional maximum errno range. `IS_ERR_VALUE(x)` tests whether an unsigned pointer-sized value falls in the high address range reserved for encoded negative errors. `ERR_PTR(error)` casts an integer error to `void *`. `PTR_ERR(ptr)` casts a pointer back to an integer. `IS_ERR(ptr)` and `IS_ERR_OR_NULL(ptr)` test encoded error pointers, and `PTR_ERR_OR_ZERO(ptr)` returns the encoded error or zero.

## Control Flow
The header is all inline/macro logic. Callers create an encoded error with `ERR_PTR(-EINVAL)`-style values, propagate it through pointer-returning APIs, then test with `IS_ERR` before dereferencing.

## State And Persistence
No state is stored. Behavior depends entirely on pointer representation and the assumption that valid pointers do not occupy the reserved top `MAX_ERRNO` range.

## Dependencies And Integration Points
The code uses `uintptr_t`; including translation units must already have the needed integer type definitions. It integrates with fio code that mirrors Linux kernel pointer-error idioms.

## Risks
This pattern is architecture-sensitive. It is safe only if callers consistently pass negative errno values and never dereference before checking. `PTR_ERR_OR_ZERO()` returns `int` but `PTR_ERR()` returns `uintptr_t`; callers should avoid losing information or sign semantics accidentally.

## Test Signals
Simple unit tests can check that `ERR_PTR((uintptr_t)-EINVAL)` is detected, NULL is handled by `IS_ERR_OR_NULL`, normal heap pointers are not errors, and `PTR_ERR_OR_ZERO()` returns zero for normal pointers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/eta.c -->
# sources/test-tools/fio/eta.c

## Purpose
`eta.c` calculates and displays fio's live job status line: thread state map, percent complete, bandwidth, IOPS, rate limits, open file count, and ETA. It also exposes packed ETA data through `get_jobs_eta()`.

## Important APIs, Types, And Functions
Global buffers `__run_str` and `run_str` store raw and condensed thread states. `check_str_update()` maps `thread_data->runstate` and workload type to status characters. `eta_to_str()` formats seconds as day/hour/min/sec. `thread_eta()` estimates remaining seconds per job using total bytes, completed bytes, time-based limits, verify expansion, zone skip adjustments, ramp/start delay, fill-device sizing, and rate limits. `calc_rate()` and `calc_iops()` compute interval deltas. `calc_thread_status()` aggregates all jobs into `struct jobs_eta`. `display_thread_status()` renders the status line. `get_jobs_eta()`, `print_thread_status()`, and `print_status_init()` are external entry points.

## Control Flow
Status printing starts with `print_thread_status()`, which calls `get_jobs_eta(false)`. That allocates `jobs_eta`, calls `calc_thread_status()`, and sizes the result to the condensed run string. `calc_thread_status()` may skip work depending on output mode, stall state, TTY status, and ETA policy, unless forced. It walks all fio threads, updates counts/rate-limit sums/open files, computes per-thread ETA after an initial grace period, updates run-state characters, aggregates bytes/IOPS, periodically logs aggregate bandwidth samples, and calculates display-rate deltas. `display_thread_status()` builds a single carriage-return status line, pads over previous longer lines, and occasionally schedules a newline.

## State And Persistence
The file keeps static counters and timestamps for rate intervals and display formatting. It reads global fio state such as `thread_number`, `done_secs`, `eta_interval_msec`, output flags, aggregate log state, and all `thread_data` records. No durable state is persisted; output goes to stdout and aggregate logs through fio logging helpers.

## Dependencies And Integration Points
Dependencies include fio core globals/macros, time helpers, number formatting, aggregate logging, Valgrind DRD annotations, and power-of-two helpers. `struct jobs_eta` is part of fio's status/reporting interface and is compile-time checked against its packed form.

## Risks
ETA is heuristic and depends on many options; zone skip, verify, fill-device, stonewall, ramp, and time-based interactions are easy to regress. Several static arrays are global and not independently synchronized; DRD annotations only suppress one known variable. `calc_thread_status()` returns early after updating some static timing paths, so logging/display cadence is subtle.

## Test Signals
Tests should cover `eta_to_str`, condensed run string generation, runstate character mapping, time-based ETA, verify doubling/mixed write adjustment, zone skip adjustment, stonewall ETA accumulation, unified mixed reporting, TTY/ETA skip rules, aggregate bandwidth sample cadence, and packed `jobs_eta` sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/eta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/exp/expression-parser.l -->
# sources/test-tools/fio/exp/expression-parser.l

## Purpose
`expression-parser.l` is the flex lexer for fio arithmetic expressions used by the experimental expression parser. It tokenizes numeric values, arithmetic operators, comments, whitespace, and fio-style unit suffixes.

## Important APIs, Types, And Functions
The lexer includes `y.tab.h`, defines `YYSTYPE` as `PARSER_VALUE_TYPE`, and overrides `YY_INPUT` to read from parser-provided `lexer_input()`. It exports global `lexer_value_is_time`, which decides whether suffix `m` means mebibytes or minutes. The `set_suffix_value` macro fills both integer and double values plus flags in `yylval`.

Rules recognize binary and decimal byte suffixes, time suffixes (`us`, `ms`, `s`, `m`, `h`, `d`), floating/scientific numbers, hex numbers, integers, arithmetic operators, newlines, and invalid characters. Comments and everything after `#`, `:`, or `,` are ignored.

## Control Flow
Flex scans the current expression string supplied by `lexer_input`. Suffix tokens return `SUFFIX` with multiplier metadata. Number tokens parse via `sscanf` and return `NUMBER`, setting `has_dval` when fractional/scientific syntax is used. Operators return their character code directly for yacc precedence handling. Newline returns 0 to end parsing.

## State And Persistence
The lexer is not thread-safe: it uses global `lexer_value_is_time` and yacc/flex globals. It stores no durable state.

## Dependencies And Integration Points
It depends on the yacc grammar's `PARSER_VALUE_TYPE`, `NUMBER` and `SUFFIX` tokens, `yyerror`, and parser-supplied input. It is paired with `expression-parser.y`.

## Risks
Some suffix values look suspicious: `[tT]` multiplies the integer by 1 TiB but the double by 1024^5, while `[pP]` uses the same integer expression as T but a larger double. Decimal IEC-looking suffixes such as `KiB` map to 1000 rather than 1024, which may be intentional or inverted naming. Integer parsing uses `int`, so large bare integers/hex values can overflow before being stored as `long long`.

## Test Signals
Lexer tests should cover every suffix in both time and non-time modes, fractional/scientific numbers, hex values, comments after separators, invalid characters, large numeric overflow behavior, and operator tokenization.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/exp/expression-parser.l -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/exp/expression-parser.y -->
# sources/test-tools/fio/exp/expression-parser.y

## Purpose
`expression-parser.y` is the yacc grammar and evaluator for fio arithmetic expressions. It computes both integer and double results, tracks parse/value errors, and applies implied units when no explicit suffix appears.

## Important APIs, Types, And Functions
`struct parser_value_type` carries `dval`, `ival`, `has_dval`, and `has_error`; it is exposed as `PARSER_VALUE_TYPE`/`YYSTYPE`. Grammar tokens are `NUMBER`, `BYE` (unused), and `SUFFIX`. Operators include `+`, `-`, `*`, `/`, `%`, `^`, unary minus, parentheses, and suffix multiplication. Runtime support includes `lexer_input()`, `setup_to_parse_string()`, `evaluate_arithmetic_expression()`, and `yyerror()`.

## Control Flow
`evaluate_arithmetic_expression()` sets the lexer time-mode global, copies the input into a fixed double-null-terminated buffer, calls `yyparse`, restarts the lexer, and returns an error flag. The grammar reduces expressions by computing integer math when both operands are integral and double math otherwise. Suffix reduction multiplies the previous expression and sets `units_specified`. Division and modulo check for zero and flag errors through `yyerror`, while exponentiation handles integer positive powers directly and otherwise delegates to `pow()`. If no suffix was specified, the final value is multiplied by `implied_units`.

## State And Persistence
Parsing uses static `lexer_read_offset` and `lexer_input_buffer[1000]`, so it is explicitly not thread-safe. Inputs longer than the buffer are truncated. No persistent state is written.

## Dependencies And Integration Points
The grammar depends on the flex lexer, C math library `pow`, and generated yacc interfaces. It is called by the test program and likely by fio option parsing code that wants arithmetic in numeric options.

## Risks
Error handling is intentionally quiet: `yyerror()` does nothing, and some divide-by-zero reductions do not explicitly set `$$.has_error` beyond operand flags. Fixed buffer truncation can convert invalid long expressions into valid prefixes. Integer overflow is unchecked in arithmetic and suffix multiplication. Thread-unsafety is documented and material if expression evaluation is used concurrently.

## Test Signals
Tests should cover precedence/associativity, unary minus, suffix multiplication, implied units, time/non-time `m`, division/modulo by zero, exponent edge cases such as `0^0` and negative exponents, long input truncation, and integer overflow boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/exp/expression-parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/exp/test-expression-parser.c -->
# sources/test-tools/fio/exp/test-expression-parser.c

## Purpose
`test-expression-parser.c` is an interactive command-line harness for the experimental arithmetic expression parser. It reads expressions from stdin, evaluates them, and prints integer and double results.

## Important APIs, Types, And Functions
The program includes generated `y.tab.h` and declares `evaluate_arithmetic_expression()`. `main()` owns a fixed 100-byte input buffer, calls `fgets`, strips a trailing newline, invokes the evaluator with implied units `1.0` and non-time mode, and prints either `"%lld (%20.20lf)"` or `Syntax error`.

## Control Flow
The loop continues until `fgets` returns NULL. The `bye` variable is initialized to zero and never changed, so EOF is the only exit. On parse success, both integer and double results are displayed; on parse failure, the local result variables are reset.

## State And Persistence
No persistent state exists. The parser itself uses static lexer/parser state in the generated files.

## Dependencies And Integration Points
This file depends on the expression parser build products and C stdio/string APIs. It is a developer/test utility rather than a fio runtime component.

## Risks
Input is limited to 89 characters plus terminator by `fgets(buffer, 90, stdin)`, which may split longer expressions across iterations. The unused `bye` variable suggests an abandoned command feature. The harness always uses non-time mode and implied units of 1.0, so it does not exercise all evaluator modes.

## Test Signals
Use it for smoke testing arithmetic, suffixes, and syntax errors. Automated tests should feed representative expressions over stdin and compare stdout/stderr. Additional harness coverage would be needed for `is_time=1` and non-1 implied units.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/exp/test-expression-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fifo.c -->
# sources/test-tools/fio/fifo.c

## Purpose
`fifo.c` implements a small circular byte FIFO used by fio internals. It is derived from a kernel-style FIFO implementation and provides allocation, free, put, and get operations.

## Important APIs, Types, And Functions
`fifo_alloc(size)` allocates `struct fifo` plus a byte buffer and initializes `in`/`out` counters. `fifo_free()` releases both. `fifo_put()` writes up to available room, splitting the copy at the physical end of the ring. `fifo_get()` reads or discards up to available bytes, also handling wraparound, then resets both counters to zero when empty.

## Control Flow
Put computes `len = min(requested, fifo_room(fifo))`, copies the first segment to `buffer + (in & (size - 1))`, copies any wrapped remainder to the start of the buffer, and advances `in`. Get computes available length from `in - out`, optionally copies out the first and wrapped segments, advances `out`, and normalizes empty state.

## State And Persistence
State is the allocated buffer and monotonically increasing `in`/`out` counters. Data is volatile and not thread-safe. Empty normalization prevents unbounded counter growth across repeated full drains.

## Dependencies And Integration Points
The code depends on `fifo.h` and `minmax.h`. It assumes the FIFO size is a power of two because it uses `index & (size - 1)` rather than `% size`.

## Risks
`fifo_alloc()` does not check the second `malloc`; if buffer allocation fails, later use or `fifo_free()` can misbehave. No validation enforces power-of-two size. Pointer arithmetic on `void *buffer`/`void *buf` is a GNU C extension, not portable ISO C. There is no locking.

## Test Signals
Unit tests should cover power-of-two sizes, wraparound put/get, partial put when full, discard get with NULL buffer, empty counter reset, non-power-of-two misuse, and buffer allocation failure handling.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/fifo.h -->
# sources/test-tools/fio/fifo.h

## Purpose
`fifo.h` declares fio's circular byte FIFO interface and its small inline helpers.

## Important APIs, Types, And Functions
`struct fifo` contains `unsigned char *buffer`, `size`, `in`, and `out`. Public functions are `fifo_alloc`, `fifo_put`, `fifo_get`, and `fifo_free`. `fifo_len()` returns `in - out`, and `fifo_room()` returns `size - in + out`.

## Control Flow
The header supplies only declarations and inline arithmetic. Implementation in `fifo.c` updates `in` and `out`; callers use the inline helpers to check occupancy and capacity.

## State And Persistence
The struct stores volatile in-memory FIFO state. It has no ownership metadata beyond the buffer pointer and no synchronization fields.

## Dependencies And Integration Points
This header is self-contained for the struct and API declarations. Consumers must link with `fifo.c` and obey the implementation's power-of-two size assumption.

## Risks
The API accepts unsigned `size` without documenting or enforcing power-of-two requirements in the header. `fifo_room()` relies on `in >= out` monotonic behavior and unsigned arithmetic. There is no const-correctness for `fifo_put` input buffers.

## Test Signals
Header-level tests should compile multiple consumers, verify inline length/room arithmetic after representative operations, and document expected behavior for empty/full states.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/file.h -->
# sources/test-tools/fio/file.h

## Purpose
`file.h` defines fio's central file abstraction, file-related enums, flags, inline flag accessors, mount metadata, and file lifecycle function declarations. It is the contract between fio core, file setup, and ioengines.

## Important APIs, Types, And Functions
`enum fio_filetype` distinguishes regular files, block devices, character devices, pipes, and directories. `enum fio_file_flags` tracks open/closing/extend/done/size-known/hash/partial-mmap/random-map allocation state. `enum file_lock_mode`, file service selection constants, and `enum fio_fallocate_mode` define policy values used by options.

`struct fio_file` contains hash linkage, file type, descriptors/Windows handles, identity, size and offset fields, FDP/ZBD/SP-random metadata pointers, per-direction position history, first/last write ranges, engine-private `engine_pos` and `engine_data`, synchronization lock union, random map union, nonuniform distribution state, references, flags, and disk-util pointer. `FILE_FLAG_FNS` generates inline set/clear/test functions for each flag. Function declarations cover setup, open/close/size, invalidation, pre-read, add/get/put, locking, directory expansion, random maps, duplication, reset, direct I/O, and filesystem sync integration.

## Control Flow
This header has no runtime flow beyond inline flag mutation. Runtime control is implemented by file setup and ioengine code that fills `fio_file`, opens descriptors, tracks sizes, and calls generic helpers or engine-specific hooks.

## State And Persistence
`fio_file` is long-lived job state. Some fields mirror persistent target properties (`real_file_size`, device IDs), while others are transient scheduling/accounting state. `engine_data` and `engine_pos` are intentionally reserved for ioengines.

## Dependencies And Integration Points
The header depends on fio compiler annotations, data direction types, intrusive lists, random distribution libraries, axmap, LFSR, and optional `CONFIG_SYNCFS`. Nearly every ioengine in this subset uses `fio_file` descriptors, file names, file sizes, `engine_pos`, or `engine_data`.

## Risks
Because `fio_file` is shared across many subsystems, flag misuse can create cross-module bugs. The union fields require callers to know which mode owns them. Engine-private fields can conflict if layered functionality assumes ownership. Reference and lock lifetimes must match file setup/teardown exactly.

## Test Signals
Tests should validate flag helpers, generic open/close/size implementations, add/get/put reference behavior, lock/unlock integration, random-map initialization, ZBD/FDP metadata lifetimes, and ioengine use of `engine_data`/`engine_pos`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/filehash.c -->
# sources/test-tools/fio/filehash.c

## Purpose
`filehash.c` maintains a global hash table of fio files by filename and a bloom filter for quick existence-style checks. It prevents duplicate file entries from being added silently and gives callers lookup/removal helpers.

## Important APIs, Types, And Functions
The hash table has 512 buckets (`HASH_BUCKETS`) indexed by Jenkins hash masked with `HASH_MASK`. Global state includes `file_hash`, `hash_lock`, and `file_bloom`. Public APIs are `file_hash_init`, `file_hash_exit`, `lookup_file_hash`, `add_file_hash`, `remove_file_hash`, explicit lock/unlock helpers, and `file_bloom_exists`.

## Control Flow
`file_hash_init()` allocates buckets with `smalloc`, initializes each list, creates a semaphore, and allocates the bloom filter. `add_file_hash()` initializes the file's hash link, locks the table, searches for an existing filename, and either returns the alias or inserts the file and sets its `hashed` flag. `lookup_file_hash()` locks around a bucket scan. `remove_file_hash()` deletes the entry if its flag says it is hashed. `file_hash_exit()` checks for remaining entries, frees table/semaphore/bloom, and clears globals.

## State And Persistence
The table and bloom filter are process-global volatile state. The bloom filter may retain names until exit and can produce false positives. Each `fio_file` records membership through `FIO_FILE_hashed` and `hash_list`.

## Dependencies And Integration Points
The implementation depends on fio lists, semaphores, Jenkins hash, smalloc, bloom filter code, logging, and `fio_file` flag helpers from `file.h`.

## Risks
`file_hash_init()` does not check allocation failures for the hash table, semaphore, or bloom filter before use. `file_bloom_exists()` assumes `file_bloom` is initialized. The bloom filter cannot remove names. `file_hash_exit()` only logs if entries remain, then frees the table anyway, so leaked file membership is diagnostic rather than fatal.

## Test Signals
Unit tests should cover insert, duplicate alias return, lookup, removal, idempotent removal of unhashed files, bloom set/query behavior, lock/unlock helpers before/after init, and exit with non-empty hash diagnostic.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/filehash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/filehash.h -->
# sources/test-tools/fio/filehash.h

## Purpose
`filehash.h` declares the global fio file hash and bloom filter interface.

## Important APIs, Types, And Functions
The header exposes initialization/exit, filename lookup, add/remove, explicit hash lock/unlock, and `file_bloom_exists(const char *, bool)`. It forward-depends on `struct fio_file` being visible to consumers that use pointer-returning APIs and includes `lib/types.h` for `bool`.

## Control Flow
The header has no logic. Consumers initialize the subsystem, then use lookup/add/remove under internal locking or wrap batches with explicit lock helpers.

## State And Persistence
State is owned by `filehash.c`, not the header. Bloom state is process lifetime and approximate.

## Dependencies And Integration Points
This header is included by file setup code and any component that needs filename deduplication. It integrates with `fio_file` hash flags and list linkage.

## Risks
The API does not document ownership or whether callers may call functions before init/after exit. Explicit lock helpers expose internal synchronization and can deadlock if callers mix them incorrectly with functions that also lock.

## Test Signals
Compile tests should include this header from C and C++ contexts where `struct fio_file` is forward-declared. Behavioral tests belong to `filehash.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/filehash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/filelock.c -->
# sources/test-tools/fio/filelock.c

## Purpose
`filelock.c` implements simple process-local exclusive locks keyed by filename hash. It lets fio coordinate access to the same file among job threads without using OS file locks.

## Important APIs, Types, And Functions
`struct fio_filelock` holds a filename hash, a semaphore used as the per-file lock, list linkage, and reference count. Global `struct filelock_data` owns an active list, global semaphore, free list, and fixed pool of `MAX_FILELOCKS` lock objects. Public APIs are `fio_filelock_init`, `fio_filelock_exit`, `fio_lock_file`, `fio_trylock_file`, and `fio_unlock_file`.

## Control Flow
Initialization allocates the global pool, initializes global/per-lock semaphores, and puts all locks on the free list. `__fio_lock_file()` hashes the filename, finds or allocates a lock object under the global lock, increments references, then either blocks on the per-file semaphore or attempts trylock-specific race handling. `fio_unlock_file()` hashes again, finds the active lock, decrements references, releases the per-file semaphore, and returns the object to the free list when references reach zero. Blocking allocation waits by dropping the global lock, sleeping, and retrying when the fixed pool is exhausted.

## State And Persistence
All state is process-local and stored in the fixed smalloc pool. Locks are keyed only by 32-bit hash, not full filename strings, so collisions alias. No OS-level persistence exists.

## Dependencies And Integration Points
The code depends on fio intrusive lists, semaphores, `smalloc`, Jenkins hash, logging, and `lib/types.h` via the header. File setup/locking code uses this as a shared synchronization primitive.

## Risks
Hash collisions can serialize unrelated files or incorrectly make trylock fail. The trylock path returns `true` when no free lock object is available, which semantically means "could not lock" but can be easy to misread. `fio_filelock_exit()` asserts the active list is empty, so teardown with leaked locks aborts in assert builds. The fixed `MAX_FILELOCKS` pool can throttle large jobs.

## Test Signals
Tests should cover blocking lock/unlock, trylock success/failure, reference counts with multiple lockers, pool exhaustion behavior, hash collision behavior via injected hashes if possible, and exit assertions/cleanup after all locks are released.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/filelock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/filelock.h -->
# sources/test-tools/fio/filelock.h

## Purpose
`filelock.h` declares fio's filename-based in-process locking API.

## Important APIs, Types, And Functions
The header exposes `fio_lock_file(const char *)`, `fio_trylock_file(const char *)`, `fio_unlock_file(const char *)`, `fio_filelock_init()`, and `fio_filelock_exit()`. It includes `lib/types.h` for `bool`.

## Control Flow
The API requires initialization before use and exit after all locks are released. `fio_lock_file` blocks until the filename lock is acquired. `fio_trylock_file` returns a Boolean indicating trylock failure/success according to the implementation's convention; callers must verify the expected polarity in `filelock.c`. `fio_unlock_file` releases by filename.

## State And Persistence
State is hidden in `filelock.c`; the header exposes no structs. Locks are process-local and non-persistent.

## Dependencies And Integration Points
The API is used by fio file setup and job coordination code that needs cooperative in-process exclusion without kernel file locks.

## Risks
The header does not document the return polarity of `fio_trylock_file`, which is non-obvious from the name alone. It also does not state that matching unlocks are mandatory before `fio_filelock_exit()`.

## Test Signals
Header-level validation is mainly compile coverage. Behavioral tests should exercise the implementation through this public API and document trylock return semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/filelock.h -->
