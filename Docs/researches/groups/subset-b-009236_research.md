# Research: subset-b-009236

Grouped research for IOR abstract I/O backends under `sources/test-tools/ior/src`. Each section preserves the source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-CEPHFS.c -->
# sources/test-tools/ior/src/aiori-CEPHFS.c

## Purpose
Implements the IOR `CEPHFS` backend using libcephfs. It exposes file I/O, metadata operations, statfs, sync, and mdtest support through a single `ior_aiori_t cephfs_aiori` registration.

## Important APIs, Types, and Functions
- `struct cephfs_options` holds cluster user, config file, local prefix, remote mount prefix, and lazy-I/O flag. A static instance backs `option_help options`.
- Global `struct ceph_mount_info *cmount` is the mounted CephFS session shared by all callbacks in the process.
- `CEPHFS_Init` creates the mount handle, reads the Ceph config, mounts the remote prefix, and validates root lookup.
- `CEPHFS_Open` maps IOR flags to Ceph flags, strips the configured local prefix with `pfix`, opens via `ceph_open`, and optionally enables `ceph_lazyio`.
- `CEPHFS_Xfer` uses positional `ceph_write` and `ceph_read`; `CEPHFS_Fsync` uses `ceph_fsync`; `CEPHFS_Sync` uses `ceph_sync_fs`.
- Metadata callbacks use `ceph_stat`, `ceph_statfs`, `ceph_mkdir`, `ceph_rmdir`, and `ceph_unlink`.

## Control Flow
IOR calls `.get_options`, `.initialize`, `.xfer_hints`, then create/open, transfer, close/remove, and finalize callbacks. `CEPHFS_Create` delegates to `CEPHFS_Open` with `IOR_CREAT`. Transfers return the requested length after checking for negative or short backend results. `GetFileSize` stat results are reconciled across MPI ranks using sum for file-per-process and min/max consistency checking for shared-file runs.

## State and Persistence
CephFS durability depends on the remote Ceph cluster and explicit `ceph_fsync`/`ceph_sync_fs`. `cmount`, the option singleton, and `hints` are process-global. File handles are heap-allocated `int *` values freed in close.

## Dependencies and Integration Points
Requires `<cephfs/libcephfs.h>`, MPI collectives through IOR utilities, and IOR globals such as `rank`, `testComm`, and `hints`. `enable_mdtest = true` means metadata benchmark paths exercise directory/stat/access callbacks.

## Risks and Edge Cases
- `CEPHFS_Init` warns and returns if options are not populated, so later callbacks can dereference an unmounted `cmount`.
- `pfix` assumes `o.prefix` is non-null and strips it by byte prefix, not path component.
- `CEPHFS_ERR` sets `errno = -ret` and calls fatal IOR error handling; use after already positive `EINVAL` values can set a negative errno.
- Append and direct I/O are explicitly unsupported.
- Lazy I/O changes persistence semantics and only logs a warning if enabling it fails.

## Test Signals
Exercise initialization with missing and valid Ceph options, prefix stripping, N-N and N-1 file-size paths, short-read/short-write failures, `fsyncPerWrite`, lazy I/O, and mdtest operations for mkdir/rmdir/stat/statfs/access.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-CEPHFS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-CHFS.c -->
# sources/test-tools/ior/src/aiori-CHFS.c

## Purpose
Implements a thin IOR backend for CHFS with file, transfer, fsync, directory, stat, and mdtest callbacks.

## Important APIs, Types, and Functions
- `struct CHFS_File` wraps an integer CHFS file descriptor.
- `struct chfs_option` currently exposes `chfs.chunk_size`; `CHFS_options` optionally calls `chfs_set_chunk_size`.
- `CHFS_initialize`/`CHFS_finalize` call `chfs_init(NULL)` and `chfs_term()`.
- `CHFS_create`, `CHFS_open`, `CHFS_xfer`, `CHFS_close`, `CHFS_delete`, and `CHFS_fsync` directly wrap the corresponding `chfs_*` APIs.
- Metadata wrappers include `chfs_stat`, `chfs_mkdir`, and `chfs_rmdir`; `CHFS_statfs` returns success without filling statfs fields.

## Control Flow
IOR installs hints, initializes CHFS, then creates/opens files unless `hints->dryRun` is set. Transfers use `chfs_pwrite` for writes and `chfs_pread` otherwise, returning the backend byte count rather than forcing the requested length.

## State and Persistence
The backend state is a global `hints` pointer plus per-open `struct CHFS_File` allocations. Durability is through `chfs_fsync`; `CHFS_sync` is a no-op.

## Dependencies and Integration Points
Requires `<chfs.h>` plus IOR `ior_aiori_t` integration. `enable_mdtest = true`, so metadata functions must behave correctly for mdtest-style workloads.

## Risks and Edge Cases
- Dry-run create/open returns `NULL`, and close/delete/fsync become no-ops.
- Transfer short counts are returned to the caller without local retry logic.
- `CHFS_statfs` does not populate capacity fields, so consumers expecting real filesystem statistics get zeros or prior contents.
- Option help marks `chunk_size` as a flag even though it is a size value.

## Test Signals
Compile with CHFS headers, validate chunk-size option parsing, verify dry-run does not call CHFS APIs, test short transfer reporting, and run mdtest-style mkdir/rmdir/stat/access paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-CHFS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-DFS.c -->
# sources/test-tools/ior/src/aiori-DFS.c

## Purpose
Implements the IOR `DFS` backend for DAOS DFS, including pool/container connection, DFS mount, file/object transfer, metadata operations, statfs, rename, and optional container destruction.

## Important APIs, Types, and Functions
- `DFS_options_t` contains pool, DAOS system group, container label, chunk size, file and directory object classes, prefix, and destroy-on-finalize.
- Global handles `poh`, `coh`, and `dfs` represent DAOS pool, container, and DFS mount state.
- `HandleDistribute` broadcasts pool/container/DFS global handles from rank 0 to the rest of `testComm`.
- `parse_filename` splits object basename and parent directory path, resolving relative directory paths with `realpath`.
- `lookup_insert_dir` caches opened DFS directory handles in a `d_hash_table`.
- `DFS_Create`, `DFS_Open`, `share_file_handle`, and `DFS_Xfer` wrap `dfs_open`, global file-handle sharing, `dfs_write`, and `dfs_read`.
- Metadata operations use `dfs_remove`, `dfs_mkdir`, `dfs_move`, `dfs_access`, `dfs_stat`, and DAOS pool space queries.

## Control Flow
`DFS_check_params` validates pool/container and initializes `testComm` if needed. `DFS_Init` is reference-counted with `dfs_init_count`: the first initialization calls `daos_init`, resolves object-class names, creates a directory-handle cache, connects or creates the container on rank 0, mounts DFS, distributes global handles, and applies a DFS prefix. Later initializations only refresh mutable object-class options. File create/open is done on all ranks for file-per-process or on rank 0 for shared-file mode, then shared through a DAOS global object handle. Finalization waits at MPI barriers, releases cached directory handles, unmounts DFS, closes or destroys the container, disconnects the pool, and calls `daos_fini`.

## State and Persistence
The DAOS container stores all persistent data. Runtime state is global and process-wide: pool/container/mount handles, object classes, cached directory object handles, and init count. `DFS_Fsync` and `DFS_Sync` call `dfs_sync`; comments note DFS has no client cache in this context.

## Dependencies and Integration Points
Requires DAOS, DFS, GURT hash/list utilities, MPI, and IOR utility macros. Integration includes IOR transfer hints, `testComm`, `rank`, mdtest callbacks, and `get_version` returning `"DAOS"`.

## Risks and Edge Cases
- Error macros jump to an `out` label, so each function's local cleanup path is central to correctness.
- `parse_filename` uses `realpath` for relative parent directories, which fails if the parent path does not exist locally even though DFS paths may not be local POSIX paths.
- Directory-handle cache uses `D_HASH_FT_NOLOCK`; thread safety depends on IOR calling patterns.
- `DFS_Open` sets `mode = S_IFREG | flags`, which mixes open flags into a mode variable.
- Shared file handles rely on correct rank-0 object creation/opening and MPI broadcasts.
- Finalization resets option fields, which may surprise code reusing the options object after finalize.

## Test Signals
Run DAOS DFS tests for existing and missing containers, destroy-on-finalize, object-class names, prefix use, file-per-process vs shared-file handle distribution, mkdir/rename/rmdir/stat/access, statfs pool-space reporting, and repeated initialize/finalize cycles.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-DFS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-DUMMY.c -->
# sources/test-tools/ior/src/aiori-DUMMY.c

## Purpose
Provides a synthetic IOR backend that performs no real I/O and optionally sleeps in create, close, sync, and transfer callbacks. It is useful for benchmarking framework overhead, scheduling, and delay behavior.

## Important APIs, Types, and Functions
- `dummy_options_t` stores microsecond delays and whether delays apply only to rank 0.
- `DUMMY_options` allocates backend options and exposes `dummy.delay-create`, `dummy.delay-close`, `dummy.delay-sync`, `dummy.delay-xfer`, and `dummy.delay-only-rank0`.
- `DUMMY_Create` and `DUMMY_Open` return synthetic monotonically increasing pointer values from static `current`.
- `DUMMY_Xfer` returns the requested length after optional delay.
- Metadata functions return success or trivial statfs values; file size is always zero.
- `DUMMY_init` and `DUMMY_final` track `count_init` and warn on lifecycle events.

## Control Flow
The backend requires `DUMMY_init` before create/open and errors if `count_init <= 0`. Delay helper logic is repeated in create, close, sync, and xfer, using `nanosleep` with microsecond option values. Close does not free handles because handles are fabricated pointer values.

## State and Persistence
No persistent state is created. Runtime state is global: synthetic pointer cursor and init count. The backend intentionally does not store file contents or metadata.

## Dependencies and Integration Points
Depends only on standard C/POSIX time functions plus IOR globals and logging. It registers a full mdtest-capable `ior_aiori_t dummy_aiori`.

## Risks and Edge Cases
- Pointer arithmetic on `char *current` fabricates invalid addresses; they must never be dereferenced by generic code.
- Delay conversion assumes microseconds and splits to seconds/nanoseconds.
- Metadata always succeeds, which can mask caller assumptions about real filesystem behavior.
- `DUMMY_Open` has no open delay, unlike create.

## Test Signals
Test lifecycle misuse, rank-0-only delays under MPI, elapsed time for each delay knob, verbose logging, and mdtest behavior with fabricated success responses.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-DUMMY.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-FINCHFS.c -->
# sources/test-tools/ior/src/aiori-FINCHFS.c

## Purpose
Implements a thin IOR backend for FINCHFS with transfer, metadata, rename, fsync, version, and mdtest support.

## Important APIs, Types, and Functions
- `struct FINCHFS_File` wraps an integer FINCHFS descriptor.
- `struct finchfs_option` contains `chunk_size`; `FINCHFS_options` calls `finchfs_set_chunk_size` when nonzero.
- `FINCHFS_initialize` and `FINCHFS_finalize` call `finchfs_init(NULL)` and `finchfs_term()`.
- File operations wrap `finchfs_create`, `finchfs_open`, `finchfs_pwrite`, `finchfs_pread`, `finchfs_close`, `finchfs_unlink`, and `finchfs_fsync`.
- Metadata operations wrap `finchfs_mkdir`, `finchfs_rename`, `finchfs_rmdir`, and `finchfs_stat`; statfs is a stub success path.

## Control Flow
The backend mirrors CHFS: dry-run returns success without backend calls, create/open allocate a descriptor wrapper, transfers return backend byte counts, close frees the wrapper, and sync is a no-op.

## State and Persistence
Persistent data lives in FINCHFS. Runtime state is a global hints pointer and per-file descriptor wrapper. Durability is available through `finchfs_fsync`; there is no global sync implementation.

## Dependencies and Integration Points
Requires `<finchfs.h>` and IOR callback integration. `enable_mdtest = true`; rename support is registered, unlike CHFS.

## Risks and Edge Cases
- Statfs reports success without filling fields.
- Transfer short counts are not retried locally.
- `chunk_size` is declared as an option flag despite being a size.
- `FINCHFS_access` ignores the requested access mode and only stats the path.

## Test Signals
Validate create/open/xfer/close/delete, rename, dry-run behavior, chunk-size option, fsync behavior, and mdtest metadata paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-FINCHFS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-Gfarm.c -->
# sources/test-tools/ior/src/aiori-Gfarm.c

## Purpose
Implements an IOR backend for Gfarm using `gfs_pio_*` file APIs and Gfarm metadata/statfs functions.

## Important APIs, Types, and Functions
- `struct gfarm_file` wraps `GFS_File`.
- `Gfarm_initialize`/`Gfarm_finalize` call `gfarm_initialize` and `gfarm_terminate`.
- `Gfarm_create`, `Gfarm_open`, `Gfarm_xfer`, `Gfarm_close`, `Gfarm_delete`, and `Gfarm_fsync` wrap Gfarm PIO functions.
- `Gfarm_xfer` seeks once, then chunks transfers with a maximum request size of 1 GiB.
- Metadata callbacks convert `gfs_stat`, `gfs_statfs_by_path`, `gfs_mkdir`, and `gfs_rmdir` results into IOR/POSIX-like responses.

## Control Flow
After hints and initialization, create/open allocate a wrapper around the Gfarm file handle. Transfers seek to the requested offset and loop until the requested length is consumed, using `gfs_pio_write` or `gfs_pio_read`. Delete maps Gfarm errors to `errno` but does not fatal-error on unlink failure.

## State and Persistence
Gfarm stores persistent data. Runtime state is limited to global hints and per-file `GFS_File` wrappers. `Gfarm_sync` is a no-op because the code treats libgfarm as having no relevant client cache; per-file sync uses `gfs_pio_sync`.

## Dependencies and Integration Points
Requires `<gfarm/gfarm.h>`, undefines Gfarm package macros to avoid conflicts, and registers mdtest support. There are no backend-specific command-line options.

## Risks and Edge Cases
- Transfer loop calculates `sz` once, so if `len > 1 GiB`, subsequent iterations still request the original capped size even when `rem` becomes smaller.
- Access ignores requested mode and only checks existence via stat.
- Stat conversion fills uid/gid with local process ids rather than Gfarm metadata.
- Delete errors only set `errno`; callers relying on fatal delete failure may miss it.

## Test Signals
Exercise large transfers around the 1 GiB cap, dry-run paths, fsync, stat/statfs conversion, mkdir/rmdir/access, and error propagation for missing files.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-Gfarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-HDF5.c -->
# sources/test-tools/ior/src/aiori-HDF5.c

## Purpose
Implements the IOR `HDF5` backend using parallel HDF5 over MPI-IO. It stores benchmark transfers in generated HDF5 datasets and maps IOR offsets to HDF5 hyperslabs.

## Important APIs, Types, and Functions
- `HDF5_options_t` embeds `mpiio_options_t` and adds collective metadata, individual dataset flag, no-fill, alignment, and dataset chunk-size options.
- `aiori_h5fd_t` stores HDF5 file id, transfer property list, dataset/data-space ids, and read-check/dataset lifecycle flags.
- `HDF5_Open` configures file creation/access property lists, MPI-IO hints, alignment, optional collective metadata, transfer mode, memory dataspace, and initial dataspace shape.
- `HDF5_Xfer` decides when to create/open the next dataset and performs `H5Dwrite` or `H5Dread`.
- `SetupDataSet` creates or opens dataset names like `Dataset-0000.0000`, applies chunking and no-fill options, and obtains file dataspace.
- `SeekOffset` maps IOR offsets into a one-dimensional hyperslab selection.
- Metadata helpers use native VOL checks where available and otherwise route to MPIIO/POSIX helpers.

## Control Flow
`HDF5_init_xfer_options` stores hints and also initializes MPIIO hints because HDF5 reuses MPIIO helpers. Create delegates to open. Open establishes the HDF5 file and memory transfer layout. Each xfer may roll to a new dataset at segment boundaries; read-check toggles avoid opening and closing the dataset twice for the two check passes. Close tears down dataset, dataspaces, transfer property list, file id, and wrapper.

## State and Persistence
Persistent data is the HDF5 file containing one or more generated datasets. Runtime state includes global hints, per-file HDF5 IDs, and a static dataset suffix in `SetupDataSet`. `HDF5_Fsync` calls `H5Fflush` with local scope. `HDF5_Finalize` calls `H5close`.

## Dependencies and Integration Points
Requires HDF5, MPI, IOR MPIIO helpers, POSIX metadata helpers, and optional HDF5 feature macros such as collective metadata, `H5Fdelete`, `H5Fis_accessible`, and VOL APIs.

## Risks and Edge Cases
- `individualDataSets` is rejected by `HDF5_check_params`, but dead code for it remains.
- Dataset suffix is static and reset only for newly opened files; concurrent/multiple handles could interact unexpectedly.
- `HDF5_Close` assumes dataset/file dataspace were created unless dry-run is set.
- Non-native VOL connectors lack statfs, mkdir, rmdir, stat, and file-size support in this backend.
- Error handling often calls `exit`, which can bypass MPI-coordinated shutdown.

## Test Signals
Run with parallel HDF5, independent and collective transfers, hints display, alignment/no-fill/chunk options, segment rollover producing multiple datasets, read-check double pass, native vs non-native VOL metadata helpers, and delete with and without `H5Fdelete`.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-HDF5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-HDFS.c -->
# sources/test-tools/ior/src/aiori-HDFS.c

## Purpose
Implements the IOR `HDFS` backend using libhdfs. It manages a per-options HDFS filesystem connection, file create/open/read/write/flush/close/delete, and metadata callbacks.

## Important APIs, Types, and Functions
- `hdfs_options_t` stores user, name node, replication count, direct-I/O flag, block size, runtime `hdfsFS`, and name-node port.
- `HDFS_options` initializes defaults from `$USER` and `"default"` name node.
- `hdfs_connect` builds a new forced HDFS client instance and stores it in `o->fs`.
- `HDFS_Create_Or_Open` maps IOR flags to libhdfs flags, coordinates shared-file truncation with MPI barriers, and calls `hdfsOpenFile`.
- `HDFS_Xfer` loops over `hdfsWrite` or `hdfsPread`, retries short transfers, and flushes writes with `hdfsHFlush` at the end.
- `HDFS_Fsync` uses `hdfsHSync`; metadata uses `hdfsCreateDirectory`, `hdfsDelete`, `hdfsExists`, `hdfsGetPathInfo`, and capacity APIs.

## Control Flow
Every metadata and file path first ensures the HDFS connection exists. Shared-file write create/open lets rank 0 truncate, then uses MPI barriers so other ranks open afterward. Writes use stream-positioned `hdfsWrite`; reads use positional `hdfsPread`. Close closes only the file handle; disconnect is implemented but not registered in `ior_aiori_t`.

## State and Persistence
Persistent state is in HDFS. Runtime connection state is stored in the allocated module options, not a global. Durability/visibility comes from `hdfsHFlush` after writes and `hdfsHSync` during fsync.

## Dependencies and Integration Points
Requires libhdfs, MPI barriers, IOR hints, and POSIX flag constants. It registers mdtest-capable metadata operations but no initialize/finalize callbacks.

## Risks and Edge Cases
- The connection is not finalized through the `ior_aiori_t`, so `hdfs_disconnect` may not be called by normal backend lifecycle.
- `IOR_RDWR` is unsupported and fatal.
- Direct I/O depends on `O_DIRECT` availability and may only affect client-side flags.
- `HDFS_GetFileSize` declares MPI aggregation variables but returns only the local `hdfsGetPathInfo` size.
- `HDFS_stat` maps HDFS permissions directly into `st_mode` without file-type bits.

## Test Signals
Test default/user/name-node options, shared-file truncation barriers, file-per-process writes, short read/write retry behavior, flush/fsync visibility, metadata callbacks, direct-I/O flag handling, and cleanup of HDFS client connections in long-running processes.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-HDFS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-IME.c -->
# sources/test-tools/ior/src/aiori-IME.c

## Purpose
Implements the IOR `IME` backend for DDN Infinite Memory Engine native APIs, including optional direct I/O, transfers, metadata, statfs, mknod, sync, and mdtest support depending on native API version.

## Important APIs, Types, and Functions
- `ime_options_t` stores `direct_io`; `IME_Options` exposes `ime.odirect`.
- `IME_Initialize` and `IME_Finalize` guard `ime_native_init`/`ime_native_finalize` with a boolean.
- `IME_Open` maps IOR flags to native open flags and optionally sets direct I/O.
- `IME_Xfer` loops over `ime_native_pwrite` or `ime_native_pread`, handles partial transfers, and optionally fsyncs per write.
- `IME_Fsync`, `IME_Close`, `IME_Delete`, `IME_GetFileSize`, and `IME_Stat` wrap native calls.
- API-version gates enable statfs/mkdir/rmdir for version >= 130 and mknod/sync for version >= 132.

## Control Flow
Create delegates to open. Transfers are positional, retry short transfers up to `MAX_RETRY`, and abort MPI when `singleXferAttempt` is set. Finalization is idempotent by `ime_initialized`.

## State and Persistence
Persistent data lives in IME. Runtime state is a global hints pointer, a global initialization boolean, and per-open heap-allocated integer descriptors. Fsync and sync are explicit native calls.

## Dependencies and Integration Points
Requires `ime_native.h`, IOR utilities, MPI globals, and POSIX-like flags. Registers both current name `IME` and legacy name `IM`.

## Risks and Edge Cases
- `IME_Xfer` does not check write `rc < 0` before partial-transfer logic, so negative write errors reach assertions after warning logic.
- Direct I/O relies on shared `set_o_direct_flag`.
- Metadata support depends heavily on `IME_NATIVE_API_VERSION`; older builds return warnings and failures for statfs/mkdir/rmdir/sync/mknod.
- `IME_GetVersion` returns a static buffer overwritten on each call.

## Test Signals
Build/test across native API versions, direct I/O, partial transfer retry/abort, fsync-per-write, initialization idempotence, statfs/mkdir/rmdir gates, mknod/sync gates, and mdtest operations.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-IME.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-LIBNFS.c -->
# sources/test-tools/ior/src/aiori-LIBNFS.c

## Purpose
Implements an IOR backend for libnfs user-space NFS, mounting an RFC2224 URL and translating IOR callbacks to synchronous libnfs operations.

## Important APIs, Types, and Functions
- Global `nfs_context` and `nfs_url` hold the mounted NFS session.
- `Map_IOR_Open_Flags_To_LIBNFS_Flags` maps IOR open flags to POSIX/libnfs flags.
- `LIBNFS_Initialize` creates context, parses `libnfs.url`, and mounts server/path.
- `LIBNFS_Open` uses `nfs_open`; `LIBNFS_Create` uses `nfs_open2` with a mode.
- `LIBNFS_Xfer` seeks with `nfs_lseek`, then uses `nfs_write` or `nfs_read`.
- Metadata wraps `nfs_mkdir2`, `nfs_rmdir`, `nfs_stat64`, `nfs_statvfs64`, `nfs_access`, and `nfs_unlink`.

## Control Flow
Options are allocated by `LIBNFS_GetOptions`. Initialization is a no-op if context or URL already exists. Transfers are seek-then-sequential-operation, returning the backend byte count. Finalize destroys context and parsed URL.

## State and Persistence
Persistent state is on the NFS server. Runtime state is global context/url plus libnfs file handles returned directly as `aiori_fd_t *`. Fsync delegates to `nfs_fsync`; there is no backend-wide sync.

## Dependencies and Integration Points
Requires `<nfsc/libnfs.h>`, `aiori-LIBNFS.h`, IOR utilities, and mdtest callbacks. The header defines only the `libnfs_options_t` URL field used by this implementation.

## Risks and Edge Cases
- No dry-run checks despite storing transfer hints.
- Global context means multiple option sets or parallel backend instances cannot mount different URLs in one process.
- `LIBNFS_Stat` returns `ENOENT` positive for missing paths rather than `-1` with `errno`, which differs from POSIX-style callbacks.
- Transfers do not retry short reads/writes and do not implement fsync-per-write.
- `IOR_EXCL` is not mapped.

## Test Signals
Test URL parsing/mount failures, open/create flag mapping, seek mismatch detection, short transfer reporting, stat/statfs field mapping, mkdir/rmdir with trailing slash, access return conventions, and finalize/reinitialize cycles.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-LIBNFS.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-LIBNFS.h -->
# sources/test-tools/ior/src/aiori-LIBNFS.h

## Purpose
Defines the small public options structure used by the libnfs IOR backend.

## Important APIs, Types, and Functions
- Include guard `_AIORI_LIBNFS_H`.
- `libnfs_options_t` contains `char *url`, the RFC2224 NFS URL consumed by `LIBNFS_Initialize` in `aiori-LIBNFS.c`.

## Control Flow
This header has no executable control flow. It is included by the libnfs backend so option allocation and callback initialization share the same structure layout.

## State and Persistence
No state is stored in the header itself. The `url` pointer is runtime configuration owned by the allocated backend options object.

## Dependencies and Integration Points
Integrated directly with `aiori-LIBNFS.c` option parsing. It does not include other headers, so consumers must include required definitions separately.

## Risks and Edge Cases
- The struct has no ownership annotation for `url`; callers must know whether option parsing stores borrowed or allocated strings.
- The header does not declare backend functions, only options.

## Test Signals
Compile the libnfs backend and verify option allocation, initialization, and URL parsing use the same `libnfs_options_t` layout.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-LIBNFS.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-MMAP.c -->
# sources/test-tools/ior/src/aiori-MMAP.c

## Purpose
Implements an IOR backend that performs transfers through a shared `mmap` mapping while reusing POSIX create/open/close/delete/file-size support.

## Important APIs, Types, and Functions
- `mmap_options_t` stores the active mapping pointer plus `madv_dont_need` and `madv_pattern` flags.
- `MMAP_options` exposes madvise controls.
- `MMAP_xfer_hints` stores hints and forwards them to `POSIX_xfer_hints`.
- `MMAP_Create` calls `POSIX_Create`, truncates to `hints->expectedAggFileSize`, and maps the file.
- `MMAP_Open` maps an existing POSIX-opened file.
- `MMAP_Xfer` copies to or from `o->mmap_ptr + offset` and optionally `msync`s per write.
- `MMAP_Close` unmaps and delegates to `POSIX_Close`.

## Control Flow
The backend uses POSIX for descriptor lifecycle, then maps the full expected aggregate size with `MAP_SHARED`. Transfer calls are simple memory copies; fsync is `msync` over either the transfer range or full mapping.

## State and Persistence
Persistent data is the underlying file. Runtime mapping state is stored in module options, so one options object effectively tracks one active mapping pointer. Durability is controlled by `msync` and POSIX close behavior.

## Dependencies and Integration Points
Requires POSIX backend declarations, `sys/mman.h`, IOR expected aggregate file size hints, and POSIX metadata helpers. It does not register mdtest metadata callbacks beyond remove/file-size.

## Risks and Edge Cases
- Pointer arithmetic on `void *` is a compiler extension; strictly conforming C would require a `char *` cast.
- Mapping size comes from `expectedAggFileSize`; incorrect planning can cause out-of-bounds transfer copies.
- Per-write sync requires transfer size page alignment by `MMAP_check_params`.
- Storing mapping pointer in options can break if one options object is used for multiple concurrent open files.

## Test Signals
Test create truncation size, read/write correctness through mapping, full and per-write `msync`, madvise random/sequential/DONTNEED options, page-alignment validation, and multiple file handles sharing one options object.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-MMAP.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-MPIIO.c -->
# sources/test-tools/ior/src/aiori-MPIIO.c

## Purpose
Implements the IOR `MPIIO` backend with MPI file handles, optional MPI_Info hints, preallocation, explicit-offset transfers, collective I/O, and optional MPI file views/datatypes for strided patterns.

## Important APIs, Types, and Functions
- `mpiio_fd_t` stores `MPI_File` and derived datatypes for transfer/file views.
- `MPIIO_options` exposes hints file, show-hints, preallocate, use-strided-datatype, and use-file-view options.
- `MPIIO_Open` maps IOR flags to MPI modes, selects communicator, applies hints, opens/truncates, optionally preallocates, and creates datatypes/file views.
- Count-wrapper functions provide `MPI_Count` compatibility where native `_c` APIs are unavailable.
- `MPIIO_Xfer` selects read/write function pointers for independent/collective and explicit/file-view transfers, checks transferred bytes, and retries short noncollective transfers.
- `SeekOffset` converts absolute IOR offsets to file-view offsets.
- `MPIIO_GetFileSize`, `MPIIO_Access`, `MPIIO_Delete`, and `MPIIO_Fsync` provide shared helpers used by HDF5 and NCMPI.

## Control Flow
Parameter validation rejects unsupported or incompatible combinations such as shared file pointers, random offsets with collective I/O, and large file-view segments on small `MPI_Aint`. Open configures state based on `filePerProc`, `collective`, and file-view options. Transfer either calls explicit-offset `MPI_File_*_at[_all]` or sets/seeks a file view and uses individual file pointers.

## State and Persistence
Persistent state is the MPI-IO target file. Runtime state is global hints plus per-file MPI handles and datatypes. Fsync calls `MPI_File_sync`; close frees derived datatypes when file views were used.

## Dependencies and Integration Points
Requires MPI and IOR utility functions `SetHints`/`ShowHints`. Provides helpers referenced by HDF5 and NCMPI and registers POSIX metadata helpers for statfs/mkdir/rmdir/stat.

## Risks and Edge Cases
- `MPI_MODE_UNIQUE_OPEN` is always set, which assumes no concurrent non-MPI openers.
- Strided datatype mode overloads `length` as a segment count and can return a synthetic transfer size for skipped offsets.
- Collective short-transfer retry is intentionally disabled; caller must handle short byte counts.
- Shared file pointer code is present but rejected/unfinished.
- `MPIIO_Delete` ignores delete errors.

## Test Signals
Run independent and collective I/O, file-per-process and shared-file modes, hints show/pass-through, preallocation, truncation, file-view and strided-datatype options, short-transfer behavior, dry-run paths, and helper use from HDF5/NCMPI.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-MPIIO.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-NCMPI.c -->
# sources/test-tools/ior/src/aiori-NCMPI.c

## Purpose
Implements the IOR `NCMPI` backend for Parallel NetCDF, storing IOR transfers in a NetCDF variable and using MPI-IO helpers for file size and access checks.

## Important APIs, Types, and Functions
- `ncmpi_options_t` embeds `mpiio_options_t` and tracks runtime `var_id`, `firstReadCheck`, and `startDataSet`.
- `NCMPI_options` exposes MPI-IO-like hints/preallocate/file-view options.
- `NCMPI_Create` and `NCMPI_Open` call `ncmpi_create`/`ncmpi_open` over `testComm`.
- `NCMPI_Xfer` defines dimensions and variable `data_var`, switches independent data mode when needed, maps offsets to `[segment][transfer][byte]`, and uses collective or independent vara calls.
- `GetFileMode` maps IOR flags to NetCDF flags and enables `NC_64BIT_DATA`.
- `NCMPI_GetFileSize` and `NCMPI_Access` delegate to MPIIO helpers.

## Control Flow
Hints are forwarded to MPIIO via `NCMPI_xfer_hints`. On the first write at a segment start, the backend defines dimensions and `data_var`, ends define mode, and stores the variable id. Reads look up the same variable. Each transfer computes segment and transfer indices from the absolute IOR offset.

## State and Persistence
Persistent state is a Parallel NetCDF file with an unlimited segment dimension and `data_var`. Runtime state lives partly in the options object (`var_id` and read-check toggles), plus a heap-allocated integer NetCDF file id.

## Dependencies and Integration Points
Requires PnetCDF, MPI, MPIIO helper functions, and POSIX metadata helpers. It registers no explicit `check_params`, so incompatible MPIIO-style options may not be validated here.

## Risks and Edge Cases
- Runtime dataset state is stored in backend options, which can conflict across multiple simultaneously open files.
- Options for preallocate/useFileView/useStridedDatatype are exposed but not applied by NCMPI transfer logic.
- `offsets[0]` uses `rank`, not `(rank + rankOffset) % numTasks`, while segment-position checks use rank offset.
- Independent mode begins but there is no explicit matching end before close in this file.

## Test Signals
Test file creation/open, collective and independent transfers, read-check toggling, rank-offset layouts, file-size/access delegation, large variable support, hints display, and multiple open files using separate option instances.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-NCMPI.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-PMDK.c -->
# sources/test-tools/ior/src/aiori-PMDK.c

## Purpose
Implements a low-level PMDK/libpmem backend for IOR using persistent-memory mapped files. It is restricted to file-per-process workloads.

## Important APIs, Types, and Functions
- `pmdk_aiori` registers PMDK create/open/xfer/close/delete/fsync/file-size callbacks and POSIX metadata helpers.
- `PMDK_Create` maps a new persistent-memory file with `pmem_map_file` using `PMEM_FILE_CREATE | PMEM_FILE_EXCL`.
- `PMDK_Open` maps an existing file with `pmem_map_file`.
- `PMDK_Xfer` writes with `pmem_memcpy_persist` or `pmem_memcpy_nodrain` depending on `fsyncPerWrite`, and reads with `memcpy`.
- `PMDK_Fsync` drains pending PMDK stores with `pmem_drain`.
- `PMDK_Delete` unlinks the backing file; `PMDK_GetFileSize` stats it.

## Control Flow
Create/open abort the MPI job if `hints->filePerProc` is false or if the mapped file is not detected as persistent memory. Transfer treats the `aiori_fd_t *` as the mapped address and applies byte offsets directly.

## State and Persistence
Persistent state is the pmem-backed file. Runtime state is global hints and mapped-address handles. Writes are persistent immediately with `pmem_memcpy_persist`, or require later drain when using no-drain per-write mode.

## Dependencies and Integration Points
Requires libpmem, MPI, IOR hints, and POSIX metadata helpers. `enable_mdtest = false`, reflecting that the backend is data-transfer oriented.

## Risks and Edge Cases
- `PMDK_Close` unmaps only `hints->transferSize`, while create/open map `blockSize * segmentCount`; that risks incomplete unmap.
- File-per-process restriction is enforced at runtime by MPI abort.
- `PMDK_Xfer` indexes `file[offset_size]` on `aiori_fd_t *`; correctness depends on this pointer being byte-addressable as returned from `pmem_map_file`.
- No dry-run handling.

## Test Signals
Run only on real or emulated pmem, validate file-per-process enforcement, mapping length/unmap correctness, persistence with and without `fsyncPerWrite`, file-size checks, and delete behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-PMDK.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-POSIX.c -->
# sources/test-tools/ior/src/aiori-POSIX.c

## Purpose
Implements the primary POSIX IOR backend, including open/create/read/write/close/delete/sync, direct I/O, optional Lustre/BeeGFS/GPFS/GPU Direct tuning, range locks, and mdtest metadata integration.

## Important APIs, Types, and Functions
- `posix_fd` wraps a POSIX fd and optional `CUfileHandle_t`.
- `posix_options_t` is defined in `aiori-POSIX.h` and includes direct I/O, Lustre striping/pool, GPFS hints, BeeGFS striping, GPU Direct, and range lock controls.
- `POSIX_options` exposes command-line options conditionally by compile-time feature macros.
- `POSIX_check_params` validates BeeGFS chunk size, Lustre pool/stripe combinations, and GPU Direct requirements.
- `POSIX_Create` maps options to `open64`, `llapi_file_open*`, Lustre ioctl striping, BeeGFS file creation, GPFS hints, and GPU Direct registration.
- `POSIX_Open` opens existing files with requested access and optional tuning.
- `POSIX_Xfer` performs seek, optional range lock, read/write or cuFileRead/cuFileWrite loops, short-transfer retry logic, fsync-per-write, and GPFS access hints.
- `POSIX_Fsync`, `POSIX_Sync`, `POSIX_Close`, `POSIX_Delete`, `POSIX_Rename`, and `POSIX_GetFileSize` provide lifecycle and metadata operations.

## Control Flow
IOR initializes/finalizes GPU Direct driver when compiled. Create has specialized paths for Lustre striping and BeeGFS file creation before falling back to `open64(O_CREAT|O_RDWR)`. Shared-file Lustre creation uses MPI barriers so rank 0 creates/stripes before other ranks open. Transfers seek to the requested offset and loop until all bytes are moved or retry limits/short reads stop progress.

## State and Persistence
Persistent state is the POSIX-visible filesystem. Runtime state is global hints plus per-open `posix_fd`. Durability is through `fsync` or `system("sync")`. Optional GPFS/Lustre/BeeGFS/GPU Direct settings affect filesystem/client behavior rather than IOR-owned persistent metadata.

## Dependencies and Integration Points
Requires POSIX, optional GPFS headers, BeeGFS headers, Lustre user/API headers, CUDA/cuFile, MPI, and IOR utility helpers. Other backends reuse POSIX helpers directly, notably MMAP, PMDK metadata, HDF5 metadata, MPIIO metadata, and NCMPI metadata.

## Risks and Edge Cases
- `POSIX_Fsync` casts the argument to `posix_fd *`, but `POSIX_Xfer` passes `&fd` when fsync-per-write is set; that is a type mismatch risk.
- `system("sync")` is global and shell-dependent.
- Range locks are released only after the transfer loop; early returns on read/write errors can skip unlock and GPFS access-end hints.
- Feature-specific paths are compile-time-dependent and hard to cover in one build.
- GPU Direct errors are warned during handle registration but later transfer paths may still try cuFile operations.

## Test Signals
Test basic POSIX read/write/delete/rename/stat, dry-run, direct I/O alignment, fsync-per-write, short read/write behavior, range locks including error paths, Lustre/BeeGFS/GPFS feature builds, GPU Direct builds, shared-file creation barriers, and helper callers such as MMAP/HDF5/MPIIO/NCMPI.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-POSIX.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-POSIX.h -->
# sources/test-tools/ior/src/aiori-POSIX.h

## Purpose
Declares POSIX backend options and public helper functions used by the POSIX backend and by other IOR backends that delegate to POSIX for metadata or file lifecycle.

## Important APIs, Types, and Functions
- `posix_options_t` contains direct-I/O, Lustre, GPFS, BeeGFS, GPU Direct, and range-lock configuration fields.
- Lustre pool-name limit is selected from Lustre headers when available, otherwise a fallback value is used.
- Function declarations include `POSIX_Create`, `POSIX_Open`, `POSIX_Close`, `POSIX_Delete`, `POSIX_Rename`, `POSIX_Fsync`, `POSIX_Sync`, `POSIX_Mknod`, `POSIX_GetFileSize`, `POSIX_options`, `POSIX_check_params`, and `POSIX_xfer_hints`.

## Control Flow
The header has no executable control flow. Its declarations allow MMAP to reuse POSIX lifecycle functions and allow other modules to call POSIX metadata/file-size helpers through shared symbols.

## State and Persistence
No state is stored in the header. The layout of `posix_options_t` is runtime-significant because option allocation in `aiori-POSIX.c` and consuming modules cast `aiori_mod_opt_t *` to this type.

## Dependencies and Integration Points
Includes `aiori.h` and optional Lustre headers. Comments warn that MMAP depends on this option layout, especially the initial `direct_io` field.

## Risks and Edge Cases
- Duplicate `POSIX_check_params` declarations appear in the header.
- Changing `posix_options_t` layout can silently break MMAP or other casts.
- Feature-gated fields mean ABI/layout differs by build configuration.

## Test Signals
Compile all POSIX-dependent backends under feature combinations, validate no duplicate-prototype warnings become errors, and verify MMAP option compatibility after any struct changes.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-POSIX.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-RADOS.c -->
# sources/test-tools/ior/src/aiori-RADOS.c

## Purpose
Implements an IOR backend for Ceph RADOS objects. It maps IOR file names to RADOS object ids and provides object create/open, read/write, delete, size, and existence checks.

## Important APIs, Types, and Functions
- `RADOS_options_t` stores Ceph user, config file, and pool.
- Global `rados_cluster` and `rados_ioctx` represent the cluster connection and pool I/O context.
- `RADOS_check_params` requires user, conf, and pool.
- `RADOS_Initialize` creates/configures/connects the cluster and creates the pool ioctx.
- `RADOS_Create_Or_Open` duplicates the object id and optionally issues a create write op with exclusive or idempotent semantics.
- `RADOS_Xfer` uses librados write and read ops for positional object I/O.
- `RADOS_GetFileSize` stats an object with a read op; `RADOS_Access` uses stat to check existence.

## Control Flow
Initialization must precede file operations. Create/open returns a heap-allocated object id string as the handle. Close frees the object id. Delete issues a remove write operation. Fsync is a no-op because writes complete through librados operations.

## State and Persistence
Persistent state is in Ceph RADOS objects. Runtime state is global cluster/ioctx plus per-handle object id strings. There is no directory hierarchy or POSIX statfs/stat support.

## Dependencies and Integration Points
Requires `<rados/librados.h>`, IOR utilities, and Ceph configuration. Registered callbacks include unsupported mdtest-like metadata functions, but `enable_mdtest` is not set.

## Risks and Edge Cases
- Object names are raw test file names; path-like names are not directories.
- `RADOS_Access` uses bitwise `|` instead of logical `||` when checking errors.
- Read error reporting passes `ret` to `RADOS_ERR` even when `read_ret` or byte-count mismatch is the failing condition.
- Statfs, mkdir, rmdir, and stat are unsupported and always warn/fail.
- No dry-run path.

## Test Signals
Test missing option validation, cluster/pool connect failures, create exclusive vs idempotent behavior, positional reads/writes, size/existence checks, delete, unsupported metadata responses, and object names containing slashes.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-RADOS.c -->
