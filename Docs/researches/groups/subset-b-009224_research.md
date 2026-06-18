# subset-b-009224 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/io_uring.c -->
# sources/test-tools/fio/engines/io_uring.c

## Purpose
Implements fio's Linux `io_uring` engines: `io_uring` for normal read/write/sync/trim SQEs and `io_uring_cmd` for NVMe passthrough commands. It is the high-performance async path for block/file workloads and the integration point for NVMe protection information, zoned namespace helpers, FDP reclaim-unit-handle queries, mixed NVMe write modes, registered files, fixed buffers, SQ polling, and command priority.

## Important APIs, Types, And Functions
Core state lives in `struct ioring_data`, which owns the ring fd, mapped SQ/CQ rings, SQEs, iovec/fixed-buffer tables, per-`io_u` index table, optional metadata buffers, command-priority state, NVMe DSM buffers, and `nvme_cmd_ext_io_opts`. `struct ioring_options` exposes engine options including `hipri`, `fixedbufs`, `registerfiles`, `sqthread_poll`, `nowait`, `force_async`, `md_per_io_size`, PI tag/check settings, `readfua`, `writefua`, `write_mode`, `verify_mode`, and `cmd_type`.

Important functions are `fio_ioring_init()`, `fio_ioring_post_init()`, `fio_ioring_queue_init()`, `fio_ioring_mmap()`, `fio_ioring_prep()`, `fio_ioring_cmd_prep()`, `fio_ioring_queue()`, `fio_ioring_commit()`, `fio_ioring_getevents()`, `fio_ioring_event()`, and `fio_ioring_cmd_event()`. File and NVMe setup are handled by `fio_ioring_open_file()`, `fio_ioring_cmd_open_file()`, `fio_ioring_open_nvme()`, `fio_ioring_cmd_get_file_size()`, and PI helpers such as `fio_get_pi_info()`.

## Control Flow
Initialization allocates per-thread state, rounds internal ring depth to a power of two, configures metadata/PI buffers, initializes command priority, allocates NVMe DSM ranges, and configures io_uring features. `post_init` attaches all `io_u` objects to iovecs, creates the ring with feature fallback for newer setup flags, optionally registers buffers and files, probes for non-vectored opcode support, and mmaps SQ/CQ state.

For normal `io_uring`, `prep` fills an SQE for read/write, fsync/sync-file-range, or discard via `IORING_OP_URING_CMD`. For `io_uring_cmd`, `prep` builds NVMe command structures through `fio_nvme_uring_cmd_prep()`, optionally converts verification reads to compare commands, and randomly selects a write opcode for mixed `write_mode` ratios. `queue` stores the SQE index in the SQ ring, applies command priority and PI generation, and has a special busy path that prevents fsynced verification flushes from racing in-flight NVMe writes. `commit` submits queued SQEs with `io_uring_enter()` or wakes SQPOLL. Completion reaping advances CQ heads, maps CQEs back to `io_u`, and translates short/error/device-specific status.

## State And Persistence
State is per fio thread except for the global `enter_flags`, which is augmented if the kernel advertises `IORING_FEAT_NO_IOWAIT`. Registered files keep `fio_file->fd` logically closed while storing real descriptors in `ld->fds`. File engine data stores NVMe namespace/metadata information. Persistent media state can be changed by write, DSM/trim, write zeroes, write uncorrectable, flush, and zoned reset/finish/move operations.

## Dependencies And Integration Points
Depends on Linux io_uring syscalls/UAPI, fio core `ioengine_ops`, `cmdprio`, `verify`, `zbd`, block-zoned helpers, and local NVMe helpers from `nvme.c/.h`. The normal engine delegates zoned operations to `blkzoned_*`; the command engine delegates to `fio_nvme_*`. It integrates with fio buffer registration, file registration, command priority, verify modes, FDP, atomic writes, and error-detail reporting.

## Risks
Ring memory is manually mapped and indexed; `io_uring_cmd` doubles SQE/CQE slot addressing and must keep index math exact. CQ head is advanced before CQE data is consumed, relying on queue-depth sizing. `enter_flags` is process-global, so feature discovery affects later threads. Metadata/PI paths require strict alignment and block-size validation. NVMe FUA and fsynced verification are explicitly incompatible. Async trim fallback depends on `async_trim_fail`; zbd trim is marked synchronous for command engine. Kernel feature fallback paths should be tested on old and new kernels.

## Test Signals
Useful tests include normal read/write with vectored and non-vectored paths, fixed buffers, registered files, SQPOLL, `nowait`, `uncached`, command priority, sync and trim fallback, `io_uring_cmd` NVMe read/write/compare/write-zeroes/write-uncor mixes, FUA options, PI generation/verification with 16-byte and 64-byte guards, invalid metadata/block-size combinations, zoned namespace report/reset/finish/move, FDP RUH fetch, and kernel feature fallback for setup flags.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/io_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libaio.c -->
# sources/test-tools/fio/engines/libaio.c

## Purpose
Implements fio's Linux native AIO engine through libaio. It batches `io_u` requests into an internal ring, submits them with `io_submit()`, reaps completions via `io_getevents()` or an optional user-space ring reader, and exposes options for `RWF_NOWAIT`, vectored AIO, and command-priority injection.

## Important APIs, Types, And Functions
`struct libaio_data` owns the AIO context, completion event buffer, queued IOCB pointers, matching `io_u` pointers, per-depth iovecs, circular queue indexes, and `struct cmdprio`. `struct libaio_options` provides `userspace_reap`, `nowait`, `libaio_vectored`, and `cmdprio` settings. Key functions are `fio_libaio_init()`, `fio_libaio_post_init()`, `fio_libaio_prep()`, `fio_libaio_queue()`, `fio_libaio_commit()`, `fio_libaio_getevents()`, `fio_libaio_event()`, and `fio_libaio_cleanup()`.

## Control Flow
`init` allocates buffers sized by `iodepth` and initializes command priority; `post_init` creates the kernel AIO context. `prep` encodes read/write IOCBs as either pread/pwrite or preadv/pwritev and sets `RWF_NOWAIT` or `RWF_ATOMIC` where supported. `queue` rejects when the internal ring is full, handles trim/syncfs synchronously if no queued AIO is outstanding, applies command priority, and appends the IOCB to the ring. `commit` submits contiguous ring spans, tracks issue time, advances the tail, and handles `EAGAIN`, `EINTR`, and `ENOMEM`. `getevents` loops until the requested minimum is met or errors occur, optionally reading the kernel completion ring directly when `userspace_reap` is safe.

## State And Persistence
Persistent state is the kernel AIO context plus queued-but-not-submitted IOCBs. User data is stored in fio's `io_u` IOCB member, so completion maps back with `container_of(ev->obj, struct io_u, iocb)`. File data is handled by generic fio file open/close/size operations.

## Dependencies And Integration Points
Depends on libaio, Linux `aio_abi` fields, fio's `cmdprio`, `io_u` lifecycle, generic file helpers, and fio issue-time accounting. It registers a single `libaio` `ioengine_ops`.

## Risks
The user-space reap path depends on kernel AIO ring layout and magic. `fio_libaio_commit()` has careful handling for partial submissions and transient resource failures; regressions can strand queued IOCBs. Trim and syncfs are synchronous only when the queue is empty. `aio_rw_flags` compatibility uses a preprocessor alias for older libaio headers.

## Test Signals
Exercise normal and vectored reads/writes, mixed queue depths, `iodepth_batch_complete_min=0`, `userspace_reap`, `nowait`, command-priority percentages, trim and syncfs interleaved with queued AIO, `EAGAIN`/resource-pressure behavior, and atomic writes when `FIO_HAVE_RWF_ATOMIC` is available.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libaio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libblkio.c -->
# sources/test-tools/fio/engines/libblkio.c

## Purpose
Implements a fio engine backed by libblkio, allowing fio workloads to target libblkio drivers and queue APIs rather than conventional file descriptors. It supports normal and poll queues, vectored read/write, discard or write-zeroes trim, custom libblkio properties, eventfd or polling completion waits, and libblkio-managed memory regions.

## Important APIs, Types, And Functions
Process-wide `proc_state` holds a mutex, initialized-thread counts, hipri-thread counts, and one shared `struct blkio *`. Per-thread `struct fio_blkio_data` stores a `struct blkioq *`, optional completion fd, optional allocated memory region, iovecs, and completion slots. `struct fio_blkio_options` contains driver/path/property strings, queue sizing, `hipri`, `vectored`, trim behavior, wait mode, and completion-eventfd forcing.

Key functions are `fio_blkio_set_props_from_str()`, `fio_blkio_check_opt_compat()`, `fio_blkio_create_and_connect()`, `fio_blkio_setup()`, `fio_blkio_init()`, `fio_blkio_post_init()`, `fio_blkio_iomem_alloc()`, `fio_blkio_iomem_free()`, `fio_blkio_queue()`, `fio_blkio_getevents()`, and `fio_blkio_event()`.

## Control Flow
`setup` validates threaded-subjob option compatibility, rejects incompatible hipri/eventfd combinations, creates a temporary blkio instance to fetch capacity, and records file size. `init` creates or reuses the process-wide blkio instance under a mutex, configures queue counts, starts libblkio, assigns each fio thread a regular or poll queue, optionally enables a blocking completion eventfd, and stores per-thread data. `post_init` maps fio core buffers into libblkio unless libblkio allocated them. `queue` calls the corresponding `blkioq_*` operation and attaches `io_u` as user data. `getevents` waits with blocking `blkioq_do_io()`, eventfd-driven polling, or busy-loop polling, and `event` maps completions back to `io_u` while translating `completion->ret`.

## State And Persistence
State is split between one shared libblkio object per process and per-thread queues. Memory regions may be owned by fio or allocated/mapped by libblkio. Persistent data effects are delegated to the selected libblkio driver; fio itself marks the engine diskless and no-extend because capacity and file I/O semantics are external.

## Dependencies And Integration Points
Depends on libblkio, fio options parsing helpers, fio threading model, memory allocation hooks, and `ioengine_ops` setup/init/post-init phases. The engine must coordinate with fio's `thread` option because multiple jobs in one process share the same libblkio object.

## Risks
Shared process state is subtle: incompatible threaded subjobs are tracked globally and all such jobs fail later. Cleanup destroys the shared blkio only when the last thread exits. Eventfd mode changes file descriptor blocking state. Memory-region length is recomputed to avoid fio padding that may violate libblkio alignment. The option parser mutates a duplicated property string; malformed `name=value` lists fail setup.

## Test Signals
Test single-process and threaded multi-job workloads, hipri and non-hipri queues, all wait modes, forced eventfd, custom properties before connect/start, vectored and non-vectored read/write, discard vs write-zeroes trim, libblkio-managed memory allocation/free, incompatible threaded option detection, and cleanup when jobs finish at different times.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libblkio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libcufile.c -->
# sources/test-tools/fio/engines/libcufile.c

## Purpose
Implements fio's NVIDIA cuFile engine for GPU Direct Storage style I/O, with a second POSIX mode that simulates CUDA copy overhead around ordinary pread/pwrite. It allocates GPU memory, optionally registers it with cuFile, registers file handles, and completes all operations synchronously from `queue()`.

## Important APIs, Types, And Functions
`struct libcufile_options` stores colon-separated GPU IDs, selected CUDA I/O mode, GPU memory pointer, POSIX simulation buffer, selected GPU, total allocation size, and one-shot alignment log flags. `struct fio_libcufile_data` stores the cuFile descriptor and handle per file. Important functions include `fio_libcufile_find_gpu_id()`, `fio_libcufile_init()`, `fio_libcufile_pre_write()`, `fio_libcufile_post_read()`, `fio_libcufile_queue()`, `fio_libcufile_open_file()`, `fio_libcufile_close_file()`, `fio_libcufile_iomem_alloc()`, `fio_libcufile_iomem_free()`, and `fio_libcufile_cleanup()`.

## Control Flow
Initialization uses a global mutex-protected `running` count so the cuFile driver is opened once for the first active worker and closed by the last. Each thread chooses a GPU by subjob number modulo the `gpu_dev_ids` list and calls `cudaSetDevice()`. I/O memory allocation creates fio's CPU buffer, optional POSIX junk buffer, CUDA device memory, initializes it, and registers the GPU buffer with cuFile in cuFile mode. File open uses generic fio open plus `cuFileHandleRegister()`.

`queue` handles sync via `fsync()`/`fdatasync()`. Read/write compute a per-`io_u` GPU offset, warn once for non-4KiB cuFile alignment, perform verify-related host/device copies or POSIX simulation copies, then loop until cuFile or POSIX I/O transfers the requested length. Reads may copy GPU data back to the fio buffer for verification.

## State And Persistence
Per-thread option state owns GPU memory and tracking flags. Per-file engine data owns cuFile handles. Global driver state is process-wide and reference counted by active jobs. Persistent file changes occur via `cuFileWrite()` or POSIX `pwrite()`; sync operations call the host file descriptor sync APIs.

## Dependencies And Integration Points
Depends on NVIDIA cuFile, CUDA driver/runtime APIs, pthread mutexes, and fio memory/file hooks. It registers as `FIO_SYNCIO`, so fio sees every queue operation as completed immediately.

## Risks
GPU offsets are derived from `io_u->index * xfer_buflen`, so variable block sizes can make offset assumptions fragile. cuFile alignment warnings are non-fatal even though performance or API behavior may vary. Global driver lifetime assumes all users of this engine follow the same process-local counter. Error handling mixes CUDA, cuFile negative statuses, and errno. POSIX mode intentionally copies through GPU memory but still writes from the fio CPU buffer.

## Test Signals
Test cuFile and POSIX modes, multiple GPU IDs/subjobs, verify and non-verify read/write, unaligned buffer lengths and offsets, partial cuFile/POSIX transfers, file handle register/deregister failures, CUDA allocation/register failures, sync/datasync operations, and last-thread driver close.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libcufile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libhdfs.c -->
# sources/test-tools/fio/engines/libhdfs.c

## Purpose
Implements an HDFS-backed fio engine using libhdfs. Because HDFS files are append-oriented and not normally mutable in-place, the engine maps a logical fio file into many fixed-size chunk files and selects the chunk by the fio offset to approximate random reads and writes.

## Important APIs, Types, And Functions
`struct hdfsio_data` stores the HDFS filesystem handle, currently open HDFS file handle, and current chunk id. `struct hdfsio_options` provides namenode host/port, working directory, chunk size, single-instance behavior, and direct-read selection. Key functions are `get_chunck_name()`, `fio_hdfsio_setup()`, `fio_hdfsio_init()`, `fio_hdfsio_io_u_init()`, `fio_hdfsio_prep()`, `fio_hdfsio_queue()`, `fio_hdfsio_open_file()`, `fio_hdfsio_close_file()`, and `fio_hdfsio_io_u_free()`.

## Control Flow
`setup` allocates engine state and computes logical file sizes from fio size/filesize options. `init` builds and connects an HDFS client, optionally forcing a new instance, and sets the working directory after checking existence. `io_u_init` pre-creates chunk files for each fio file, writing zero-filled buffers until every chunk reaches the configured size. `prep` maps `io_u->offset` to a chunk id, closes the previous chunk if necessary, chooses read or write flags, opens the chunk, and stores it as current. `queue` seeks within the chunk, performs `hdfsRead()`, `readDirect()`, `hdfsWrite()`, or `hdfsFlush()`, and completes synchronously.

## State And Persistence
Logical fio file state is persisted as HDFS paths named `file_name_chunkid`. The engine tracks only one open chunk per thread. `curr_file_id == -1` means no current file. File sizes are logical and set in fio metadata, not queried from HDFS except during chunk preparation.

## Dependencies And Integration Points
Depends on libhdfs and fio diskless/sync engine hooks. It avoids generic POSIX open/close and marks itself `FIO_SYNCIO | FIO_DISKLESSIO | FIO_NODISKUTIL`.

## Risks
The code uses the misspelled `chunck` naming throughout, which matters for option aliasing and path formatting. `io_u_free` disconnects the HDFS filesystem, so lifecycle correctness depends on fio calling it in a safe order relative to all `io_u` objects. `hdfsGetPathInfo()` results are not freed in the source. Random writes smaller than chunks can fail because HDFS seek/write semantics are limited. `fio_hdfsio_open_file()` sets `td->error` for `direct` but returns 0.

## Test Signals
Test chunk creation for multiple files, exact and non-exact logical size to chunk-size division, read/write/sync paths, `hdfs_use_direct`, missing directory/host failures, `single_instance=0`, random write behavior across chunk boundaries, close/reopen chunk transitions, and cleanup/disconnect behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libhdfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libiscsi.c -->
# sources/test-tools/fio/engines/libiscsi.c

## Purpose
Implements an iSCSI fio engine using libiscsi and SCSI CDB helpers. It connects each fio file URL as a LUN, discovers capacity and block size, submits asynchronous SCSI READ16/WRITE16/SYNCHRONIZE CACHE commands, and polls libiscsi file descriptors for completions.

## Important APIs, Types, And Functions
`struct iscsi_lun` owns a libiscsi context, parsed URL, block size, and block count. `struct iscsi_info` owns all LUNs, pollfd array, completed-event list, and event count. `struct iscsi_task` links a SCSI task to its LUN and fio `io_u`. Important functions are `fio_iscsi_setup_lun()`, `fio_iscsi_setup()`, `fio_iscsi_queue()`, `iscsi_cb()`, `fio_iscsi_getevents()`, `fio_iscsi_event()`, and cleanup helpers.

## Control Flow
Setup parses each file name as a full iSCSI URL, creates a context using the configured initiator, sets target/session/header-digest options, connects synchronously, sends READ CAPACITY(16), extracts block size and block count, stores real fio size, and records the libiscsi fd in `pfds`. Queue validates read/write alignment to the LUN block size, builds READ16/WRITE16 or synchronize-cache CDBs, attaches buffers, allocates an `iscsi_task`, and submits asynchronously. The callback records success or error and appends the task to `complete_events`. `getevents` polls all LUN fds, services libiscsi events until at least `min` completions are buffered, and `event` frees the SCSI task wrapper.

## State And Persistence
Each fio file's `engine_data` points to its LUN. Completion state is buffered in `iscsi_info->complete_events` until fio consumes it. Persistent effects are remote SCSI writes and cache synchronize commands.

## Dependencies And Integration Points
Depends on libiscsi, SCSI low-level helpers, `poll()`, and fio diskless async event hooks. It bypasses generic file open/close and registers no-op open/close.

## Risks
Setup allocations are not fully checked for NULL. The loop in `fio_iscsi_setup()` breaks only on `ret < 0`, while some setup errors are positive, which can leave partially initialized state. `complete_events` is sized by `iodepth` and callback increments without explicit bounds. Sync command length uses bytes where SCSI synchronize-cache expects block addressing fields from the helper API. Poll timeout ignores fio's `timespec` parameter.

## Test Signals
Test valid and invalid iSCSI URLs, multiple LUNs, capacity discovery, unaligned offset/buffer rejection, read/write/sync command completion, failed SCSI statuses, partial setup cleanup, concurrent completions up to `iodepth`, EINTR/EAGAIN poll handling, and logout/destroy cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libiscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libpmem.c -->
# sources/test-tools/fio/engines/libpmem.c

## Purpose
Implements a PMDK libpmem-backed synchronous engine. It maps files from a DAX-capable persistent-memory filesystem with `pmem_map_file()`, reads with `memcpy()`, writes with `pmem_memcpy()`, and drains persistence on sync operations or synchronous write settings.

## Important APIs, Types, And Functions
`struct fio_libpmem_data` stores the mapped pointer, mapped size, and map offset for each fio file. Key functions are `fio_libpmem_init()`, `fio_libpmem_file()`, `fio_libpmem_open_file()`, `fio_libpmem_prep()`, `fio_libpmem_queue()`, and `fio_libpmem_close_file()`.

## Control Flow
`init` rejects block sizes smaller than a page when fsync/fdatasync options require mmap-style page granularity. `open_file` allocates per-file data, sets map size to `f->io_size`, and calls `pmem_map_file()` with create permissions. `prep` validates the block size does not exceed real file size and points `io_u->mmap_data` at the mapped address plus fio offset. `queue` copies from mapped memory for reads, copies to mapped memory for writes using flags derived from `sync_io` and `odirect`, and calls `pmem_drain()` for sync-like directions.

## State And Persistence
The persistent backing is the mapped file on a DAX filesystem. Per-file engine data tracks one mapping. `sync=1` or explicit sync operations ensure `pmem_drain()`; otherwise writes use `PMEM_F_MEM_NODRAIN` and may require later drain.

## Dependencies And Integration Points
Depends on PMDK `libpmem`, fio verify support, file prepopulation, generic size handling, and fio `FIO_MEMALIGN`/`FIO_BARRIER` behavior. It is synchronous and diskless from fio's perspective.

## Risks
`pmem_map_file()` can succeed on non-pmem files; the code reports an error but retains mapping until error cleanup. Close uses `ret &= generic_close_file()`, which can mask return semantics. It assumes mapping size is `f->io_size` and does not implement remapping for offsets beyond that. Pointer arithmetic on `void *` is a compiler extension.

## Test Signals
Test DAX and non-DAX paths, read/write/sync with `sync=0` and `sync=1`, `direct=1` nontemporal mode, too-small block sizes with fsync/fdatasync, oversized block rejection, verify workloads, map/unmap failure handling, and prepopulation integration.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libpmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/libzbc.c -->
# sources/test-tools/fio/engines/libzbc.c

## Purpose
Implements a synchronous libzbc engine for host-aware/host-managed SMR or ZBC/ZAC devices. It performs direct sector-based reads/writes/flushes and implements fio zoned-block-device callbacks by translating libzbc zone data into fio's `zbd_zone` model.

## Important APIs, Types, And Functions
`struct libzbc_data` stores the libzbc device handle, device model, sector count, and max-open sequential requirement. Important functions are `libzbc_open_dev()`, `libzbc_get_dev_info()`, `libzbc_get_file_size()`, `libzbc_get_zoned_model()`, `libzbc_report_zones()`, `libzbc_reset_wp()`, `libzbc_move_zone_wp()`, `libzbc_finish_zone()`, `libzbc_get_max_open_zones()`, `libzbc_rw()`, and `libzbc_queue()`.

## Control Flow
Open validates that the fio file is a block or char device, chooses read/write flags based on workload, opens with SCSI/ATA libzbc drivers, and caches device info in `td->io_ops_data`. Size is `nr_sectors << 9`. Zone reporting allocates a libzbc zone array, calls `zbc_report_zones()`, converts starts/lengths/write pointers from sectors to bytes, maps types and conditions, and treats read-only/offline/unknown conditions as offline. Queue handles read/write through `zbc_pread()`/`zbc_pwrite()`, sync through `zbc_flush()`, and trim through fio's zbd trim helper.

## State And Persistence
One libzbc device handle is stored per thread. Persistent changes include writes, flushes, zone resets, zone finishes, and write-pointer movement by writing filler data. The engine does not cache normal I/O data and invalidation is a no-op.

## Dependencies And Integration Points
Depends on libzbc, fio `zbd` types/helpers, and raw direct device access. It supplies fio's zoned callbacks for model, report, reset, finish, max-open, and write-pointer movement.

## Risks
All I/O lengths and offsets are converted with `>> 9`, so callers must honor 512-byte sector alignment. Some functions assume `td->io_ops_data` is already open. Error handling negates libzbc return values and logs sense-key details when available. Zone capacity is set equal to zone length because ZBC/ZAC lacks an explicit capacity field.

## Test Signals
Test block and char devices, host-aware/host-managed model detection, size discovery, zone reporting conversions, reset-all and per-zone reset, finish-zone, write-pointer movement, read/write short transfer errors, flush, trim in zbd mode, max-open-zone limit handling, and open/close cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/libzbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/mmap.c -->
# sources/test-tools/fio/engines/mmap.c

## Purpose
Implements fio's memory-mapped file engine. It maps a whole file when feasible or maps per-I/O windows when necessary, performs read/write as memory copies, and implements sync by `msync()`.

## Important APIs, Types, And Functions
`struct fio_mmap_data` stores mapped pointer, mapped size, and map offset per file. When transparent hugepage support is compiled, `struct mmap_options` exposes `thp`. Key functions are `fio_mmapio_init()`, `fio_mmap_file()`, `fio_mmapio_prep_full()`, `fio_mmapio_prep_limited()`, `fio_mmapio_prep()`, `fio_mmapio_queue()`, `fio_mmapio_open_file()`, and `fio_mmapio_close_file()`.

## Control Flow
`init` rejects sub-page minimum block sizes when direct/sync options require page granularity and divides a 1 GiB mapping cap across files for 32-bit safety. File open uses generic open and attaches per-file mapping state. `prep` reuses an existing mapping if the requested offset/length fits; otherwise it unmaps, attempts a full-file map, and falls back to a limited window if the full map fails or is too large. Mapping protection is derived from workload direction and verify settings. `queue` copies from/to the mapped region, calls `msync()` for sync, delegates trim to fio, and for `direct=1` forces `msync()` plus `POSIX_MADV_DONTNEED` on the touched range.

## State And Persistence
Per-file mapping state is stored in `FILE_ENG_DATA`. The file's partial-mmap flag records that full mapping is unsuitable. Writes persist to the mapped file according to normal mmap and `msync` semantics.

## Dependencies And Integration Points
Depends on POSIX `mmap`, `munmap`, `msync`, `posix_madvise`, optional `MADV_HUGEPAGE`, fio generic file helpers, and fio verify/read/write settings.

## Risks
`fio_mmapio_close_file()` frees mapping metadata but does not unmap an active mapping, so correctness depends on prior prep/unmap behavior or process cleanup. Full-map fallback clears fio error before limited mapping. `MAP_PRIVATE` is used when `thp` is requested, changing write persistence semantics. Direct I/O behavior is simulated with sync/drop-cache advice rather than true O_DIRECT.

## Test Signals
Test full-file and partial-window mapping, 32-bit/large-file fallback, read/write/verify protections, sync and trim, `direct=1` drop behavior, THP option behavior, fadvise/madvise combinations, unaligned page-size rejection, and repeated offsets that reuse vs remap.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/mtd.c -->
# sources/test-tools/fio/engines/mtd.c

## Purpose
Implements a synchronous fio engine for Linux MTD character devices. It splits each request across erase-block boundaries, performs MTD read/write/erase operations through libmtd/oslib helpers, and can skip known bad erase blocks.

## Important APIs, Types, And Functions
Global `desc` is the libmtd descriptor opened at engine registration. `struct fio_mtd_data` stores `mtd_dev_info` per file. `struct fio_mtd_options` exposes hidden `skip_bad`. Important functions are `fio_mtd_queue()`, `fio_mtd_maybe_mark_bad()`, `fio_mtd_is_bad()`, `fio_mtd_open_file()`, `fio_mtd_close_file()`, and `fio_mtd_get_file_size()`.

## Control Flow
Registration opens libmtd. File open uses generic open, allocates per-file MTD data, and queries device info. Queue loops over the `io_u` buffer, computing erase-block index and offset, limiting each sub-operation to the current erase block. With `skip_bad`, it checks and silently skips bad blocks. Reads call `mtd_read()`, writes call `mtd_write()`, trims require whole erase-block alignment and call `mtd_erase()`. On `EIO`, the engine attempts to mark the erase block bad.

## State And Persistence
Per-file engine data caches erase-block size and total MTD size. Persistent effects are writes, erases, and marking blocks bad. Skipped bad-block ranges still advance through the request without transferring data.

## Dependencies And Integration Points
Depends on Linux MTD UAPI, fio's oslib libmtd wrapper, generic file helpers, and synchronous fio queue completion.

## Risks
Partial failures can leave `io_u->error` set while the loop advances to later erase blocks. Trim alignment is checked per erase block but the loop continues unless a helper failure breaks it. Bad-block marking only happens for `errno == EIO`. The global libmtd descriptor must be valid for all engine users.

## Test Signals
Test reads/writes spanning multiple erase blocks, trim alignment failures and aligned erases, `skip_bad=1`, simulated `EIO` bad-block marking, file-size discovery, open failure cleanup, and registration/unregistration descriptor lifecycle.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/nbd.c -->
# sources/test-tools/fio/engines/nbd.c

## Purpose
Implements an asynchronous Network Block Device engine using libnbd. It connects to an NBD URI, discovers export size, issues asynchronous read/write/trim/flush commands, polls for command completion, and maps callbacks back to fio `io_u` objects.

## Important APIs, Types, And Functions
`struct nbd_data` stores the libnbd handle, debug flag, dynamically sized completed-`io_u` list, and completion count. `struct nbd_options` stores the required URI. Key functions are `nbd_setup()`, `nbd_init()`, `nbd_queue()`, `cmd_completed()`, `retire_commands()`, `nbd_getevents()`, `nbd_event()`, and `nbd_cleanup()`.

## Control Flow
`setup` creates fio's synthetic file if needed, creates an NBD handle, connects synchronously to fetch size, records `real_file_size`, then closes the setup handle. `init` creates a per-thread handle and connects. `queue` attaches `nbd_data` to `io_u->engine_data`, asserts read/write size is within `NBD_MAX_REQUEST_SIZE`, and calls the appropriate `nbd_aio_*` function with a callback. The callback stores the error result and appends the `io_u` to `completed` via `realloc()`. `getevents` repeatedly calls `nbd_poll()` and retires completed cookies until enough completions exist. `event` pops completed `io_u` entries in LIFO order.

## State And Persistence
The network export is persistent; fio file state is synthetic. Completion state is held in a heap array on `nbd_data`. The libnbd handle is per fio thread after init.

## Dependencies And Integration Points
Depends on libnbd, fio diskless/noextend engine behavior, and fio async event callbacks. It provides no generic file open because the connection is the target.

## Risks
Setup error paths can return without freeing partially allocated `nbd_data` or handles. Completion list grows with `realloc()` and is popped LIFO, ignoring the event index. Timeout handling notes that loop iterations can wait longer than requested. `max` is not used to cap event return count. The read/write request limit is an assert, not a recoverable validation.

## Test Signals
Test missing/bad URI, size discovery, reconnect in `init`, read/write/trim/flush, callback error propagation with and without errno, debug logging, request sizes near 64 MiB, timeout behavior, multiple completions, and cleanup after setup/init failures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/nbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/net.c -->
# sources/test-tools/fio/engines/net.c

## Purpose
Implements fio network engines `net` and, when Linux splice support is enabled, `netsplice`. It sends and receives fio I/O buffers over TCP, UDP, IPv6 variants, UNIX sockets, and vsock streams, with optional ping-pong behavior, socket tuning, multicast support, UDP sequencing, and splice/vmsplice data movement.

## Important APIs, Types, And Functions
`struct netio_data` stores listen fd, splice pipe fds, resolved socket addresses, and UDP sequence counters. `struct netio_options` stores port, protocol, listen/pingpong flags, TCP_NODELAY, TTL, window size, MSS, and multicast interface. Important functions include `fio_netio_setup()`, `fio_netio_init()`, `fio_netio_open_file()`, `fio_netio_connect()`, `fio_netio_accept()`, `fio_netio_queue()`, `fio_netio_send()`, `fio_netio_recv()`, splice helpers, UDP open/close helpers, address setup helpers, and cleanup/terminate.

## Control Flow
`setup` creates a synthetic fio file and allocates net state. `init` rejects random I/O, validates protocol/port/filename combinations, offsets the port by subjob number, and either prepares a listening socket or resolves/connects a peer address. `open_file` accepts or connects a socket, then performs UDP open handshake if needed. `queue` performs synchronous send or receive for the requested direction; ping-pong mode immediately performs the opposite direction after a completed operation. Datagram protocols are forced to one direction, while TCP/vsock can listen or connect. `netsplice` uses pipes plus splice/vmsplice for stream protocols except UDP and UNIX sockets.

## State And Persistence
Network state is process runtime only: listen fd, accepted/connected fd, pipe fds, UDP sequence counters, and peer addresses. UDP close/open control messages signal lifecycle. Sequence trailers track dropped UDP datagrams in fio stats when verify is disabled.

## Dependencies And Integration Points
Depends on POSIX sockets, optional IPv6/vsock/splice/TCP socket options, fio synthetic files, fio unidirectional pipe I/O flags, and fio termination behavior. `hostname` option writes into `td->o.filename`.

## Risks
Synchronous send/recv loops can block indefinitely through `poll_wait()`. Close notification is sent for all protocols through `sendto()` with protocol-dependent address handling. UDP open/close magic uses mixed host/network/le conversions in different paths. `fio_netio_terminate()` sends SIGTERM to `td->pid`. Multicast is IPv4-only. Port is mutated by subjob number during init, which can surprise reused option state.

## Test Signals
Test TCP client/server, UDP sender/receiver, IPv6 builds, UNIX sockets, vsock with and without support, multicast join/interface/TTL, ping-pong, close/open handshakes, UDP sequence loss accounting, socket window/MSS/TCP_NODELAY options, netsplice stream transfer, partial send/recv and EMSGSIZE busy behavior, and termination while blocked in accept/poll.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/nfs.c -->
# sources/test-tools/fio/engines/nfs.c

## Purpose
Implements an asynchronous NFS engine using libnfs. It mounts an NFS URL, opens fio file paths on that mount, queues asynchronous pread/pwrite operations, and buffers completions for fio's event loop.

## Important APIs, Types, And Functions
`struct fio_libnfs_options` stores the shared libnfs context, URL, queue depth, outstanding/buffered completion counters, circular event-buffer indexes, and event array. `struct nfs_data` stores an opened NFS file handle and pointer back to options. Key functions are `do_mount()`, `fio_libnfs_setup()`, `fio_libnfs_open()`, `fio_libnfs_queue()`, `nfs_callback()`, `nfs_event_loop()`, `fio_libnfs_getevents()`, `fio_libnfs_event()`, `fio_libnfs_close()`, and `fio_libnfs_cleanup()`.

## Control Flow
`setup` disables fio thread mode because libnfs can hang on threaded exit. `open` requires `nfs_url`, mounts once per job through `do_mount()`, allocates per-file state, and opens the NFS file. Queue attaches the per-file state to `io_u`, calls libnfs async read or write with API-version-dependent argument order, and increments `outstanding_events`. The libnfs callback copies read data into the fio buffer, sets error/residual fields, and appends the `io_u` to a circular completion buffer. `getevents` services the libnfs fd via `poll()` and `nfs_service()` until completions are buffered or queue pressure is relieved. `event` returns completions in buffered order and validates sequential fio event requests with asserts.

## State And Persistence
The NFS context and completion buffer are stored in option state. Per-file engine data owns each `nfsfh`. Persistent effects are remote NFS writes. The engine does not support trim.

## Dependencies And Integration Points
Depends on libnfs headers, fio event callbacks, fio option state, and POSIX `poll()`. It marks itself diskless/noextend/no diskutil.

## Risks
`do_mount()` assumes `nfs_parse_url_full()` succeeds and builds mount path by concatenating URL path and file. Completion buffers are assert-heavy rather than gracefully bounded. `fio_libnfs_getevents()` ignores `min`, `max`, and timeout arguments and returns whatever the event loop has buffered. Cleanup assumes context was mounted. EOF on read is logged as likely unexpected.

## Test Signals
Test missing and malformed `nfs_url`, mount/open failure, LIBNFS API v1/v2 builds, read/write completions, EOF reads, event ordering assertions, queue-depth saturation, trim rejection, cleanup after partial open, and non-threaded multi-job behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/nfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/null.c -->
# sources/test-tools/fio/engines/null.c

## Purpose
Implements fio's fake `null` engine and an optional external C++ `cpp_null` engine. It performs no real I/O and is used to test fio scheduling, queueing, issue-time accounting, and external engine ABI behavior.

## Important APIs, Types, And Functions
`struct null_data` stores queued `io_u` pointers, queued count, and event count. Shared helpers are `null_init()`, `null_queue()`, `null_commit()`, `null_getevents()`, `null_event()`, `null_open()`, and `null_cleanup()`. C wrappers register the built-in C engine, while the C++/external section wraps `null_data` in `NullData` and exposes `get_ioengine()`.

## Control Flow
`null_init` chooses synchronous mode when `iodepth == 1`; otherwise it allocates an `io_u` array and marks the engine as setting issue time. `queue` completes immediately for sync mode, returns busy if previous async events are waiting, or stores the `io_u` for later commit. `commit` stamps issue time for all queued requests, marks them submitted for built-in builds, moves queued count into event count, and resets queued count. `getevents` returns and clears events only when a nonzero minimum is requested. `event` indexes the stored `io_u` array.

## State And Persistence
There is no persistent storage effect. State is purely in-memory per thread and exists only to model fio engine behavior.

## Dependencies And Integration Points
Depends on fio core `ioengine_ops`, issue-time helpers, and external engine ABI definitions. It conditionally compiles alternate behavior under `__cplusplus` and `FIO_EXTERNAL_ENGINE`.

## Risks
The async path supports only one outstanding committed batch at a time because `queue` returns busy while `events` is nonzero. `null_getevents()` ignores `max` and timeout. Dynamic changes to `td->io_ops->flags` in init require `td_set_ioengine_flags()` to keep fio state coherent.

## Test Signals
Test `iodepth=1` synchronous completion, `iodepth>1` queue/commit/getevents/event flow, issue-time accounting, busy behavior before events are consumed, read/write/trim fake operations, built-in registration, and external C++ engine loading through `get_ioengine()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/nvme.c -->
# sources/test-tools/fio/engines/nvme.c

## Purpose
Provides NVMe helper logic for the `io_uring_cmd` engine. It constructs NVMe passthrough commands, discovers namespace/controller geometry and protection-information capabilities, generates and verifies PI guard/application/reference tags, implements ZNS zone callbacks, and fetches FDP reclaim unit handle status.

## Important APIs, Types, And Functions
Important exported functions are `fio_nvme_uring_cmd_prep()`, `fio_nvme_pi_fill()`, `fio_nvme_generate_guard()`, `fio_nvme_pi_verify()`, `fio_nvme_get_info()`, `fio_nvme_get_zoned_model()`, `fio_nvme_report_zones()`, `fio_nvme_reset_wp()`, `fio_nvme_get_max_open_zones()`, and `fio_nvme_iomgmt_ruhs()`. Internal helpers include 16-byte and 64-byte PI generate/verify functions, `fio_nvme_uring_cmd_trim_prep()`, `nvme_identify()`, `nvme_report_zones()`, and `nvme_fdp_reclaim_unit_handle_status()`.

## Control Flow
Command prep zeroes an `nvme_uring_cmd`, selects opcode by fio direction, builds DSM ranges for trim, flush for sync, SLBA/NLB for read/write/compare/verify/write-zeroes/write-uncorrectable, optionally points to an iovec, and attaches separate metadata when present. PI fill sets NVMe PRINFO flags, generates guard data when the controller will not insert/remove it, and populates reference/application tag command dwords. PI verification recomputes CRC-T10DIF or NVMe CRC64 and compares guard/app/ref tags per LBA. Info discovery opens the namespace char device, reads namespace id, identify controller, identify namespace, optional NVM namespace identify for ELBAS, computes LBA size/extended LBA metadata, PI type, guard type, and namespace size.

ZNS helpers identify ZNS support, report zones in chunks, translate NVMe descriptors to fio `zbd_zone`, reset zone write pointers, and read max-open-zone limits. FDP helper sends an IO management receive command and maps unsupported failures to `-ENOTSUP`.

## State And Persistence
`struct nvme_data` is stored by callers in file engine data and carries namespace id, LBA sizes, metadata size, PI type, guard type, and PI location. Helper calls can alter device state through DSM deallocate and ZNS reset operations.

## Dependencies And Integration Points
Depends on Linux NVMe ioctl UAPI, fio CRC implementations, endian helpers, fio `zbd` types, and `nvme.h` structure declarations. It is not a standalone engine; `io_uring.c` calls it for command setup, open validation, completion verification, and zoned/FDP callbacks.

## Risks
The helpers require `/dev/ngXnY` namespace generic char devices. LBA/metadata validation must match the caller's block-size checks. PI interval calculation differs for extended vs separate metadata and first/last PI placement. `fio_nvme_get_max_open_zones()` returns `mor + 1`; callers must know NVMe zero-based semantics. Some identify failures return raw ioctl errors while other paths return negative errno.

## Test Signals
Test NVM and ZNS namespace identify, unsupported file types, namespaces with no PI, 16-byte and 64-byte guards, PRACT on/off, extended and separate metadata, read/write/compare/verify/flush/trim command construction, multi-range DSM, ZNS report/reset/max-open behavior, FDP RUH fetch, and CRC mismatch error logs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/nvme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/nvme.h -->
# sources/test-tools/fio/engines/nvme.h

## Purpose
Declares NVMe UAPI-compatible structures, constants, helper inline functions, and public helper prototypes used by fio's `io_uring_cmd` NVMe implementation. It provides local fallback definitions for `nvme_uring_cmd` when system headers lack them.

## Important APIs, Types, And Functions
Key declarations include `struct nvme_uring_cmd`, NVMe passthrough ioctl constants, identify CNS/CSI/admin/io opcode enums, PI constants, ZNS state/type constants, FDP RUH structures, DSM range structures, `struct nvme_data`, `struct nvme_pi_data`, `struct nvme_cmd_ext_io_opts`, identify namespace/controller structs, and ZNS descriptor/report structs. Inline helpers are `ilog2()`, `put_unaligned_be48()`, `get_unaligned_be48()`, `fio_nvme_pi_ref_escape()`, `get_slba()`, and `get_nlb()`.

## Control Flow
As a header, it does not own runtime control flow. The inline helpers convert byte offsets and lengths into NVMe logical block numbers using either extended-LBA byte size or `lba_shift`, encode/decode 48-bit reference tags, and detect PI reference escape patterns.

## State And Persistence
The important state carrier is `struct nvme_data`, which is populated by `nvme.c` and stored in fio file engine data by `io_uring.c`. Other structs mirror device command/identify wire formats and do not own lifetime.

## Dependencies And Integration Points
Depends on `<linux/nvme_ioctl.h>` and fio core types. It is included by `io_uring.c` and `nvme.c`, binding the `io_uring_cmd` engine to local NVMe command construction and zoned/FDP helper APIs.

## Risks
Many structures mirror kernel/NVMe specification layout; padding, endian annotations, and field sizes must stay compatible with ioctl expectations. The fallback `nvme_uring_cmd` must match kernel UAPI when headers are old. `get_nlb()` returns zero-based NLB for read/write but callers adjust DSM trim to one-based ranges.

## Test Signals
Compile against old and new kernel headers, validate command struct sizes used by ioctls, exercise inline SLBA/NLB conversion with extended and non-extended LBAs, 48-bit tag encode/decode, PI reference escape handling, and all exported prototypes through `nvme.c`/`io_uring.c` builds.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/nvme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/page_fault.c -->
# sources/test-tools/fio/engines/page_fault.c

## Purpose
Implements a synchronous diskless engine that performs I/O against anonymous private memory. The goal is to benchmark or exercise page-fault behavior by reading/writing an mmap'd region rather than a real file.

## Important APIs, Types, And Functions
`struct fio_page_fault_data` stores the anonymous mapping pointer and size. Key functions are `fio_page_fault_init()`, `fio_page_fault_queue()`, `fio_page_fault_cleanup()`, and no-op open/close hooks.

## Control Flow
`init` rejects multiple files and nonzero `start_offset`, allocates state, maps `td->o.size` bytes with `MAP_PRIVATE | MAP_ANONYMOUS`, and stores it in `td->io_ops_data`. `queue` validates state and bounds, computes the mapped address from `io_u->offset`, copies from mapping on reads, copies to mapping on writes, treats sync directions as no-ops, and rejects unsupported directions. Cleanup unmaps and frees state.

## State And Persistence
All data is volatile anonymous memory and disappears at cleanup/process exit. There is no file persistence despite generic file-size integration.

## Dependencies And Integration Points
Depends on `mmap()`/`munmap()` and fio synchronous diskless engine hooks. Generic file-size callback is present, but open/close are no-ops.

## Risks
The mapping size is exactly `td->o.size`; any workload that generates offsets beyond that returns EINVAL. It does not support multiple files or start offsets. Mapping failure returns 1 without setting detailed fio error state.

## Test Signals
Test single-file read/write, sync no-op directions, unsupported directions, out-of-bounds offsets, multiple-file rejection, start-offset rejection, mapping allocation failure, and cleanup unmap.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/page_fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/engines/posixaio.c -->
# sources/test-tools/fio/engines/posixaio.c

## Purpose
Implements fio's POSIX AIO engine using `aio_read()`, `aio_write()`, `aio_suspend()`, `aio_error()`, `aio_return()`, and optionally `aio_fsync()`. It is a portable async engine relative to Linux native AIO, with synchronous fallbacks for trim and some sync paths.

## Important APIs, Types, And Functions
`struct posixaio_data` stores completed event pointers and current queued count. Important functions are `fio_posixaio_init()`, `fio_posixaio_prep()`, `fio_posixaio_queue()`, `fio_posixaio_getevents()`, `fio_posixaio_event()`, and `fio_posixaio_cleanup()`.

## Control Flow
`prep` fills the per-`io_u` `aiocb` with file descriptor, buffer, length, offset, and `SIGEV_NONE`, then clears `io_u->seen`. `queue` issues `aio_read()` or `aio_write()`, handles trim synchronously only when no POSIX AIO is queued, and either calls `aio_fsync()` for sync directions or falls back to fio synchronous sync when unavailable. `EAGAIN` maps to `FIO_Q_BUSY` so fio naturally throttles queue depth. `getevents` scans all in-flight `io_u`s, calls `aio_error()`, records completions, computes residuals with `aio_return()`, waits on up to eight active aiocbs with `aio_suspend()`, and respects an approximate timeout using monotonic time.

## State And Persistence
State is per-thread: queued count and a completion array sized by `iodepth`. The POSIX AIO control block itself is embedded in each `io_u`. Persistent effects are normal file reads/writes and optional fsync.

## Dependencies And Integration Points
Depends on POSIX AIO, fio generic file helpers, fio `io_u_all` iteration, and optional `CONFIG_POSIXAIO_FSYNC`. The registered engine flags advertise asynchronous trim/syncfs handling behavior.

## Risks
`aio_suspend()` is called even if `suspend_entries` is zero after scans, depending on workload state. Timeout handling restarts scans and can be approximate. `retval` from `aio_return()` is used directly to compute residual; negative unexpected returns could inflate residual. Completion scanning is O(total io_u) per getevents call.

## Test Signals
Test reads/writes at varying queue depths, low OS AIO limit producing `EAGAIN`, trim while queued vs idle, fsync with and without `CONFIG_POSIXAIO_FSYNC`, cancellations (`ECANCELED`), timeout behavior, residual computation for short I/O, and cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/engines/posixaio.c -->
