# subset-b-009237 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-S3-4c.c -->
# sources/test-tools/ior/src/aiori-S3-4c.c

## Purpose
Implements the legacy aws4c/libcurl S3 backend family for IOR: `S3-4c` for standard multipart-upload S3 semantics, `S3_plus` for S3 plus EMC extensions, and `S3_EMC` for EMC byte-range writes. It adapts IOR's abstract I/O table to object-store operations, including bucket setup, object create/open, ranged reads, multipart write assembly, pseudo-delete, and object size lookup.

## Important APIs, Types, And Functions
Defines `s3_options_t` with bucket/user/host options plus runtime `IOBuf` state, ETag accumulation, multipart `UploadId`, part numbering, curl flags, and written-state tracking. Registers `s3_4c_aiori`, `s3_plus_aiori`, and `s3_emc_aiori`. Key functions are `S3_options`, `S3_init`, `S3_finalize`, `S3_check_params`, `s3_connect`, `S3_Create_Or_Open_internal`, `S3_Xfer_internal`, `S3_Close_internal`, `S3_Delete`, `EMC_Delete`, and `S3_GetFileSize`.

## Control Flow
Initialization calls `aws_init`; first open/create lazily runs `s3_connect`, reads aws4c credentials, creates/reuses the bucket on rank 0, initializes `IOBuf` structures, and enables EMC extensions if requested. Create/open returns the object name cast as an `aiori_fd_t *`; for multipart writes, rank 0 initiates MPU for N:1 and broadcasts the `UploadId`. Transfers either upload parts and store ETags, perform EMC byte-range PUTs/appends, or issue ranged GETs expecting HTTP 206. Close finalizes MPU by gathering ETags to rank 0 for N:1, formatting `CompleteMultipartUpload` XML in correct segmented/strided order, posting completion, resetting MPU buffers, and synchronizing ranks. Deletes overwrite with a zero-length object because of documented EMC append/delete/recreate behavior.

## State And Persistence Behavior
The backend stores per-rank runtime state in `s3_options_t`, but it is explicitly not safe for concurrent access to multiple files. It persists benchmark data as S3 objects under a configured bucket and uses zero-length replacement instead of actual deletion. Multipart state is held in `UploadId`, `part_number`, and an accumulated ETag `IOBuf` until close. Rank synchronization via `testComm` controls bucket creation, UploadId sharing, MPU completion, and read-after-write visibility.

## Dependencies And Integration Points
Depends on aws4c/`aws4c_extra`, libcurl, libxml2, MPI globals `rank` and `testComm`, `aiori.h`, `ior.h`, and debug/error macros. IOR supplies transfer hints through `S3_xfer_hints`; `ior.c` invokes this backend through the `ior_aiori_t` hooks for create/open/xfer/close/remove/get_file_size/fsync.

## Risks And Edge Cases
`S3_Xfer` calls `S3_Xfer_internal` but does not return its value, which violates the `xfer` contract and can corrupt IOR's byte-count checks. The code depends on global `hints`; create/open dereferences it for N:1/N:N decisions. Standard S3 cannot append, and `S3_check_params` only rejects one N:1 strided case. Multipart part numbering starts at `0` in generated XML although S3 APIs commonly expect one-based part numbers. ETag gathering for large N:1 jobs can exhaust rank 0 memory and is constrained by S3 MPU part limits noted in comments. `UploadId` length check uses `>` instead of `>=` against the fixed buffer size. Pseudo-delete leaves buckets and zero-length objects behind.

## Test Signals
Useful signals include S3/EMC IOR write/read/check runs in file-per-process and shared-file modes, transfer-size equal and smaller than block-size, verbose MPU ETag output, HTTP status validation, final aggregate file-size checks in `ior.c`, and data verification failures from `WRITECHECK`/`READCHECK`. A focused unit or integration test should catch the missing return from `S3_Xfer`.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-S3-4c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-S3-curl.c -->
# sources/test-tools/ior/src/aiori-S3-curl.c

## Purpose
Provides a libcurl-based S3 backend named `S3-curl` for IOR and mdtest. It implements a simple object interface with configurable credentials, host, bucket, region, SSL, timeout, and certificate verification options.

## Important APIs, Types, And Functions
Defines `s3_curl_options_t`, `s3_curl_fd_t`, and `MemoryStruct`. Registers `s3_curl_aiori` with create/open/xfer/close/remove/stat/statfs/access/rename/sync hooks. Important helpers are `S3_curl_options`, `S3_curl_check_params`, `init_curl_handle`, `set_s3_url`, `S3_curl_Create`, `S3_curl_Xfer`, `S3_curl_GetFileSize`, `S3_curl_access`, and `S3_curl_stat`.

## Control Flow
`S3_curl_initialize`/`finalize` wrap libcurl global init and cleanup. Create validates options, allocates an fd, initializes a CURL easy handle, sets a PUT URL, sends a zero-length upload, and returns the fd on success. Open allocates an fd without validating remote existence. `S3_curl_Xfer` performs PUT for writes and GET for reads, checking libcurl result and HTTP status. Size and access are implemented with HEAD requests; stat synthesizes a POSIX `struct stat`; mkdir/rmdir/statfs/sync are mostly no-ops or dummy responses.

## State And Persistence Behavior
Each open fd owns a duplicated key and CURL handle. Data persists as S3 objects at `/{bucket}/{key}` on the chosen endpoint. There is no multipart state, buffering across transfers, append support, directory state, or local persistence. `hints` are stored globally but not used by this implementation.

## Dependencies And Integration Points
Uses libcurl, IOR `ior_aiori_t`, IOR logging globals, and `utilities.h`. It integrates with `aiori.c` when compiled under `USE_S3_CURL_AIORI` and with IOR's generic file lifecycle and size-check logic.

## Risks And Edge Cases
The implementation does not perform AWS Signature V4 signing; setting `CURLOPT_USERNAME` and `CURLOPT_PASSWORD` is insufficient for most S3 endpoints. Read handling is unsafe: `WriteMemoryCallback` reallocates `mem->memory`, but `S3_curl_Xfer` points it at the caller's transfer buffer, so it may realloc non-malloc memory, write beyond intended ownership, and returns the accumulated size rather than bytes copied. `ReadDataCallback` mutates the memory pointer and is unused for current write setup. The `offset` argument is ignored for both PUT and GET, so normal IOR multi-transfer files overwrite or reread whole objects rather than byte ranges. Header lists are not associated with fd lifetime but are freed after use; curl options may retain stale pointers until changed. `S3_curl_stat` treats zero-byte objects as missing.

## Test Signals
Run IOR with `-a S3-curl` against an S3-compatible test server for single-transfer whole-object writes first, then multi-transfer block-size larger than transfer-size to expose offset loss. Address sanitizer or valgrind should flag the GET realloc misuse. HEAD/access/stat tests should include zero-byte objects and missing keys.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-S3-curl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-S3-libs3.c -->
# sources/test-tools/ior/src/aiori-S3-libs3.c

## Purpose
Implements the `S3-libs3` IOR backend using the newer libs3 API. It maps files and directories to S3 buckets and objects, with a mode for one bucket per file/directory or a shared bucket containing object fragments.

## Important APIs, Types, And Functions
Defines `s3_options_t`, `S3_fd_t`, `data_handling`, and `s3_delete_req`. Registers `S3_libS3_aiori`. Main functions include `S3_options`, `def_file_name`, `def_bucket_name`, libs3 response callbacks, `S3_Create`, `S3_Open`, `S3_Xfer`, `S3_Delete`, `S3_mkdir`, `S3_rmdir`, `S3_stat`, `S3_access`, `S3_GetFileSize`, `S3_check_params`, `S3_init`, and `S3_final`.

## Control Flow
Options establish bucket naming, host/credentials, region/location, SSL, and S3-compatible behavior. Initialization optionally splits a host list by rank, initializes libs3, derives a bucket suffix from the access key, initializes `S3BucketContext`, and creates the shared bucket on rank 0. Create creates a bucket or zero-length object marker. Transfers write each IOR transfer as a separate object key based on file name, offset, and length, or read the matching object. Delete removes a per-file bucket or deletes the base object and matching fragments. Finalization deletes the shared bucket on rank 0 and deinitializes libs3.

## State And Persistence Behavior
Backend state lives in `s3_options_t`, including mutable `bucket_context`, selected host, and generated bucket prefix. File handles store the normalized object name. Data is persisted as many S3 objects when offsets are nonzero. Directory operations are represented by buckets or zero-length objects, not hierarchical filesystem metadata. Global `s3status` and `s3error` capture latest libs3 callback status.

## Dependencies And Integration Points
Uses libs3, MPI global `rank`, IOR's abstract backend table, debug warnings, and utilities. `S3_statfs` uses `S3_list_service`; `ior.c` relies on `get_file_size`, `stat`, `access`, mkdir/rmdir, and remove hooks for validation and cleanup. The backend is mdtest-enabled.

## Risks And Edge Cases
Global `s3status`/`s3error` are shared mutable state and can carry stale results if callbacks are not invoked as expected. The shared-bucket finalizer deletes the bucket on rank 0 regardless of whether objects remain, which can fail or surprise users. `S3_Xfer` always returns `length` even when libs3 reports an error in compatible mode. File size is incomplete for fragmented files because `S3_stat` has a TODO to sum fragment sizes. Object/bucket name construction can exceed fixed `FILENAME_MAX` buffers and loses or transforms characters. `S3_init` destructively tokenizes `host`, which may affect reused option defaults. Delete heuristics depend on `S3LIB_DELETE_HEURISTICS` and may miss fragments.

## Test Signals
Important coverage includes shared-bucket and bucket-per-file modes, multi-host rank selection, fragmented writes where transfer-size is smaller than block-size, delete with and without `S3LIB_DELETE_HEURISTICS`, stat/get_file_size after fragmented writes, and mdtest mkdir/rmdir/stat behavior against an S3-compatible endpoint.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-S3-libs3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-aio.c -->
# sources/test-tools/ior/src/aiori-aio.c

## Purpose
Provides an IOR backend named `AIO` that layers Linux native asynchronous I/O (`libaio`) over the existing POSIX backend. It batches transfers, keeps a pool of aligned buffers for asynchronous operations, and delegates filesystem metadata operations to POSIX helpers.

## Important APIs, Types, And Functions
Defines `aio_options_t` for POSIX sub-options, libaio context, pending iocbs, in-flight counts, pending bytes, and buffer pool state. Defines `aio_fd_t` wrapping a POSIX fd. Key functions are `aio_options`, `aio_initialize`, `aio_setup_pool`, `submit_pending`, `aio_reap_one`, `process_some`, `complete_all`, `aio_Xfer`, `aio_Close`, `aio_Fsync`, and `aio_Sync`. Registers `aio_aiori`.

## Control Flow
Initialization creates one `io_context_t` and allocates an iocb submission array sized by `granularity`. Open/create delegate to POSIX. For normal reads/writes, `aio_Xfer` ensures capacity, provisions a buffer pool, copies write data into a pooled buffer, prepares a pwrite/pread iocb, queues it, and submits when granularity is reached. When maximum in-flight operations is reached, it reaps some completions. For verification reads, it synchronizes all outstanding work and performs a blocking single AIO so the caller's buffer is immediately valid. Close/fsync/sync call `complete_all` before delegating.

## State And Persistence Behavior
Runtime state is in backend options and is shared by the backend instance: libaio context, in-flight counters, pending-byte accounting, and buffer pool. Data persistence is ordinary POSIX file persistence through the underlying POSIX fd. Read operations into the pool do not copy data back to the caller except in verification paths, so non-check read benchmarking measures completion of async reads without returning useful payload to IOR.

## Dependencies And Integration Points
Depends on `libaio`, POSIX AIORI functions from `aiori-POSIX.h`, aligned buffer utilities, and the IOR backend contract. It forwards xfer hints to POSIX, uses POSIX option parsing through `option_merge`, and reuses POSIX statfs/access/mkdir/rmdir/stat/remove/get_file_size.

## Risks And Edge Cases
`pending_bytes` is incremented for reads as well as writes and decremented by completion result; short I/O or errors are detected only at completion. Non-check reads never copy pooled read data into the caller's buffer, which is acceptable for pure throughput but surprising if a caller expects data. `io_submit` error handling uses `errno`, although libaio often returns negative errno values directly. The stack VLA in `complete_all`/`process_some` is bounded to 512 events but still depends on runtime values. `aio_check_params` enforces minimum max-pending and granularity constraints but not zero/negative granularity explicitly.

## Test Signals
Exercise AIO with write/read and write-check/read-check modes, direct/aligned POSIX options, `aio.max-pending` and `aio.granularity` boundary values, short file reads, fsync-per-write, and close/sync completion. Error injection for `io_submit`/`io_getevents` would validate pending-byte accounting and abort paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori-debug.h -->
# sources/test-tools/ior/src/aiori-debug.h

## Purpose
Defines shared logging, warning, error, and MPI-check macros used by IOR AIORI backends and core code. It centralizes output formatting to `out_logfile`, verbosity-aware diagnostics, warning-as-error behavior, and MPI abort-on-failure handling.

## Important APIs, Types, And Functions
Declares external `FILE *out_logfile`, `int verbose`, and `int aiori_warning_as_errors`, plus `FailMessage`. Macros include `FAIL`, `WARN_RESET`, `WARNF`, `WARN`, `INFOF`, `INFO`, `ERRF`, `ERR`, `MPI_CHECKF`, and `MPI_CHECK`.

## Control Flow
Warning macros print on rank/verbosity conditions and flush logs. `WARNF` escalates to `ERRF` when `aiori_warning_as_errors` is set. `ERRF` and MPI check failures print file/line context, flush, and call `MPI_Abort(MPI_COMM_WORLD, -1)`. `WARN_RESET` copies a default member value into a target struct member and reports the reset on rank 0.

## State And Persistence Behavior
No persistent state is owned here; behavior depends on global log file, verbosity, MPI rank, and warning policy. The macros synchronously flush log output before aborting or returning to callers.

## Dependencies And Integration Points
Requires MPI and stdio. Included by `aiori.h` and many backend implementations, so it affects error behavior across POSIX, S3, AIO, and core IOR validation paths.

## Risks And Edge Cases
Macros evaluate some arguments in formatted contexts and can be unsafe with side effects. `ERRF` always aborts `MPI_COMM_WORLD`, which may be broader than a per-test communicator. `WARN_RESET` assumes integer formatting for the reset member. `FAIL` depends on `rank` and `ERROR_LOCATION` being visible where used. Format-string mismatches are easy because these are variadic macros.

## Test Signals
Compiler warnings with format checking, forced MPI failure paths, warning-as-error runs, and validation warnings from `ValidateTests` confirm these macros behave as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori.c -->
# sources/test-tools/ior/src/aiori.c

## Purpose
Implements the registry and common helpers for IOR's abstract I/O interface. It selects available backends at compile time, exposes option metadata for all modules, provides API listing/default selection, and supplies generic POSIX-based statfs/mkdir/rmdir/access/stat fallbacks.

## Important APIs, Types, And Functions
Defines `available_aiori[]` gated by `USE_*_AIORI` macros. Exports `airoi_create_all_module_options`, `airoi_update_module_options`, `aiori_supported_apis`, `aiori_posix_statfs`, `aiori_posix_mkdir`, `aiori_posix_rmdir`, `aiori_posix_access`, `aiori_posix_stat`, `aiori_get_version`, `aiori_select`, `aiori_count`, and `aiori_default`.

## Control Flow
At startup or option parsing, callers can create a module option set for every compiled backend. `aiori_select` scans the registry for the requested canonical or legacy name, warns on legacy use, fills missing metadata hooks with POSIX fallbacks, and returns the backend function table. Supported API strings are built by iterating the registry and optionally filtering for mdtest-enabled backends.

## State And Persistence Behavior
The registry is static process state. `aiori_select` mutates backend function tables by installing fallback function pointers the first time a backend is selected. POSIX statfs derives the parent directory from a duplicated path and translates platform statfs/statvfs fields into `ior_aiori_statfs_t`.

## Dependencies And Integration Points
Depends on compile-time backend symbols declared in `aiori.h`, option structures from `option.h`, POSIX/statvfs or statfs headers, and debug warnings. It is used by command-line parsing and `init_IOR_Param_t`/`ValidateTests` in `ior.c`.

## Risks And Edge Cases
`airoi_update_module_options` indexes modules by walking both `available_aiori` and `opt->modules`; mismatched ordering would update the wrong module. Fallback mutation of global backend tables is convenient but can hide missing backend operations. `aiori_posix_statfs` returns early on statfs failure without freeing `fileName`. It sets `f_bavail` only in the `ior_aiori_statfs_t` struct definition, but this helper does not copy it. `aiori_default` can return `dummy_aiori` if it is the first compiled entry after unavailable optional backends.

## Test Signals
Compile matrices with different `USE_*_AIORI` macros, `-a` selection by canonical and legacy names, mdtest API listing, option help generation, and fallback stat/mkdir/access behavior for a backend with missing hooks are primary tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/aiori.h -->
# sources/test-tools/ior/src/aiori.h

## Purpose
Defines IOR's abstract I/O interface contract. It gives core benchmark code a uniform function table for different storage backends and declares backend selection, option, version, and POSIX fallback helpers.

## Important APIs, Types, And Functions
Defines IOR open/mode flags, `ior_aiori_statfs_t`, `aiori_xfer_hint_t`, opaque `aiori_mod_opt_t`, opaque `aiori_fd_t`, and the central `ior_aiori_t` function table. Declares all backend instances, `aiori_select`, `aiori_count`, `aiori_supported_apis`, `airoi_create_all_module_options`, `airoi_update_module_options`, `aiori_default`, generic POSIX helper functions, and reusable MPIIO option/API declarations.

## Control Flow
Backends fill `ior_aiori_t` hooks for create/open/xfer/close/remove/get_file_size/stat/metadata/initialize/finalize/options/check/sync. `ior.c` selects one backend, sends transfer hints, and then calls these hooks through the test lifecycle. Optional hooks may be filled by `aiori.c` fallbacks.

## State And Persistence Behavior
The header owns no state. `aiori_xfer_hint_t` is the state-transfer structure from `IOR_param_t` to backends, carrying access pattern, sizes, aggregate expectations, fsync flags, and dry-run/single-xfer hints.

## Dependencies And Integration Points
Includes `iordef.h`, `aiori-debug.h`, `option.h`, stat definitions, and bool. It is included by core IOR, mdtest-aware backend code, and backend implementations. The `enable_mdtest` field is the integration switch for mdtest API listings.

## Risks And Edge Cases
The interface uses opaque structs that are cast to backend-specific types, so type safety is minimal. Many hooks are allowed to be NULL and later defaulted, which can surprise non-POSIX backends. Changing `mpiio_options_t` requires synchronized changes in dependent modules. The `xfer` contract returns bytes transferred, and backend violations directly affect IOR validation.

## Test Signals
ABI/compiler checks across all enabled backends, backend selection smoke tests, transfer-hint propagation tests, and mdtest API filtering validate this contract.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/aiori.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/ior-internal.h -->
# sources/test-tools/ior/src/ior-internal.h

## Purpose
Declares private cross-file interfaces for IOR's internal implementation, primarily connecting `ior.c` with output/reporting functions in `ior-output.c` and exposing random offset generation to helper code.

## Important APIs, Types, And Functions
Declares `PrintHeader`, `ShowTestStart`, `ShowTestEnd`, `ShowSetup`, repeat and summary printers, `GetTestFileName`, `PrintRemoveTiming`, `PrintReducedResult`, `PrintTestEnds`, `PrintTableHeader`, and `GetOffsetArrayRandom`. Defines `struct results` for summary min/max/mean/variance/stddev/value arrays.

## Control Flow
`ior.c` calls these declarations while running tests: header before tests, setup and table header at test start, reduced result rows after each operation, repeat/test endings, short and long summaries, and removal timing. `ior-output.c` consumes `IOR_test_t`, `IOR_param_t`, and `IOR_results_t` from `ior.h`.

## State And Persistence Behavior
No state is stored in the header. It exposes output functions that write to global `out_resultfile`/`out_logfile` and helper state inside `ior-output.c`.

## Dependencies And Integration Points
Requires prior visibility of `IOR_param_t`, `IOR_test_t`, and `IOR_offset_t`, normally through including `ior.h` before this header. It is an internal boundary and not a public API for external users.

## Risks And Edge Cases
The header lacks includes/forward declarations for its parameter types, making include order significant. `struct results` includes a flexible-style trailing pointer allocated by callers, so allocation and ownership must remain coordinated with `ior-output.c`.

## Test Signals
Full IOR build, output-format tests, and compilation of translation units that include this header through the expected include order are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/ior-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/ior-main.c -->
# sources/test-tools/ior/src/ior-main.c

## Purpose
Provides the standalone executable entry point for IOR.

## Important APIs, Types, And Functions
Includes `ior.h` and defines `main(int argc, char **argv)`, which returns `ior_main(argc, argv)`.

## Control Flow
All substantive startup, MPI initialization, parsing, execution, reporting, and cleanup are delegated to `ior_main` in `ior.c`.

## State And Persistence Behavior
No state is owned here. Process exit status is the return value from `ior_main`, typically based on total error count.

## Dependencies And Integration Points
Links the executable target to the reusable IOR library-style function `ior_main`. This allows the same implementation to be invoked from tests or other embedding code through `ior_run`/`ior_main`.

## Risks And Edge Cases
Any change to `ior_main` signature or ownership of MPI initialization must be reflected here. The file intentionally has no direct MPI handling, so standalone behavior depends entirely on `ior.c`.

## Test Signals
Executable startup smoke tests, `ior -h`/option parsing, and MPI launcher runs validate this wrapper.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/ior-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/ior-output.c -->
# sources/test-tools/ior/src/ior-output.c

## Purpose
Handles user-visible IOR output in default text, CSV, and JSON-like formats. It prints run headers, test setup, per-iteration reduced metrics, removal timing, short summaries, and long all-test summaries.

## Important APIs, Types, And Functions
Public functions include `PrintTableHeader`, `PrintKeyVal`, `PrintRepeatEnd`, `PrintRepeatStart`, `PrintTestEnds`, `PrintReducedResult`, `PrintHeader`, `ShowTestStart`, `ShowTestEnd`, `ShowSetup`, `PrintLongSummaryOneTest`, `PrintLongSummaryHeader`, `PrintLongSummaryAllTests`, `PrintShortSummary`, and `PrintRemoveTiming`. Internal helpers include `PrintNextToken`, section/array printers, `PrintKeyValDouble`, `PrintKeyValInt`, `bw_ops_values`, `bw_values`, `ops_values`, `PrintLongSummaryOneOperation`, `PPDouble`, and `mean_of_array_of_doubles`.

## Control Flow
Rank 0 prints the run header, begins a tests array/section, and for each test prints start metadata, filesystem size, options, and a results array. `ior.c` calls `PrintReducedResult` after MPI-reduced timings are available. Summaries compute per-repetition bandwidth and operations statistics from `IOR_results_t`. JSON output is managed by global indentation and comma-token state; CSV output emits flat rows; default output emits human-readable tables.

## State And Persistence Behavior
The file keeps static `indent` and `needNextToken` formatting state. It writes to global `out_resultfile` and sometimes `out_logfile`. It does not persist files itself except through caller-provided output streams; stonewalling status storage is triggered from `ShowTestEnd` through utility functions.

## Dependencies And Integration Points
Depends on `ior.h`, `ior-internal.h`, `utilities.h`, global `rank`, `verbose`, `outputFormat`, `out_resultfile`, `out_logfile`, and environment variables for verbose dumps. Calls `GetTestFileName`, `ShowFileSystemSize`, `HumanReadable`, `CurrentTimeString`, and stonewalling utilities.

## Risks And Edge Cases
JSON generation is manual and does not escape strings, so command lines, file names, or environment-derived values containing quotes/backslashes can produce invalid JSON. `PrintKeyVal` mutates the passed value when it ends in newline. Several functions early-return for nonzero ranks, which must match caller synchronization. `PrintArrayEnd` decrements `indent` even though `PrintArrayStart` does not increment it, making indentation state fragile. Summary calculations divide by timings and transfer sizes and can emit infinities for zero elapsed time.

## Test Signals
Golden output tests for default, CSV, and JSON formats; command lines with special characters; multi-repetition summaries; stonewalling summary paths; and rank-gated output under MPI validate this code.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/ior-output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/ior.c -->
# sources/test-tools/ior/src/ior.c

## Purpose
Contains the core IOR benchmark engine. It initializes MPI/test state, selects and initializes AIORI backends, validates parameters, generates file names and data patterns, executes write/read/check loops, times operations, reduces metrics, verifies data, removes files, and reports summaries.

## Important APIs, Types, And Functions
Exports `ior_run`, `ior_main`, `init_IOR_Param_t`, `AllocResults`, `FreeResults`, `CreateTest`, `GetPlatformName`, `GetTestFileName`, `test_time_elapsed`, and `GetOffsetArrayRandom`. Important internal functions include `test_initialize`, `test_finalize`, `ior_set_xfer_hints`, `InitTests`, `ValidateTests`, `TestIoSys`, `WriteOrRead`, `WriteOrReadSingle`, `CheckFileSize`, `CompareData`, `CountErrors`, `ReduceIterResults`, `RemoveFile`, `PrependDir`, `DistributeHints`, `HogMemory`, `StoreRankInformation`, and `ProcessIterResults`.

## Control Flow
`ior_main` initializes MPI, parses tests, initializes defaults, prints headers, runs each test, prints summaries, finalizes MPI, and destroys tests. `ior_run` provides a library-style variant using an existing communicator/output stream. For each test, `test_initialize` builds a smaller test communicator, sets globals, optionally initializes CUDA/backend, sends xfer hints, and prints start data. `TestIoSys` loops repetitions: setup buffers, warn on existing files, optionally remove old files, create/open backend fd, call `WriteOrRead`, close, check size, reduce/tally results, optionally verify data, read, remove files, and print summaries. `WriteOrRead` computes sequential or random offsets, handles stonewalling and min/max duration behavior, performs optional random prefill, and calls `WriteOrReadSingle` per transfer.

## State And Persistence Behavior
File-scope state includes `totalErrorCount` and selected `backend`; shared globals include `rank`, `rankOffset`, `testComm`, output streams, verbosity, and backend warning policy. Persistent benchmark artifacts are created through backend hooks and optionally removed unless `keepFile` or `keepFileWithError` applies. Optional CSV output is written per operation/rank and for rank details. Stonewalling can persist iteration counts in a status file.

## Dependencies And Integration Points
Depends on MPI, optional CUDA, AIORI backends, parser code (`parse_options.h`), utilities for timing, memory patterns, node mapping, aligned buffers, random functions, stonewalling storage, and output functions from `ior-output.c`. Every backend must honor the `ior_aiori_t` lifecycle and `xfer` byte-count contract used here.

## Risks And Edge Cases
Global `backend` and `testComm` make concurrent embedded runs unsafe. `test_finalize` frees global `testComm` rather than `test->params.testComm` by address, so global state must remain consistent. `CreateTest` shallow-copies `IOR_param_t`, including pointer fields and backend options, which complicates ownership. Random offset mode `>1` computes offsets using `sizerand / blockSize * blockSize - transferSize`, which can underflow for small sizes. Some buffers for `PrependDir` are heap allocated and returned without clear ownership at call sites. `WriteOrReadSingle` aborts on any short transfer, so async/object backends must accurately return byte counts. Parameter validation has backend-specific exclusions that may miss newer S3 backends in fsync warnings.

## Test Signals
Coverage should include write, read, write-check, read-check, file-per-process, shared-file, random offset modes, reorder modes, stonewalling/wear-out, min/max duration, GPU memory flags where available, save-per-op/rank CSV output, multi-repetition summaries, and every enabled backend's create/xfer/close/get_file_size/remove path.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/ior.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/ior.h -->
# sources/test-tools/ior/src/ior.h

## Purpose
Defines the public core data structures and entry points for the IOR benchmark engine. It describes test parameters, transfer buffers, per-operation results, test list nodes, and the callable main/run APIs.

## Important APIs, Types, And Functions
Defines `IOR_io_buffers`, `IOR_param_t`, `IOR_point_t`, `IOR_results_t`, and `IOR_test_t`. Declares `CreateTest`, `AllocResults`, `GetPlatformName`, `init_IOR_Param_t`, `ior_run`, and `ior_main`. Also defines `ISPOWEROFTWO` and HDFS placeholder types when HDFS support is disabled.

## Control Flow
`IOR_param_t` is populated from defaults and command-line/script parsing, then consumed by `ior.c` to drive backend selection, MPI communicator setup, file naming, data layout, timing, verification, and output. `IOR_results_t` arrays are allocated per test and filled per repetition.

## State And Persistence Behavior
The header itself owns no storage, but `IOR_param_t` carries almost all mutable test state: backend pointer/options, file names, MPI communicators, access mode flags, size/layout controls, random/stonewalling state, output paths, GPU memory settings, POSIX flags, URI, and transfer hints.

## Dependencies And Integration Points
Includes config, HDFS type definitions, `option.h`, `iordef.h`, `aiori.h`, MPI, and MPI-IO when needed. Comments explicitly require synchronized updates to defaults, usage, parser directives, and user guide whenever `IOR_param_t` changes.

## Risks And Edge Cases
`IOR_param_t` is large and shallow-copied in `CreateTest`, so pointer ownership is subtle. Adding fields without updating initialization/parsing/output documentation can produce uninitialized behavior. MPI communicator fields and backend options tie this structure to a specific runtime context. Some fields are intermediate parser strings, while others are authoritative runtime values.

## Test Signals
Builds with and without optional HDFS/MPI-IO support, parser/default round-trip tests, multi-test scripts, `ior_run` embedding tests, and result allocation/freeing validate this API.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/ior.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/iordef.h -->
# sources/test-tools/ior/src/iordef.h

## Purpose
Provides common IOR definitions, portability shims, constants, enums, and scalar typedefs shared by core code and backends.

## Important APIs, Types, And Functions
Defines `ior_dataPacketType_e`, `ior_memory_flags`, `enum OutputFormat_t`, boolean constants, decimal and binary byte constants, access-mode constants `WRITE`/`WRITECHECK`/`READ`/`READCHECK`, verbosity levels, `MAX_STR`, `MAX_HINTS`, `MAX_RETRY`, `PATH_MAX`, parser delimiters, `FILENAME_DELIMITER`, `IOR_offset_t`, `IOR_size_t`, and `IOR_format`. Adds Windows compatibility definitions for POSIX-like functions and `utsname`.

## Control Flow
No runtime control flow is implemented here. The constants and enums steer parsing, validation, data generation, transfer loops, and output formatting across the benchmark.

## State And Persistence Behavior
No state or persistence. It standardizes integer widths for offsets and transfer sizes as signed long long values.

## Dependencies And Integration Points
Optionally includes generated config, stdio/stdlib/string, Windows headers or POSIX headers. Included by `ior.h`, `aiori.h`, and backend code, making its definitions part of the common ABI.

## Risks And Edge Cases
`IOR_offset_t`/`IOR_size_t` are signed long long, so extremely large sizes can overflow in multiplications such as expected aggregate file size. Windows compatibility macros redefine common functions and can diverge from POSIX behavior. `random()` emulation only has noted limited entropy. Access mode constants are integers rather than an enum, so invalid values are possible.

## Test Signals
Cross-platform compilation, large-size parsing/validation tests, output format selection, access mode switch coverage, and Windows builds validate this file's assumptions.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/iordef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/md-workbench-main.c -->
# sources/test-tools/ior/src/md-workbench-main.c

## Purpose
Provides the standalone executable entry point for the metadata workbench tool.

## Important APIs, Types, And Functions
Includes MPI and `md-workbench.h`. Defines `main(int argc, char **argv)`, calls `MPI_Init`, invokes `md_workbench_run(argc, argv, MPI_COMM_WORLD, stdout)`, finalizes MPI, and returns 0.

## Control Flow
The wrapper initializes MPI before handing control to the metadata workbench implementation and finalizes MPI afterward. Commented lines show earlier API-check/debug use of returned phase statistics.

## State And Persistence Behavior
No local state is persisted. Runtime output goes to stdout through `md_workbench_run`; any filesystem effects are owned by the workbench implementation.

## Dependencies And Integration Points
Integrates the md-workbench library code with MPI process startup. It is separate from IOR's `ior_main` path but shares the same test-tools source tree and AIORI backends through md-workbench internals.

## Risks And Edge Cases
The return value from `md_workbench_run` is ignored, so failures may not affect process exit status unless that function aborts. MPI is always initialized/finalized here, making embedding or nested MPI ownership unsuitable.

## Test Signals
Executable smoke tests, option parsing through `md_workbench_run`, and failure-path tests that verify exit status behavior are the relevant signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/md-workbench-main.c -->
