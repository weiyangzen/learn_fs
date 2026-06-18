# subset-b-009232 research

Grouped research report for fio test tools and regression harnesses under `sources/test-tools/fio/t`. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/btrace2fio.c -->
# sources/test-tools/fio/t/btrace2fio.c

## Purpose
Converts binary Linux blktrace streams into either an ASCII workload summary or a fio replay-style job file. It groups observed I/O by trace PID, infers read/write/trim mix, block-size distribution, queue depth, sequentiality, start delay, runtime, rate, target devices, and optional collapsed `numjobs`.

## Important APIs, Types, and Functions
Core state is held in `struct btrace_pid` and `struct btrace_out`; block-size accounting uses `struct bs`, device mappings use `struct trace_file`, and in-flight queue-depth tracking uses `struct inflight`. `load_blktrace()` reads `struct blk_io_trace` records through a fio `fifo`; `handle_trace()`, `handle_queue_trace()`, `handle_trace_fs()`, and `handle_trace_discard()` update per-PID statistics. `trace_needs_swap()` and `byteswap_trace()` handle endianness. `__output_p_ascii()` and `__output_p_fio()` emit the two output formats, while `prune_entry()`, `entries_close()`, `merge_entries()`, and `check_merges()` filter or collapse similar jobs.

## Control Flow
`main()` parses thresholds and output options, detects trace byte order, initializes PID and in-flight hash buckets, loads one trace file, normalizes the first timestamp, then calls `output_p()`. While loading, queue actions create in-flight entries and update size/count/sequential stats, merge actions adjust or remove in-flight entries, and completion actions convert bytes to KiB and reduce outstanding depth. Output pruning drops tiny, short, or low-rate PIDs before sorting by I/O count and rendering each retained PID as a summary or fio job section.

## State and Persistence Behavior
The program is batch-only. Persistent output is stdout text; there is no file write besides caller redirection. In-memory state includes global hash lists, dynamic block-size arrays, per-PID device names, merged PID lists, and optional extra fio options. `filename` supplied with `-d` overrides detected devices for fio job output.

## Dependencies and Integration Points
Depends on fio internals for data-direction constants, intrusive lists, hashes, fifos, byte swapping, logging, min/max helpers, blktrace record definitions, and Linux device lookup. Generated fio output integrates with fio job-file syntax through `ioengine`, `iodepth`, `rw`, `rwmixread`, `percentage_random`, `filename`, `runtime`, `bssplit`, `rate`, and user-provided `-a` options.

## Risks
Depth inference depends on matching queue/merge/complete trace events; missing completions cap depths at `max_depth`. Device lookup failure is fatal for fio job output unless `-d` is used. Low-frequency block sizes below one percent are omitted from `bssplit`, which can hide tail behavior. Collapse heuristics compare sequentiality and depth only, so merged jobs can overgeneralize distinct workloads. Several allocations are unchecked or only lightly checked.

## Test Signals
Useful signals are successful parsing of native and swapped traces, rejection of bad magic/version/PDU lengths, sane ASCII totals, replay job output for read/write/trim and mixed jobs, `-d` override behavior, pruning thresholds, rate emission, and collapse behavior on near-identical PIDs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/btrace2fio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/client_server.py -->
# sources/test-tools/fio/t/client_server.py

## Purpose
Regression harness for fio client/server mode. It starts four local fio daemon servers, runs command-line client jobs against one or more servers, and validates JSON output for global option propagation and aggregated latency percentile reporting.

## Important APIs, Types, and Functions
`ClientServerTest` extends `FioJobCmdTest` and builds `--client=<server> <jobfile>` argument pairs. `ClientServerTestGlobalSingle` validates a single job file's `[global]` section against JSON `global options`. `ClientServerTestGlobalMultiple` validates the array form used with multiple clients. `ClientServerTestAllClientsLat` checks the `All clients` aggregate for expected `slat`, `clat`, and `lat` percentile presence. `start_servers()`, `stop_servers()`, `parse_args()`, and `main()` drive server lifecycle and runner setup.

## Control Flow
`main()` creates an artifact directory, resolves the fio binary, daemonizes servers on ports 8765-8768, rewrites test specs from server/job indexes into concrete paths, then delegates to `run_fio_tests()`. Each test creates one fio client invocation and inherits JSON decoding and basic success checks from `FioJobCmdTest`. After tests, the script kills the daemon PIDs from pidfiles and exits with the failure count.

## State and Persistence Behavior
State is stored in artifact subdirectories through the common runner: command, stdout, stderr, exit code, and JSON output files. Runtime server PID files are created with `tempfile.mktemp()` and tracked in `PIDFILE_LIST`. The script mutates `TEST_LIST` in place by replacing server indexes and relative jobfile names with concrete values.

## Dependencies and Integration Points
Depends on a built fio executable, local TCP/loopback ports, job files under `t/client_server`, Python `configparser`, and `fiotestlib` runner semantics. It directly validates fio's client/server JSON schema, especially `global options` and `client_stats`.

## Risks
Fixed ports can collide with existing services. `tempfile.mktemp()` is race-prone. A server startup failure exits before cleanup of already-started servers. `stop_servers()` uses `kill` directly and is Unix-oriented. In-place `TEST_LIST` mutation means repeated `main()` calls in the same interpreter would corrupt server indexes.

## Test Signals
Passing tests indicate basic client/server operation, single and multi-client global option reporting, no-global behavior, mixed global array matching by host/port, and correct all-client latency percentile inclusion or exclusion for `slat`, `clat`, and `lat`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/client_server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/debug.c -->
# sources/test-tools/fio/t/debug.c

## Purpose
Provides a minimal debug/logging shim for small fio test tools that link against fio internals but do not need the full fio debug subsystem.

## Important APIs, Types, and Functions
Defines global symbols `FILE *f_err`, `void *fio_ts`, and `unsigned long fio_debug` expected by linked fio objects. Exports `__dprint()` as a no-op variadic debug printer and `debug_init()` to point `f_err` at `stderr`.

## Control Flow
There is no complex flow: callers invoke `debug_init()` during startup, after which fio logging code that writes via `f_err` has a valid stream.

## State and Persistence Behavior
Only process-global debug state is provided. No persistent files are written.

## Dependencies and Integration Points
Integrated by test programs such as `dedupe.c` via `debug.h`, satisfying linker references from shared fio code paths without pulling the full application.

## Risks
All debug output is silently discarded through `__dprint()`, so problems in linked fio internals can be harder to diagnose. The global `fio_ts` is only a stub and must not be relied on for real fio thread state.

## Test Signals
The main signal is successful link/startup of utilities that include fio internals and call `debug_init()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/debug.h -->
# sources/test-tools/fio/t/debug.h

## Purpose
Declares the minimal debug initializer used by test utilities that compile with the local `debug.c` shim.

## Important APIs, Types, and Functions
Exports `debug_init(void)` behind the `FIO_DEBUG_INC_H` include guard.

## Control Flow
No runtime logic exists in the header.

## State and Persistence Behavior
No state is owned by the header; it exposes initialization of the state defined in `debug.c`.

## Dependencies and Integration Points
Included by `dedupe.c` and any similar test binary needing fio logging globals.

## Risks
The header declares only `debug_init()`, so code requiring richer debug APIs still depends on external symbols or the full fio headers.

## Test Signals
Successful compilation of consumers that include `debug.h` verifies the header contract.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/dedupe.c -->
# sources/test-tools/fio/t/dedupe.c

## Purpose
Scans a file or block device for duplicate fixed-size extents and reports dedupe ratio, fio-compatible `dedupe_percentage`, and optionally compressed unique capacity or full duplicate extent lists.

## Important APIs, Types, and Functions
`struct worker_thread` tracks per-thread progress, duplicate counts, zlib state, and file descriptor. `struct chunk` stores a unique MD5 hash in a fio red-black tree; `struct extent` records offsets when collision checking or dumps are enabled. `get_size()`, `get_work()`, `read_blocks()`, `crc_buf()`, `insert_chunk()`, `insert_chunks()`, `thread_fn()`, `run_dedupe_threads()`, `dedupe_check()`, `iter_rb_tree()`, and `show_stat()` form the scan pipeline.

## Control Flow
`main()` parses block size, threads, direct I/O, bloom, collision, progress, dump, and compression options, initializes fio architecture/runtime state, then scans the input. `dedupe_check()` opens the target and computes an aligned size. Worker threads claim `chunk_size` ranges under `size_lock`, read them, hash every `blocksize` block, and either insert hashes into a shared red-black tree or update a probabilistic bloom filter under `rb_lock`. After joining, the main thread derives totals and prints ratio/statistics.

## State and Persistence Behavior
The target is read-only. Persistent behavior is stdout/stderr output only. Shared in-memory state includes `cur_offset`, `total_size`, `rb_root`, optional `bloom`, global `file`, semaphore locks, and per-thread zlib buffers. When compression is enabled, unique blocks are reread and deflated to estimate capacity.

## Dependencies and Integration Points
Uses fio internals for file/device sizing, semaphores, aligned memory, red-black trees, bloom filters, MD5, timing, architecture setup, cleanup, and logging. Uses zlib for compression estimates and pthreads for parallel scanning.

## Risks
Default bloom mode is approximate and cannot support exact duplicate counts, dumps, collision checks, or compression. The progress loop stops when any thread is done rather than all threads, so display can end early. `thread_fn()` marks normal no-work termination as `err = 1`, though the joined error is not aggregated. `blocksize` should be power-of-two-like because size alignment masks with `blocksize - 1`. Large exact scans can consume significant memory for unique chunks and extents.

## Test Signals
Good coverage would compare known-pattern files against expected duplicate percentages, exercise bloom versus exact tree modes, verify collision-check rejection of MD5 collisions by content, confirm `O_DIRECT` alignment behavior, and validate compression output for repeated and random data.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/dedupe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/fiotestcommon.py -->
# sources/test-tools/fio/t/fiotestcommon.py

## Purpose
Provides shared success-policy dictionaries, safe file reading, and environment requirement probes for fio Python regression tests.

## Important APIs, Types, and Functions
`SUCCESS_DEFAULT`, `SUCCESS_LONG`, `SUCCESS_NONZERO`, and `SUCCESS_STDERR` describe expected return/stderr/timeout behavior. `get_file()` reads text using the preferred locale encoding. `Requirements` computes class-level booleans and exposes requirement callbacks such as `linux()`, `libaio()`, `io_uring()`, `zbd()`, `root()`, `zoned_nullb()`, `not_macos()`, `not_windows()`, `unittests()`, `cpucount4()`, and `nvmecdev()`.

## Control Flow
Constructing `Requirements(fio_root, args)` probes the host platform. On Linux it reads `config-host.h` for feature macros, checks `/proc/kallsyms` for `io_uring_setup`, tests effective UID, and optionally tries `modprobe null_blk` for zoned-nullb support. It also checks for a built unittest binary, CPU count, and an optional NVMe character device argument, then logs every requirement result.

## State and Persistence Behavior
Requirement results are class variables, so one probe establishes process-global state for subsequent callbacks. External side effects are limited to possible `modprobe null_blk` execution.

## Dependencies and Integration Points
Used by test scripts through requirement lists consumed by `run_fio_tests()`. It depends on fio build artifacts, Linux proc/sysfs conventions, Python platform APIs, and command execution.

## Risks
Missing `config-host.h` sets ZBD to true but leaves some other feature flags false, which can over-admit zoned tests in unusual trees. `/proc/kallsyms` visibility can be restricted, making io_uring probing conservative. Class-level state can become stale if multiple different fio roots or argument sets are probed in one interpreter.

## Test Signals
Tests should check requirement callbacks on Linux/non-Linux mocks, missing config handling, unittest path detection, CPU-count threshold, and `args.nvmecdev` propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/fiotestcommon.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/fiotestlib.py -->
# sources/test-tools/fio/t/fiotestlib.py

## Purpose
Defines the shared Python test framework used by many fio regression scripts to run fio binaries, job files, and command-line jobs while collecting artifacts and checking expected process/output behavior.

## Important APIs, Types, and Functions
`FioTest` owns common paths, artifact filenames, setup, and pass/fail state. `FioExeTest` runs a generic executable with timeout handling and checks return code/stderr expectations. `FioJobFileTest` wraps fio job files, optional preconditioning jobs, output-format selection, and JSON parsing. `FioJobCmdTest` builds command-line fio invocations, reads JSON output, reads IOPS logs, and validates data-direction emptiness through `check_empty()` and `check_all_ddirs()`. `run_fio_tests()` is the central table-driven runner.

## Control Flow
Test scripts pass dictionaries describing test class, ID, fio options, job files, requirements, and success policy. `run_fio_tests()` applies skip filters, constructs the right test object, checks requirements unless disabled, calls `setup()`, `run()`, and `check_result()`, then reports and optionally removes per-test artifacts. `FioExeTest.run()` uses `subprocess.Popen` instead of `subprocess.run()` so timeout cleanup can terminate fio more gracefully.

## State and Persistence Behavior
Every test writes command, stdout, stderr, exitcode, and often fio output files under `artifact_root/<test_id>`. Parsed JSON and IOPS logs are stored in object fields for subclass checks. The runner mutates configs by supplying a default success policy for command tests.

## Dependencies and Integration Points
Integrates all fio Python tests with the fio executable, fio job files under `t/jobs`, common requirement callbacks, platform-specific Python invocation on Windows, and artifact cleanup behavior.

## Risks
JSON extraction assumes output contains lines from the first `{` through the last `}`, which fails for malformed or empty output and can mis-handle braces in non-JSON text. `FioExeTest.run()` asserts `proc.poll()` after `terminate()`, which assumes prompt process exit. Test configs are mutable and can leak changes across repeated runs. Only stderr size and return code are checked generically, so deeper semantic validation must be supplied by subclasses.

## Test Signals
Framework signals include timeout behavior, nonzero/stderr success policies, JSON decoding with leading informational lines, precondition failure propagation, Windows script invocation, requirement-based skips, pass-through arguments, and artifact cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/fiotestlib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/fuzz/fuzz_parseini.c -->
# sources/test-tools/fio/t/fuzz/fuzz_parseini.c

## Purpose
libFuzzer entry point that fuzzes fio INI/job-file parsing by feeding arbitrary data into `parse_jobs_ini()` in parse-only mode.

## Important APIs, Types, and Functions
Defines `LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)`. Uses a static `initialized` flag, fake command-line arguments `--output /dev/null --parse-only`, and fio APIs `fio_init_options()`, `parse_cmd_line()`, `sinit()`, and `parse_jobs_ini()`.

## Control Flow
Inputs shorter than two bytes are ignored. The first fuzz call initializes fio option parsing and runtime state. For each input, the harness allocates a buffer, copies all but the last byte, NUL-terminates it, and passes the final input byte as the `stonewall`/type argument to `parse_jobs_ini()`.

## State and Persistence Behavior
Fio initialization is persistent across fuzz cases through static process state. Output is redirected to `/dev/null`; no corpus artifacts are written by the harness itself.

## Dependencies and Integration Points
Links directly against fio parser internals and is meant for libFuzzer or a compatible harness. `onefile.c` in the same directory can drive this entry point with a single file.

## Risks
Process-global fio state may accumulate between fuzz iterations if parser paths are not reentrant or do not fully reset temporary state. The final byte drives parser mode, so generated inputs need at least two bytes to exercise content parsing.

## Test Signals
Crashes, sanitizer findings, leaks, or hangs in `parse_jobs_ini()` are the primary signals. Seed files should include job sections, globals, malformed options, includes, escapes, and truncated lines.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/fuzz/fuzz_parseini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/fuzz/onefile.c -->
# sources/test-tools/fio/t/fuzz/onefile.c

## Purpose
Small standalone driver that reads one input file and passes its bytes to `LLVMFuzzerTestOneInput()`, allowing fuzz targets to be reproduced outside a fuzzer runtime.

## Important APIs, Types, and Functions
Declares the external `LLVMFuzzerTestOneInput()` symbol and implements `main()`. Uses standard C file I/O, `fseek()`, `ftell()`, `malloc()`, and `fread()`.

## Control Flow
`main()` requires exactly one path. It opens the file in binary mode, seeks to the end to determine size, rewinds, allocates an exact-size buffer, reads the entire file, calls the fuzz entry point, frees the buffer, closes the file, and returns zero unless setup/read errors occurred.

## State and Persistence Behavior
No persistent state beyond reading the supplied file. It returns `1` for usage errors and `2` for file/allocation/read failures.

## Dependencies and Integration Points
Designed to link with a fuzz target such as `fuzz_parseini.c`. It is useful for crash minimization and CI reproduction of a specific corpus file.

## Risks
`ftell()` result is cast to `size_t`, so extremely large files or platform-specific `long` limits can be problematic. Empty files allocate zero bytes and then expect `fread(..., size, 1, ...) == 1`, which may reject them.

## Test Signals
The executable should reproduce the same return/crash behavior as the fuzzer entry point for a given corpus file.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/fuzz/onefile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/gen-rand.c -->
# sources/test-tools/fio/t/gen-rand.c

## Purpose
Command-line sanity checker for fio's random number helper `rand_between()`. It samples a requested inclusive range and reports whether bucket counts fall within one standard deviation of the expected uniform mean.

## Important APIs, Types, and Functions
Uses `struct frand_state`, `init_rand()`, and `rand_between()` from fio's random library. `main()` parses `start`, `end`, and `nvalues`, allocates bucket counters, computes binomial mean/deviation, and prints pass/fail per bucket.

## Control Flow
After argument and range validation, it initializes deterministic fio random state, loops `nvalues` times, increments the chosen bucket, then evaluates each bucket against `[mean - dev, mean + dev]`.

## State and Persistence Behavior
Only in-memory bucket state exists. Output is human-readable stdout/stderr; no files are written.

## Dependencies and Integration Points
Depends on fio `lib/rand.h`, `lib/types.h`, and `log.h`. It is a statistical smoke test for code used by fio workload generation.

## Risks
One-standard-deviation acceptance is statistically strict for many buckets, so a correct RNG can produce failures. `strtoul()` parsing does not reject trailing garbage. Large ranges or sample counts can allocate large memory or run long.

## Test Signals
Expected signals are argument validation failures for bad ranges and approximately uniform bucket output across common ranges with a sufficiently large sample count.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/gen-rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/genzipf.c -->
# sources/test-tools/fio/t/genzipf.c

## Purpose
Generates and summarizes synthetic Zipf, Pareto, or normal access distributions using fio's distribution libraries, helping users choose fio random distribution parameters and cache-size expectations.

## Important APIs, Types, and Functions
`struct node` records a unique generated offset and hit count. Hash helpers `hashv()`, `hash_lookup()`, and `hash_insert()` track unique offsets in a chained hash table. `parse_options()` configures type, input parameter, GiB size, block size, output rows, cache-hit percentage, and CSV mode. `output_csv()` and `output_normal()` render ranked hit counts and bucket summaries.

## Control Flow
`main()` parses options, computes the number of block ranges, initializes the selected fio distribution state (`zipf_init`, `pareto_init`, or `gauss_init`), builds a hash sized from range count, samples one value per range, increments unique-node hit counters, sorts nodes by hit count, and outputs either CSV or a human summary.

## State and Persistence Behavior
All state is transient heap memory. Output is stdout. The optional `-p` percentage reports how much cache would satisfy the requested percentage of hits.

## Dependencies and Integration Points
Uses fio's `zipf`, `gauss`, list, and Jenkins hash helpers. The results map directly to fio distribution configuration values and block-size/data-set sizing decisions.

## Risks
Memory use scales with `nranges`; the default 500 GiB at 4 KiB implies a very large `nodes` allocation and hash table. `int` loop counters over `nranges` can overflow on large data sets. Default `dist_val` for normal distribution remains zero unless supplied. Input validation is minimal for zero block size and huge row counts.

## Test Signals
Useful tests include small deterministic data sets for each distribution, CSV format validation, invalid distribution parameter rejection, and cache-percentage output sanity.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/genzipf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/ieee754.c -->
# sources/test-tools/fio/t/ieee754.c

## Purpose
Round-trip test for fio's IEEE-754 double serialization helpers.

## Important APIs, Types, and Functions
Uses `fio_double_to_uint64()` and `fio_uint64_to_double()` from `lib/ieee754.h`. `main()` iterates a static set of representative doubles and returns the number of mismatches.

## Control Flow
Each value is converted to a `uint64_t`, converted back to `double`, printed with delta, and compared for exact equality. The sentinel `0.0` terminates the loop and is not tested.

## State and Persistence Behavior
No persistent state. Output is diagnostic stdout and the process exit code carries mismatch count.

## Dependencies and Integration Points
Validates conversion routines used anywhere fio needs stable binary or integer representation of floating-point values.

## Risks
The sentinel means zero itself is not tested despite appearing in the values array. Exact equality is appropriate for bit-preserving conversions but would fail if helpers intentionally normalized NaNs or other special values; those special values are not covered.

## Test Signals
Exit code zero indicates all listed values round-trip exactly. Additional useful signals would include zero, infinities, NaNs, subnormals, and negative zero.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/ieee754.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/io_uring.c -->
# sources/test-tools/fio/t/io_uring.c

## Purpose
Standalone fio-adjacent benchmark and exerciser for Linux `io_uring`, optional legacy libaio, synchronous `preadv2`, and NVMe passthrough read commands. It stresses submission/completion behavior, registered buffers/files/rings, SQPOLL, IOPOLL, restrictions, NUMA placement, hugepage buffers, vectored I/O, and latency percentile reporting.

## Important APIs, Types, and Functions
`struct submitter` is the per-thread coordinator with ring mappings, files, buffers, counters, latency buckets, and optional aio context. `struct file` tracks max size, offset, pending I/O, fixed file ID, and NVMe namespace metadata. Ring setup uses `io_uring_setup()`, `setup_ring()`, `io_uring_register_buffers()`, `io_uring_register_files()`, `io_uring_register_ring()`, and `io_uring_register_restrictions()`. Fast paths include `prep_more_ios_uring()`, `init_io()`, `init_io_pt()`, `reap_events_uring()`, `reap_events_uring_pt()`, `submitter_uring_fn()`, `submitter_aio_fn()`, and `submitter_sync_fn()`. Latency support uses `plat_val_to_idx()`, `calculate_clat_percentiles()`, and `show_clat_percentiles()`.

## Control Flow
`main()` parses many single-letter options, opens target files/devices, distributes them across submitter threads, optionally maps a hugetlbfs file, then starts one worker thread per submitter. Each worker initializes memory and engine state, keeps queue depth filled up to `depth`, submits in `batch_submit` batches, reaps completions in `batch_complete` batches, updates latency buckets if enabled, and exits when global or per-thread finish is set. The main thread sleeps once per second, prints IOPS/BW/call metrics, enforces optional runtime, handles signals, joins workers, and prints per-thread latency percentiles.

## State and Persistence Behavior
The tool opens targets read-only and does not intentionally write data. It may create a `tsc-rate` file when `-T` is used and may mmap caller-provided hugetlbfs storage. Runtime state includes global finish flags, shared maximum IOPS, per-thread ring mmap regions, allocated I/O buffers, registered resources, and file offsets.

## Dependencies and Integration Points
Depends on Linux `io_uring` syscalls and headers, fio arch/os/rand/minmax helpers, NVMe command definitions, optional libaio, optional libnuma, optional `preadv2`, and block/NVMe device ioctls. It directly exercises kernel interfaces that fio's ioengines also rely on.

## Risks
The program is Linux and feature-level sensitive; many options fail depending on kernel, filesystem, device, privileges, and build macros. Global `sq_ring_mask`/`cq_ring_mask` are shared across submitters and assume compatible rings. Pointer arithmetic on `void *` relies on compiler extensions. Registered resources and mmaps are not comprehensively unwound on every error. Passthrough mode requires `/dev/ngXnY` and read opcode assumptions. Latency buckets require CPU-clock support and enough samples.

## Test Signals
Signals include successful setup for normal, fixed-buffer, fixed-file, SQPOLL, IOPOLL, registered-ring, restricted, vectored, libaio, sync, NUMA, hugetlb, and NVMe passthrough modes; stable IOPS output; no unexpected completion results; and plausible percentile output when stats are enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/io_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/io_uring_pi.py -->
# sources/test-tools/fio/t/io_uring_pi.py

## Purpose
Destructive NVMe protection-information regression harness for fio's `io_uring` engine. It formats a target namespace with supported LBA formats, protection types, and PI locations, then tests DIF/DIX metadata read/write behavior.

## Important APIs, Types, and Functions
`DifDixTest` extends `FioJobCmdTest` and builds fio jobs with `--ioengine=io_uring`, `--md_per_io_size`, `--pi_act=0`, `--pi_chk`, app tags, variable block-size ranges, and optional engine flags. `get_lbafs()`, `get_guard_pi()`, `get_capabilities()`, `format_device()`, and `difdix_test()` discover and iterate device formats.

## Control Flow
`main()` parses `--dut`, resolves fio, queries LBA formats and namespace PI capabilities with `nvme-cli`, assigns the target filename to every test, and loops over `(lbaf, pil, pitype)` combinations. Each combination formats the device, creates a combination-specific artifact directory, adjusts block-size range, metadata size, and `pi_chk` for Type 3 PI, then runs five tests covering write/read success and expected read failures for app-tag mismatch or invalid mask.

## State and Persistence Behavior
This script persistently reformats the target namespace and overwrites data on it. Artifacts are written under a timestamped root, partitioned by LBA format, PI location, and PI type. `TEST_LIST` entries are mutated per combination with derived `filename`, `bsrange`, `md_per_io_size`, and `pi_chk`.

## Dependencies and Integration Points
Requires Linux, root/sudo access, `nvme` CLI, a target NVMe namespace, fio with io_uring metadata support, and JSON output parsing through `fiotestlib`.

## Risks
The test is explicitly destructive. It trusts `sudo nvme format` and handles one known rescan warning but skips other failures. It assumes JSON keys from `nvme-cli` such as `lbafs`, `elbafs`, `mc`, and `dpc`. Type 3 PI handling strips `REFTAG`, but other device-specific PI restrictions may still produce false failures.

## Test Signals
Passing signals include successful metadata writes, successful reads with matching guard/ref/app tags, intentional failure for app-tag mismatch, intentional failure for invalid app-tag mask, and compatibility across supported LBA format/PI combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/io_uring_pi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/jsonplus2csv_test.py -->
# sources/test-tools/fio/t/jsonplus2csv_test.py

## Purpose
Smoke test for converting fio `json+` latency-bin output to CSV with `fio_jsonplus_clat2csv`, including the converter's validation mode.

## Important APIs, Types, and Functions
`run_fio()` chooses an async engine by platform and runs a three-job fio workload producing `fio-output.json` in `json+` format. `check_output()` runs the converter once normally and once with `--validate`. `parse_args()` and `main()` resolve paths and report pass/fail count.

## Control Flow
The script resolves the fio executable and converter path, runs fio for a short random read/write workload with slat/clat/lat percentiles enabled, then checks that CSV generation and validation both exit zero.

## State and Persistence Behavior
Writes `fio-output.json`, `fio-output.csv`, and the workload target file in the current working directory. No artifact root isolation is provided.

## Dependencies and Integration Points
Depends on fio, the converter under `tools/fio_jsonplus_clat2csv`, Python subprocess support, and an async ioengine (`libaio`, `windowsaio`, or `posixaio`) to produce submission latencies.

## Risks
Current-directory outputs can collide with existing files. It only checks command success, not CSV contents directly. If platform async engine support is unavailable, fio fails before converter behavior is tested.

## Test Signals
The signal is one passing test after fio generation, CSV conversion, and converter self-validation succeed.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/jsonplus2csv_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/latency_percentiles.py -->
# sources/test-tools/fio/t/latency_percentiles.py

## Purpose
Comprehensive regression harness for fio latency percentile reporting across JSON, JSON+, terse output, unified read/write reporting, sync latency, multi-job aggregation, and per-priority latency summaries.

## Important APIs, Types, and Functions
`FioLatTest` runs fio, parses JSON/terse output, and implements validators: `check_latencies()`, `similar()`, `check_jsonplus()`, `check_sync_lat()`, `check_terse()`, `check_nocmdprio_lat()`, and `check_prio_latencies()`. Test subclasses `Test001` through `Test021` encode direction-specific expectations. `main()` builds a 22-case matrix using null and async engines, percentile option combinations, `fsync`, `numjobs`, `cmdprio_percentage`, `cmdprio_bssplit`, and `unified_rw_reporting`.

## Control Flow
Each test creates an artifact subdirectory, runs fio with latency logs enabled and the configured output format, then parses output. `check_latencies()` reads raw latency log files, filters by data direction or unified reporting, recomputes fio-style percentile ranks, and compares values within the theoretical 1/128 bin error. JSON+ checks validate bins against min/max/sample counts. Terse tests compare selected terse percentile fields to JSON values. Priority tests verify per-priority sample counts, min/max, weighted means, and optionally merged bins.

## State and Persistence Behavior
Artifacts include command, stdout, stderr, exitcode, fio output, workload files, and latency log files under `latency-test-<timestamp>/<test_id>`. No external devices are required, but cmdprio tests are skipped unless running as Linux root. The test list is local to `main()`.

## Dependencies and Integration Points
Depends on fio output schemas, latency log formats, platform async engine selection (`libaio`, `windowsaio`, or `posixaio`), CSV parsing, and Python math/json tools. It validates fio statistic code paths such as `sum_thread_stats()`, JSON+ bins, sync latency accounting, and priority aggregation.

## Risks
Percentile comparisons are approximate and can fail on largest latency bins, as noted by the TODO. Terse index slices are tied to terse version 3 and default percentile layout. Runtime tests can be noisy on slow hosts. Root-only cmdprio skips reduce coverage on common CI setups.

## Test Signals
Passing tests prove expected presence/absence of slat/clat/lat percentiles, consistency with raw latency logs, JSON+ bin self-consistency, terse/JSON agreement, sync latency reporting, multi-job aggregation, unified mixed reporting, and per-priority summary consistency.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/latency_percentiles.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/lfsr-test.c -->
# sources/test-tools/fio/t/lfsr-test.c

## Purpose
Interactive benchmark and verifier for fio's linear-feedback shift register sequence generator.

## Important APIs, Types, and Functions
Uses `struct fio_lfsr`, `lfsr_init()`, and `lfsr_next()`. `main()` accepts the number of values in hex, optional seed, spin count, and a `verify` flag, then prints LFSR parameters and timing.

## Control Flow
After argument parsing and architecture initialization, the program initializes the LFSR. In verify mode it allocates one byte per expected number and marks each generated value. It loops until `lfsr_next()` reports completion, optionally validates every value appeared exactly once, computes elapsed microseconds, and returns zero or verification failure.

## State and Persistence Behavior
No persistent state. Verification can allocate large memory proportional to the requested sequence length. Output is split between stdout summaries and stderr progress.

## Dependencies and Integration Points
Depends on fio LFSR, timing, architecture, and compiler fallthrough helpers. It validates random-offset generation infrastructure used by fio.

## Risks
Verification memory is unbounded relative to user input. Pointer arithmetic on `void *` is a compiler extension. `atol()`/`atoi()` parsing is permissive and seed is decimal while count is hex.

## Test Signals
Signals include successful initialization for valid sizes, full-cycle uniqueness in verify mode, and stable mean generation timing for performance comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/lfsr-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/log.c -->
# sources/test-tools/fio/t/log.c

## Purpose
Minimal `log_err()` and `log_info()` implementation for standalone test tools that link fio helper libraries.

## Important APIs, Types, and Functions
Defines `log_err(const char *format, ...)` and `log_info(const char *format, ...)`. Both format into a fixed 1024-byte stack buffer with `vsnprintf()`, clamp the length with fio's `min()`, and write to `stderr` or `stdout`.

## Control Flow
Each call formats variadic input, clamps output to buffer capacity, then writes one item through `fwrite()`.

## State and Persistence Behavior
No persistent state; output goes to standard streams.

## Dependencies and Integration Points
Uses `../minmax.h` and satisfies logging references from small C utilities such as `gen-rand.c`.

## Risks
Return value is `fwrite()` item count rather than byte count, so callers expecting standard printf-like semantics may be surprised. Output longer than 1023 bytes is truncated.

## Test Signals
Compilation/linking of standalone utilities and visible stdout/stderr messages are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/log_compression.py -->
# sources/test-tools/fio/t/log_compression.py

## Purpose
Regression test for fio I/O log compression, ensuring compressed or asynchronously flushed log entries are neither missing nor out of order.

## Important APIs, Types, and Functions
`run_fio()` runs a null-engine sequential write workload with `--write_bw_log`, `--log_offset=1`, and `--log_compression=10K`, optionally adding `--log_store_compressed=1` and inflating the `.fz` log through fio. `check_log_file()` validates line count and monotonic offsets. `main()` runs both compressed-storage modes.

## Control Flow
For each `log_store_compressed` value, the script runs fio, inflates if needed, reads the resulting BW log, checks that the number of non-empty lines equals `1000M / 128K`, and verifies the fifth CSV field advances by block size from zero.

## State and Persistence Behavior
Writes `test_bw.log`, `test_bw.log.fz`, and `test_bw.from_fz.log` in the current directory. It does not isolate artifacts or remove outputs.

## Dependencies and Integration Points
Depends on fio's null engine, bandwidth log writer, log compression/inflation path, and subprocess execution.

## Risks
Current-directory output can collide with existing logs. It assumes log CSV field order and exact one-entry-per-I/O behavior. `subprocess.check_output()` raises on fio failure before a clean failed test report.

## Test Signals
Two passing cases prove uncompressed compressed-buffer flushing and stored-compressed inflation preserve all 8000 sequential offsets in order.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/log_compression.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/memlock.c -->
# sources/test-tools/fio/t/memlock.c

## Purpose
Memory pressure utility that allocates a configured MiB amount per thread and repeatedly touches pages, useful for exercising memory locking, page residency, or system pressure scenarios.

## Important APIs, Types, and Functions
`struct thread_data` holds MiB per thread. `worker()` allocates `mib * 1024 * 1024`, loops 100000 times, and writes 512 bytes at offset 512 of each 4 KiB page. `main()` parses MiB and thread count, creates pthreads, and joins them.

## Control Flow
The main thread validates arguments, allocates the pthread array, stores the shared MiB value, starts all workers with the same `td`, then waits for completion. Each worker prints one message after its first full pass.

## State and Persistence Behavior
No files are written. Runtime state is large heap allocation per worker and CPU time spent dirtying memory.

## Dependencies and Integration Points
Uses pthreads and libc allocation/memset. It is independent of fio internals despite living in the test tree.

## Risks
`malloc()` is not checked before use. Very large MiB/thread values can exhaust memory or trigger OOM. The fixed 100000 passes can run for a very long time. All workers share one immutable `td`, which is safe for current fields but would not be for mutable additions.

## Test Signals
Signals are successful allocation/startup and visible first-pass output for each thread. External monitoring can observe memory pressure or locking behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/memlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/numberio_overlap.py -->
# sources/test-tools/fio/t/numberio_overlap.py

## Purpose
Regression harness for fio verify `numberio` handling when writes overlap because `io_size > size`, random maps are disabled, mixed modes revisit offsets, real file size is smaller than configured size, or multiple files share the job.

## Important APIs, Types, and Functions
`OfflineOverlapVerifyTest` runs separate write and `verify_only` phases and checks both JSON outputs. `OnlineOverlapVerifyTest` runs a single `--do_verify=1` job. Both build fio arguments dynamically, support multi-file `--filename` strings, parse JSON with leading text stripped, and validate `verify_errors`, write byte counts, and verify read byte counts where exact expectations are meaningful. `TEST_LIST` encodes 13 offline/online scenarios.

## Control Flow
`main()` resolves fio, optionally probes requirements, fills every test's target filename, selects async and sync engines by platform or `--ioengines`, deep-copies the test matrix for each engine, and calls `run_fio_tests()`. Offline tests run a write phase with `--do_verify=0` followed by a verify phase with `--verify_only=1 --verify_write_sequence=1`. Online tests run write and verify in one job.

## State and Persistence Behavior
Artifacts are written under `numberio-overlap-test-<timestamp>/<engine>/<test_id>`. Test data is written to the user-selected `--file` path, and multi-file cases append `.0`, `.1`, etc. Some tests pre-create/truncate files to force `real_file_size < size`.

## Dependencies and Integration Points
Depends on fio verify internals, JSON output, platform ioengines, `fiotestlib`, and `fiotestcommon.Requirements`. It specifically targets overlap-risk and rb-tree `io_hist` paths in fio verification.

## Risks
The script is destructive to the target file path. Random `norandommap` cases intentionally skip exact read-byte assertions because coverage is probabilistic. Mixed read/write modes skip byte assertions because read counts combine workload reads and verify reads. Platform engine defaults can make results dependent on local async engine support.

## Test Signals
Passing tests indicate overlapping writes complete to `io_size`, verify reads check only the latest numberio once per block in deterministic cases, no verify errors occur in overlap scenarios, early rb-tree initialization works for short real files, and multi-file overlap accounting works.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/numberio_overlap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/nvmept.py -->
# sources/test-tools/fio/t/nvmept.py

## Purpose
Regression harness for fio's `io_uring_cmd` NVMe passthrough engine against an NVMe generic character device. It checks read/write/trim direction accounting, verification, queue-depth attainment, SQPOLL/fixed resource combinations, and flush command accounting.

## Important APIs, Types, and Functions
`PassThruTest` builds standard passthrough fio jobs with `--ioengine=io_uring_cmd --cmd_type=nvme` and validates nonzero/zero data-direction sections using `check_all_ddirs()`. It also requires the requested iodepth level 8 to be reached at least 95 percent. `FlushTest` builds jobs with `fsync` and checks `sync.total_ios` against expected write/fsync cadence. `TEST_LIST` defines 19 cases.

## Control Flow
`main()` parses required `--dut`, creates an artifact root, resolves fio, assigns the target device to every test, and runs the test list. Early tests cover sequential/random read, write, trim, mixed read/write, and trimwrite. Later tests enable fixed buffers/files, force async, SQPOLL, and validate flush behavior for read, write, readwrite, and trimwrite modes.

## State and Persistence Behavior
The script writes artifacts under `nvmept-test-<timestamp>`. It performs I/O directly to the provided NVMe character device and write/trim cases are destructive to device contents.

## Dependencies and Integration Points
Requires a fio build with `io_uring_cmd` NVMe support, Linux NVMe generic character devices such as `/dev/ng0n1`, JSON output, and the common Python runner. It exercises fio's NVMe command construction and accounting paths.

## Risks
The target device is destructive for write and trim tests. Tests assume the device can sustain iodepth 8; slow or constrained devices can fail the depth threshold despite functional correctness. Flush expectations allow one missing sync at tail but still assume stable `fsync` accounting. There is no requirement probe for device existence beyond fio failure.

## Test Signals
Passing cases prove direction-specific stats for read/write/trim/mixed passthrough commands, verify read-back on write tests, SQPOLL/fixed-resource compatibility for read/write/trim, and expected sync command counts for flush-enabled jobs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/nvmept.py -->
