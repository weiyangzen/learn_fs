# Research: subset-b-000331

Grouped research for zstd test and regression harness files. Each section preserves the source path in the title and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/poolTests.c -->
## sources/compression/zstd/tests/poolTests.c

Purpose: This is a focused executable test for the zstd thread pool abstraction in `pool.h`. It validates pool creation constraints, FIFO-style job completion behavior, queue draining during `POOL_free()`, deadlock resistance with small queues, thread-count reduction through `POOL_resize()`, and completion of queued jobs when a pool is shrunk immediately before teardown.

Important APIs, types, and functions: The file uses `POOL_create()`, `POOL_add()`, `POOL_resize()`, and `POOL_free()` from the pool implementation, plus zstd's pthread wrapper types `ZSTD_pthread_mutex_t` and `ZSTD_pthread_cond_t`. Local assertion macros return `1` from the active test on failure. `struct data` is shared by `fn()` to record job ordering under a mutex. `poolTest_t` combines a mutex, condition variable, active-worker counter, maximum-observed concurrency, and countdown latch for resize checks. `abruptEndCanary_t` records how many queued delayed jobs actually ran before `POOL_free()` returned.

Control flow: `main()` first rejects successful creation with zero threads, then runs `testOrder()` and `testWait()` for `numThreads` 1 through 4 and `queueSize` 0 through 2. `testOrder()` submits sixteen jobs that lock a mutex, write their current index, and increment it; after `POOL_free()` it verifies all entries were executed in submission order. `testWait()` floods the pool with short sleeping jobs to expose producer/consumer deadlocks. `testThreadReduction()` creates a four-thread pool, observes max concurrency of four, resizes to two, and observes max concurrency of two. `testAbruptEnding()` queues all jobs, shrinks the pool, frees it, and verifies teardown waits for every job.

State and persistence: All state is process-local and owned by stack structs protected by mutexes and condition variables. There is no file or global persistence. The pool itself is externally allocated by `POOL_create()` and must be freed even on successful paths.

Dependencies and integration points: It integrates with zstd's portable threading wrapper, `UTIL_sleepMilli()` from `util.h`, and the library pool implementation. It is normally built and run as part of zstd's native test suite to guard multithreaded compression infrastructure.

Risks and test signals: The ordering assertion depends on pool semantics that preserve execution order in the tested configuration; if pool behavior changes to allow out-of-order execution, this test will fail even if every job completes. Timing-sensitive sleeps make resize tests sensitive to very slow or oversubscribed systems, though the condition variable countdown avoids fixed waits. A pass prints `PASS: all POOL tests`; failures print a named test failure and exit nonzero.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/poolTests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/rateLimiter.py -->
## sources/compression/zstd/tests/rateLimiter.py

Purpose: This Python script is a minimal stdin-to-stdout throttler used as a replacement for `pv` in tests. It limits throughput to a caller-specified number of MB/s and intentionally does not "catch up" after blocking.

Important APIs and functions: The script has no function definitions. At module execution it reads `sys.argv[1]`, converts it to bytes per second using `MB = 1024 * 1024`, and loops over `sys.stdin.buffer.read()` and `sys.stdout.buffer.write()`. It catches `KeyboardInterrupt` and `BrokenPipeError` so pipelines can terminate without noisy tracebacks.

Control flow: It initializes `start = time.time()` and repeatedly computes how many bytes may be read since the previous iteration. `to_read` is at least one byte and capped to 1 MiB. It then resets `start` to the current time, reads up to `to_read`, writes the buffer, and exits once read returns an empty buffer.

State and persistence: State is transient: current timestamp, rate, and the current buffer. `total_read` is initialized but unused, so the limiter is interval-based rather than cumulative. It writes no files and has no persistent cache.

Dependencies and integration points: It depends only on Python standard modules `sys` and `time`. Test scripts can insert it in a pipe to simulate slow producers or consumers for zstd streaming behavior.

Risks and test signals: There is no argument validation, so missing or invalid rates raise Python exceptions. Because writes are not flushed explicitly and no sleep is used, low rates can still be affected by pipe buffering and scheduler timing. The unused `total_read` hints that cumulative accounting was considered but not implemented. Successful behavior is observable by bounded output throughput and clean exit on EOF or broken downstream pipe.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/rateLimiter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/Makefile -->
## sources/compression/zstd/tests/regression/Makefile

Purpose: This Makefile builds the zstd compression regression executable in `tests/regression`. It compiles the harness modules, links against a locally built multithreaded `libzstd.a`, and pulls in libcurl for downloading regression datasets.

Important targets and variables: `CFLAGS ?= -O3` allows callers to override optimization. `CURL_CFLAGS` and `CURL_LDFLAGS` come from `curl-config`; `CURL_LDFLAGS` also adds `-pthread`. `PROGDIR` and `LIBDIR` point to zstd's `programs` and `lib` directories. `ZSTD_CPPFLAGS` exposes program and library headers and suppresses deprecated API warnings because the harness intentionally exercises older APIs. Targets build `xxhash.o`, `util.o`, `data.o`, `config.o`, `method.o`, `result.o`, `test.o`, `libzstd.a`, and finally `test`.

Control flow: The default target is `all: test`. Object targets compile local and upstream source files with the regression flags. The phony `libzstd.a` target invokes `make -C ../../lib libzstd.a-mt` then copies the resulting archive into the regression directory. `test` links all objects and the archive with curl and pthread flags. `clean` delegates library cleanup and removes generated regression objects, archive, and executable.

State and persistence: Build outputs are local object files, copied `libzstd.a`, and `test`. No test data cache is managed here; runtime cache handling lives in `data.c` and the executable arguments.

Dependencies and integration points: Requires a C compiler, zstd source tree layout, `curl-config`, libcurl development files, pthread support, and make support in the upstream `lib` directory. It integrates harness modules through their headers and links static zstd plus `xxhash` and `util`.

Risks and test signals: `curl-config` is evaluated at make parse time, so missing curl tooling fails early or yields bad flags. Copying `libzstd.a` into the working directory can leave stale artifacts if the library target fails partially. A successful build produces the `test` executable; a useful smoke signal is `make -C tests/regression test`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/config.c -->
## sources/compression/zstd/tests/regression/config.c

Purpose: This module defines the compression-configuration matrix used by the regression harness. It expands level macros from `levels.h` into `config_t` objects covering normal levels, negative fast levels, dictionary variants, row-match-finder settings, multithreading, long-distance mode, literal-compression modes, explicit frame/compression parameters, and pledged-source-size behavior.

Important APIs, types, and functions: It exports `configs`, a NULL-terminated array of `config_t const*`. `config_skip_data()` skips dictionary-only configs for data without dictionaries. `config_get_level()` extracts `ZSTD_c_compressionLevel` or returns `CONFIG_NO_LEVEL`. `config_get_zstd_params()` derives `ZSTD_parameters` from a config, source size, and dictionary size, then overlays selected C parameters and frame parameters.

Control flow: Macro families `FAST_LEVEL`, `LEVEL`, and `ROW_LEVEL` declare static `param_value_t` arrays and corresponding `config_t` instances. `levels.h` is included twice: once to generate definitions and once to populate `g_configs`. Additional static configs cover no pledged size, LDM, MT, small logs, explicit params, and literal modes. At runtime, callers iterate the exported array, optionally skip invalid data/config combinations, and pass the config to compression methods.

State and persistence: The matrix is static read-only configuration. No runtime state is mutated except the harness's iteration through these objects. Parameter arrays are file-scope and live for the process lifetime.

Dependencies and integration points: Depends on `config.h`, zstd static-only parameter enums, `levels.h`, and `data_has_dict()`. It is consumed by `test.c` and `method.c`. The string `cli_args` field must remain compatible with the CLI tested by `method.c`, while `param_values` must remain compatible with the advanced API paths.

Risks and test signals: The macro expansion is broad, so adding a level can multiply the test matrix substantially. `config_get_zstd_params()` handles only a subset of `ZSTD_cParameter` values; advanced-only parameters such as workers or row finder may be applied by other method paths but not reflected in legacy `ZSTD_parameters`. CLI and API parameter equivalence can drift. Expected signals are stable result-table rows and skips for unsupported combinations rather than compression errors.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/config.h -->
## sources/compression/zstd/tests/regression/config.h

Purpose: This header defines the regression harness's compression configuration contract. It gives `method.c` and `test.c` a uniform way to identify a test configuration, provide equivalent CLI arguments and API parameters, and decide whether dictionary or pledged-size behavior applies.

Important APIs and types: `param_value_t` pairs a `ZSTD_cParameter` with an integer value. `param_values_t` wraps an array and size. `config_t` includes `name`, optional `cli_args`, `param_values`, and boolean fields `use_dictionary`, `no_pledged_src_size`, and `advanced_api_only`. `CONFIG_NO_LEVEL` is a sentinel below the valid compression-level range. Public functions are `config_skip_data()`, `config_get_level()`, and `config_get_zstd_params()`. `configs` is a NULL-terminated exported config list.

Control flow: The header itself has no executable flow. It shapes the runtime flow by allowing the harness to iterate `configs`, skip incompatible data, derive levels for simple APIs, and derive `ZSTD_parameters` for legacy advanced APIs.

State and persistence: All state described by this header is immutable configuration once compiled. It does not allocate or persist resources.

Dependencies and integration points: It uses `ZSTD_STATIC_LINKING_ONLY` before including `<zstd.h>` so internal/advanced parameter types are visible. It includes `data.h` because skip logic depends on dataset dictionary availability.

Risks and test signals: The API intentionally bridges several zstd API generations, so fields can be meaningful for one method and ignored by another. Adding new parameters requires checking both modern `ZSTD_CCtx_setParameter()` users and legacy `ZSTD_parameters` derivation. Correctness is signaled by consistent matrix rows across CLI and API methods and by intentional skips for incompatible configs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/data.c -->
## sources/compression/zstd/tests/regression/data.c

Purpose: This module defines the regression datasets, downloads and verifies them, derives local cache paths, exposes file/directory contents as buffers, and manages cache validity through a stamp hash. It is the harness's data supply layer.

Important APIs, types, and functions: It exports `data`, a NULL-terminated list containing `silesia`, `silesia.tar`, `github`, and `github.tar`, with optional dictionary resources for GitHub data. Public functions include `data_has_dict()`, `data_init()`, `data_finish()`, `data_buffer_read()`, `data_buffer_get_data()`, `data_buffer_get_dict()`, `data_buffer_create()`, `data_buffer_compare()`, `data_buffer_free()`, `data_buffers_get()`, and `data_buffers_free()`. Internal helpers handle path concatenation, `mkdir -p`, curl callbacks, decompression/extraction with `zstd` and `tar`, path creation/freeing, and stamp hashing.

Control flow: `data_init(dir)` ensures the cache directory exists, stores `g_data_dir`, creates derived paths, checks whether `STAMP` matches the current data manifest, and otherwise downloads all resources. Downloads stream through libcurl into a `popen()` pipeline: file resources are decompressed to the derived file path, directory resources are decompressed and extracted under the cache directory. The raw downloaded compressed stream is hashed with XXH64 and compared to the expected resource hash. On completion, `stamp_write()` records or removes the stamp. Runtime buffer helpers either read a single file or expand a directory to file names via `UTIL_createExpandedFNT()`.

State and persistence: Persistent state lives under the caller-provided cache directory: decompressed files/directories, dictionaries, and `STAMP`. Process-global `g_data_dir` and derived `path` fields are allocated in `data_init()` and released by `data_finish()`.

Dependencies and integration points: Depends on libcurl, zstd CLI in `PATH` for decompression, `tar`, zstd `util.h`, `mem.h`, and `xxhash.h`. It is consumed by `config.c`, `method.c`, and `test.c`. URLs point to the zstd GitHub regression-data release.

Risks and test signals: `popen()` command strings quote paths but still rely on shell command construction and external tools. `data_buffers_free()` only frees the buffers array, not each buffer's `data`, so repeated directory buffer loads can leak file contents unless process lifetime hides it. `buffer_state_destroy()` in `method.c` also does not call this module's free helpers. Cache correctness depends on hash/stamp coverage; URL changes are ignored by design if names and hashes remain constant. Success signals include "stamp matches" reuse, "stamped new data cache", matching XXH64 checks, and nonzero buffers for all expanded files.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/data.h -->
## sources/compression/zstd/tests/regression/data.h

Purpose: This header declares the dataset and buffer abstraction for the regression harness. It lets compression methods treat file and directory datasets uniformly while still exposing dictionaries and cache initialization.

Important APIs and types: `data_type_t` distinguishes a single file from a directory. `data_resource_t` stores a download URL, expected XXH64, and derived local path. `data_t` combines data and dictionary resources, type, and logical name. `data_buffer_t` owns a byte pointer, size, and capacity. `data_buffers_t` represents multiple buffers for directory datasets. Public functions cover dictionary availability, cache lifecycle, reading dataset data/dictionaries, direct file reads, buffer allocation, comparison, and freeing.

Control flow: The header has no implementation flow, but its contracts drive the harness: `test.c` calls `data_init()` and `data_finish()`, `method.c` loads `data_buffers_t` and optional dictionaries per dataset, and configs call `data_has_dict()` to skip dictionary-required cases.

State and persistence: It declares the external `data` list and cache lifecycle but stores no state itself. Callers are responsible for honoring ownership rules: buffers returned from read/create functions must be freed, and cache-derived paths are valid after successful initialization until `data_finish()`.

Dependencies and integration points: Uses standard `stddef.h` and `stdint.h`. It is included by `config.h`, `method.h`, `test.c`, and implementation modules.

Risks and test signals: The comments state `data_buffers_free()` frees a list of buffers, but callers must understand whether individual buffer contents are freed by the implementation. Directory versus file semantics are important: `data_buffer_get_data()` returns empty for directories. Correct use is signaled by non-empty `data_buffers_t` for datasets and successful dictionary loads only when `data_has_dict()` is true.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/levels.h -->
## sources/compression/zstd/tests/regression/levels.h

Purpose: This macro include file centralizes the compression levels used by the regression matrix. It is included by `config.c` with `FAST_LEVEL`, `LEVEL`, and `ROW_LEVEL` defined to generate both objects and the config pointer list.

Important APIs and macros: The file requires callers to define `LEVEL(x)`, `FAST_LEVEL(x)`, and `ROW_LEVEL(x, y)`. It lists fast levels 5, 3, and 1; normal levels including 0, 1, 3 through 7, 9, 13, 16, and 19; and row-match variants at selected levels with `y` values representing force enabled and disabled.

Control flow: There is no runtime flow. The compile-time flow is macro expansion: each entry expands according to the including context. The comments explain that selected levels aim to trigger every strategy across source sizes, fast levels, default level, and row hash entries of different widths.

State and persistence: None. This is a generated-code driver for static configuration.

Dependencies and integration points: It is tightly coupled to `config.c` and must be included only after the three macros are defined. It assumes zstd's level-to-strategy mapping and row hash behavior, so it should be updated when compression strategy thresholds change.

Risks and test signals: Because it is macro-only, compile errors can be cryptic if a required macro is missing or has a mismatched expansion. Level selection can become stale as zstd internals evolve, reducing regression coverage without obvious build failures. Useful signals are the number and names of generated config rows in the regression output.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/levels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/method.c -->
## sources/compression/zstd/tests/regression/method.c

Purpose: This module implements the compression methods compared by the regression harness. It exercises zstd through simple one-shot APIs, reusable CCtx/DCtx APIs, CLI invocation, modern advanced APIs, constrained-output paths, and old streaming APIs with and without dictionaries/CDicts.

Important APIs, types, and functions: It exports `methods`, a NULL-terminated array of `method_t const*`, and `method_set_zstdcli()`. Local `buffer_state_t` extends `method_state_t` with loaded inputs, optional dictionary, and reusable compressed/decompressed buffers. Key implementations include `simple_compress()`, `compress_cctx_compress()`, `cli_compress()`, `advanced_one_pass_compress_output_adjustment()`, `advanced_streaming_compress()`, `init_cstream()`, and `old_streaming_compress_internal()`. Helper `advanced_config()` applies `config->param_values` through `ZSTD_CCtx_setParameter()`.

Control flow: `test.c` calls each method's `create()` once per dataset, then `compress()` for every config. Buffer-based methods load all dataset files and dictionaries once. Simple compression only handles single-file, non-dictionary, pledged-size configs with explicit levels and verifies round trips. `compress_cctx_compress()` handles directory datasets with reusable contexts and verifies decompression. CLI compression builds a shell command, reads compressed bytes from stdout, and reports size. Advanced methods set parameters, optionally pledged source sizes, then use `ZSTD_compress2()` or `ZSTD_compressStream2()`. Old streaming methods initialize `ZSTD_CStream` in basic, advanced, dictionary, or CDict modes, then stream input chunks and accumulate output sizes.

State and persistence: Method state is per dataset and should be destroyed through each method's `destroy`. `g_zstdcli` is process-global and must be set before CLI use. Compression buffers are reused across config calls. There is no persistent output except result rows produced by `test.c`.

Dependencies and integration points: Depends on zstd static-linking APIs, the config/data/result modules, and the zstd CLI path supplied by command-line parsing. It is the main integration point between the regression matrix and zstd API surfaces.

Risks and test signals: `buffer_state_destroy()` frees only the state struct and does not release nested buffers/dictionaries, so long runs leak memory. `cli_compress()` constructs a shell command using data and dictionary paths, making quoting and path contents security-sensitive. The `advanced_one_pass_small_out` method is declared with name "advanced one pass small out" but its `compress` pointer is wired to `advanced_one_pass_compress` instead of the small-output adjustment wrapper, so the intended too-small-output test may not run. Some advanced configs are skipped by older paths, which is expected. Success is a stable compressed-size table; errors are encoded as result strings.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/method.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/method.h -->
## sources/compression/zstd/tests/regression/method.h

Purpose: This header declares the compression method plugin interface used by the regression runner. It abstracts state creation, compression execution, and cleanup so `test.c` can iterate all methods uniformly.

Important APIs and types: `method_state_t` is the base state containing the active `data_t`. Derived states must embed it as a member. `method_t` has `name`, `create(data)`, `compress(state, config)`, and `destroy(state)` fields. `method_set_zstdcli()` sets the CLI executable used by CLI-backed methods. `methods` is the NULL-terminated exported method list.

Control flow: There is no executable flow in the header, but the lifecycle is explicit: create one method state for a dataset, call compress repeatedly for configs, then destroy the state.

State and persistence: State ownership is delegated to each method. The base type carries dataset identity only; derived implementations own buffers or other resources.

Dependencies and integration points: Includes `data.h`, `config.h`, and `result.h`, tying each method to a dataset/config pair and a `result_t` outcome. `test.c` is the primary consumer.

Risks and test signals: Because derived states are recovered with a `container_of` pattern in `method.c`, implementations must return a pointer to the embedded base exactly as documented. A destroy mismatch or partial allocation handling bug can leak or crash. Method names must be comma-free because the result table is comma-separated.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/method.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/result.c -->
## sources/compression/zstd/tests/regression/result.c

Purpose: This tiny implementation maps `result_t` error codes to human-readable strings for regression output.

Important APIs and functions: It implements `result_get_error_string(result_t result)`, switching on `result_get_error()` and returning strings for ok, skip, system error, compression error, decompression error, round trip error, and unknown error.

Control flow: The function is a straightforward switch. It is called by `test.c` when a method returns an error result that is not skipped.

State and persistence: None. Returned string literals are static and immutable.

Dependencies and integration points: Depends only on `result.h`. Its strings become part of the regression result table and any diff baseline, so changes can affect expected outputs.

Risks and test signals: Adding a new `result_error_t` without updating this switch will produce "unknown error" in output. Correct behavior is visible as readable error labels in the CSV-like results table.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/result.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/result.h -->
## sources/compression/zstd/tests/regression/result.h

Purpose: This header defines the result value used by regression methods. It carries either a successful compressed-size measurement or a typed error/skip result.

Important APIs and types: `result_error_t` enumerates ok, skip, system error, compression error, decompression error, and round-trip error. `result_data_t` contains `total_size`. `result_t` stores an internal error code and internal data. Static helper functions construct errors and data, test whether a result is error or skip, fetch the error, and fetch data. `result_get_error_string()` is implemented in `result.c`.

Control flow: Method implementations return `result_data()` on success, `result_error(result_error_skip)` for intentionally unsupported combinations, or another error for failures. `test.c` suppresses skips, prints error strings for errors, and prints `total_size` for successes.

State and persistence: Result values are passed by value and have no ownership or persistence.

Dependencies and integration points: Uses `stddef.h` for `size_t`. It is included by `method.h`, `method.c`, `result.c`, and `test.c`.

Risks and test signals: The header says not to access internal members directly, but the members are public in C and can be misused. `result_get_data()` does not assert non-error state, so callers must check first. Stable output depends on preserving enum/string meaning.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/result.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/regression/test.c -->
## sources/compression/zstd/tests/regression/test.c

Purpose: This is the command-line regression runner. It parses required cache/output/zstd options plus optional filters and diff baseline, initializes data, runs every method/data/config tuple, writes a CSV-like compressed-size table, and optionally compares it to a prior result file.

Important APIs and functions: Globals store parsed options: `g_output`, `g_diff`, `g_cache`, `g_zstdcli`, `g_config`, `g_data`, and `g_method`. `is_name_bad()` and `are_names_bad()` reject NULL names, comma-containing names, and track maximum padding length. `parse_args()` uses `getopt_long()`. `tprintf()` and `tflush()` mirror result output to file and stderr. `run_all()` performs the matrix iteration. `diff_results()` loads two files with `data_buffer_read()` and compares them.

Control flow: `main()` parses arguments, validates names, sets the CLI path, initializes the data cache, opens the output file, calls `run_all()`, closes output, optionally diffs, then calls `data_finish()`. `run_all()` prints a header, iterates methods with optional method filter, iterates datasets with optional data filter, creates method state once per dataset, iterates configs with optional config filter, applies `config_skip_data()`, calls the method, suppresses skip results, and prints either an error string or compressed size.

State and persistence: The output results file is persistent and may be compared to a baseline. The data cache persists through `data_init()`. Global option pointers reference `argv` memory. `g_max_name_len` is computed during validation and used for aligned output.

Dependencies and integration points: Includes `config.h`, `data.h`, and `method.h`. Runtime requires a working zstd CLI path, writable output path, and cache directory. It is built by the regression Makefile.

Risks and test signals: `parse_args()` does not detect unknown trailing positional arguments. If `methods[method]->create()` returns NULL, some method implementations report system errors while others may rely on destroy tolerating NULL. The output is not strict CSV because fields are padded with spaces, but comma-free name validation keeps simple diffing stable. Success is exit code zero, a complete result table, and optional "actual results match expected results".
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/regression/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/roundTripCrash.c -->
## sources/compression/zstd/tests/roundTripCrash.c

Purpose: This standalone test program loads a file, compresses and decompresses it with zstd, verifies exact round-trip equality, and deliberately crashes or exits on corruption. It is suitable for fuzzing and crash-focused regression detection.

Important APIs and functions: `roundTripTest()` uses `ZSTD_compress()` and `ZSTD_decompress()` with a compression level derived from an XXH32 hash of up to the first 128 bytes. `cctxParamRoundTripTest()` uses `ZSTD_CCtx`, `ZSTD_CCtx_params`, `ZSTD_CCtxParams_setParameter()`, `ZSTD_CCtx_setParametersUsingCCtxParams()`, and `ZSTD_compressStream2()` with workers and overlap settings. `roundTripCheck()` allocates buffers, dispatches the selected compression path, checks size and bytes through `checkBuffers()`, and frees buffers. File helpers determine regular-file size, reject directories, and load the input.

Control flow: `main()` requires an input file and optionally consumes `--cctxParams`. It then calls `fileCheck()`, which loads the file into memory and calls `roundTripCheck()`. Any zstd error, regenerated-size mismatch, byte mismatch, file-read failure, or allocation failure exits nonzero. In fuzzing builds, `crash()` calls `abort()` instead of `exit()`.

State and persistence: All buffers are heap-local to a single run and freed on success. No output file is written. The only persistent effect is process termination status or crash.

Dependencies and integration points: Depends on zstd static-linking declarations, `xxhash.h`, standard C file/stat APIs, and optional `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`. It integrates with fuzzing or test scripts that provide candidate input files.

Risks and test signals: `rBuff` is allocated with compressed-bound capacity, which is at least source size for zstd but is conceptually a decompression output buffer. The `--cctxParams` path uses multithreaded compression parameters, so builds without threading support may behave differently. Error messages precede nonzero exit or abort; success writes "no pb detected" to stderr.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/roundTripCrash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/seqgen.c -->
## sources/compression/zstd/tests/seqgen.c

Purpose: This module generates deterministic byte streams designed to produce specific zstd sequence characteristics: match length, literal length, and offset. It is a test-data generator for compression behavior that can be resumed across small output buffers.

Important APIs, types, and functions: It implements `SEQ_initStream()`, `SEQ_gen()`, and `SEQ_digest()` declared in `seqgen.h`. Internal `SEQ_randByte()` is a simple deterministic PRNG over an unsigned seed. `SEQ_gen_matchLength()`, `SEQ_gen_litLength()`, and `SEQ_gen_offset()` are state machines that write into `SEQ_outBuffer` and update an XXH64 digest of generated bytes.

Control flow: `SEQ_initStream(seed)` resets state and hash. `SEQ_gen()` dispatches based on `SEQ_gen_type`; callers must repeatedly pass the same type/value until it returns zero. Each generator uses `stream->state`, `stream->saved`, and `stream->bytesLeft` to resume after the caller's output buffer fills. Match-length generation emits a guard byte, a run of `value + 1` different bytes, then another guard. Literal-length generation emits a repeatable high-bit run, low-bit literals, then a repeated high-bit match. Offset generation emits a high-bit run, zero padding to create the target offset, then the saved high-bit run again.

State and persistence: `SEQ_stream` stores PRNG seed, resumable state, saved seed/byte, remaining byte count, and running XXH64 state. There is no file persistence; deterministic output depends only on stream seed and call sequence.

Dependencies and integration points: Depends on `seqgen.h`, `mem.h` for byte typedefs, `string.h`, and xxhash. It is intended for zstd tests that need controlled match/literal/offset pressure without hand-authored binary fixtures.

Risks and test signals: The API contract is strict: changing type or value before a nonzero return completes can corrupt the state-machine assumptions. Very small values are documented as unreliable in the header. Digest updates use only newly written bytes, so `out->pos` must be valid on entry. Success signals are deterministic output and stable `SEQ_digest()` for a fixed generation plan.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/seqgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/seqgen.h -->
## sources/compression/zstd/tests/seqgen.h

Purpose: This header exposes the deterministic sequence generator used by zstd tests. It defines generation modes and the resumable stream/output buffer contracts.

Important APIs and types: `SEQ_gen_type` contains `SEQ_gen_ml`, `SEQ_gen_ll`, `SEQ_gen_of`, and sentinel `SEQ_gen_max`. `SEQ_stream` stores internal XXH64 state, seed, state-machine integer, saved value, and bytes left. `SEQ_outBuffer` mirrors zstd-style buffers with `dst`, `size`, and `pos`. Public functions are `SEQ_initStream()`, `SEQ_gen()`, and `SEQ_digest()`.

Control flow: Callers initialize a stream, prepare an output buffer, call `SEQ_gen(stream, type, value, out)`, and repeat with the same `type` and `value` while the return value is nonzero. `SEQ_digest()` can be called to verify generated content so far.

State and persistence: State lives entirely in `SEQ_stream`, which callers own. The header labels it internal, but the struct is visible so it can be stack allocated and copied if needed.

Dependencies and integration points: Defines `XXH_STATIC_LINKING_ONLY`, includes `xxhash.h` and `stddef.h`, and is implemented by `seqgen.c`. It intentionally uses zstd-like buffer conventions, making it natural to embed in compression tests.

Risks and test signals: Since internals are visible, callers can mutate state accidentally. The note warns very small values below 6 do not work well, so test plans should avoid interpreting them too precisely. Deterministic hashes from `SEQ_digest()` are the primary verification signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/seqgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/test-license.py -->
## sources/compression/zstd/tests/test-license.py

Purpose: This Python test enforces zstd's expected Meta copyright and dual BSD/GPL license text across selected source directories.

Important APIs and functions: Constants define `ROOT`, scanned relative directories, excluded subdirectories, suffixes, scan limits, expected license lines, and basename exceptions. `valid_copyright()` checks for a copyright line containing "Meta Platforms, Inc", no year or "present", and the literal "(c)" form. `valid_license()` searches for the expected four-line license block. `valid_file()` reads the first 10 KB and first 50 lines, applies exception sets, and reports failures. `exclude()` filters absolute path prefixes. `main()` globs recursively and returns nonzero if any file fails.

Control flow: On execution, the script builds absolute scan/exclude roots, walks each directory/suffix combination with `glob.glob(..., recursive=True)`, skips excluded files, validates each file, accumulates invalid paths, and prints either "Pass!" or "Fail!" with invalid file names.

State and persistence: There is no persistent state. It reads source files and prints diagnostics to stderr/stdout.

Dependencies and integration points: Uses only Python standard modules. It is intended for CI or release checks over `doc`, `examples`, `lib`, `programs`, `tests`, and `contrib/linux-kernel`.

Risks and test signals: Matching by basename exceptions can exempt files with the same name in other directories. `valid_license()` indexes `lines[b + l]` without an explicit bounds check, relying on the first expected line not appearing too close to EOF. The suffix match includes any path ending with the string, so `Makefile` is treated as a suffix. Pass/fail output and exit status are the test signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/test-license.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/test-variants.sh -->
## sources/compression/zstd/tests/test-variants.sh

Purpose: This shell test verifies that specialized zstd binary variants include and exclude the intended feature symbols and still perform their supported compression/decompression roles.

Important APIs and functions: It defines paths to variant executables in `programs/`. Helpers include `println()`, `die()`, `symbol_present()`, `symbol_not_present()`, feature-specific symbol absence checks, `test_help()`/`test_no_help()`, `extras_not_present()`, `test_compress()`, `test_decompress()`, and `test_zstd()`.

Control flow: With `set -e -u -x`, the script fails on unset variables, failed commands, and echoes commands. It checks frugal/compress/decompress variants for missing dictionary, legacy, benchmark, and trace symbols; checks compress-only and decompress-only binaries for absent opposite-direction APIs; checks dictBuilder and nolegacy variants; verifies old legacy symbols are absent from the main binary; then runs small pipe-based compression/decompression tests and help-option expectations.

State and persistence: It creates no durable files except transient pipe data. It inspects binaries with `nm` and invokes zstd commands in pipelines.

Dependencies and integration points: Requires the variant binaries to already be built, plus `nm`, `grep`, a POSIX shell, and the main `zstd` binary for validation. It integrates with the zstd build matrix for variant targets.

Risks and test signals: `symbol_present()` treats an `nm` failure as text piped to `grep`, so missing binaries may produce less direct diagnostics. Symbol checks are platform/toolchain-sensitive because link-time optimization, stripping, or symbol visibility can change `nm` output. Success ends with "Success!"; any unexpected symbol/help support or failed pipe test exits nonzero.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/test-variants.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/test-zstd-versions.py -->
## sources/compression/zstd/tests/test-zstd-versions.py

Purpose: This Python integration test verifies interoperability across zstd release versions. It builds historical zstd tags plus the current development binary, generates compressed files and dictionaries, removes duplicates, and checks that each selected version can decompress compatible outputs.

Important APIs and functions: Configuration globals define the upstream repo, temporary directory, make/git commands, sample file, head tag name, dictionary source globs, and build arguments. `execute()`, `proc()`, `make()`, and `git()` wrap subprocess execution. `get_git_tags()` lists release tags. `dict_ok()` validates a dictionary. `create_dict()` builds or falls back to a dictionary. `zstd()` runs a tagged binary with file redirection. `compress_sample()`, `dict_compress_sample()`, `decompress_zst()`, and `decompress_dict()` generate and validate artifacts. `remove_duplicates()` collapses byte-identical compressed files. `sha1_of_file()` reports final artifact hashes.

Control flow: The script creates `tests/versionsTest`, clones the zstd repo if needed, copies `README.md` as test data, discovers tags `v[0-9].[0-9].[0-9]`, filters from `v0.5.0`, builds each historical tag and current head with appropriate legacy support, cleans old `.zst`/`.dec` files, creates dictionary source files, builds the head dictionary, then for each tag creates a dictionary, dictionary-compresses, deduplicates, dictionary-decompresses, plain-compresses, deduplicates, and plain-decompresses. It finishes by listing remaining compressed files with size and SHA1.

State and persistence: It creates and reuses `tests/versionsTest`, cloned source, checked-out tag directories, built binaries named `zstd.<tag>`, dictionaries, compressed samples, and decompressed files. It mutates current working directory extensively.

Dependencies and integration points: Requires network access for clone if the cache is absent, git, make, working compilers, zstd build compatibility across old tags, and a repository layout with `README.md` and `programs`. It is a high-cost integration lane rather than a quick unit test.

Risks and test signals: Tag filtering compares version strings lexicographically, which can be wrong for multi-digit components. Some command paths use `shell=True` with joined filenames for dictionary training. The script has no cleanup for the versions test directory, so it can consume significant disk. Compatibility expectations include explicit skips for v0.6.0 with older dictionaries. Success is absence of raised exceptions and a final enumeration of distinct `.zst` files.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/test-zstd-versions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/test_process_substitution.bash -->
## sources/compression/zstd/tests/test_process_substitution.bash

Purpose: This Bash test verifies zstd's `--filelist` support when the file list path is supplied through Bash process substitution.

Important APIs and commands: It accepts an optional first argument selecting the zstd executable, defaulting to `zstd`. It uses `rm`, `mkdir`, `echo`, `find`, `sort`, process substitution `<(...)`, output redirection, `grep`, and zstd compression/decompression flags `--filelist`, `-c`, `-d`, and `-o`.

Control flow: The script enables `set -e`, creates `tmp_process_substit` with three text files, removes prior artifacts, and runs five tests. Test 1 passes a sorted `find` output as a process-substitution file list. Test 2 passes an `echo -e` list. Test 3 writes a filelist then passes `cat` through process substitution. Test 4 decompresses the combined output and greps for all three expected file contents. Test 5 passes an empty list and accepts either graceful output creation or proper rejection. It then removes the temporary directory.

State and persistence: Temporary state is confined to `tmp_process_substit` and removed at the end on success. If a command fails before cleanup, the temp directory can remain for diagnosis.

Dependencies and integration points: Requires Bash specifically because POSIX `sh` does not support process substitution. It depends on zstd archive behavior for multiple files listed through `--filelist` and on decompression producing a combined output file.

Risks and test signals: The script uses Unicode check/cross symbols in output, unlike most source files. `echo -e` behavior is shell-dependent but Bash is explicit. `set -e` plus `|| true` intentionally tolerates the empty-list case. Success prints each pass message and "All tests completed successfully!".
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/test_process_substitution.bash -->
