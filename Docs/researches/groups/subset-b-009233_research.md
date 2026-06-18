# subset-b-009233 Research

Grouped research for fio test/tool sources under `sources/test-tools/fio/t`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_fdp.py -->
# sources/test-tools/fio/t/nvmept_fdp.py

Purpose: destructive fio regression coverage for NVMe passthrough Flexible Data Placement writes through `io_uring_cmd` with `--cmd_type=nvme`. It validates old FDP options (`fdp`, `fdp_pli`, `fdp_pli_select`) and newer data-placement options (`dataplacement=fdp`, `plids`, `plid_select`, `dp_scheme`) against NVMe reclaim unit accounting.

Important APIs and types: `FDPTest` extends `FioJobCmdTest` and builds fio command lines; `FDPSinglePLIDTest`, `FDPMultiplePLIDTest`, and `FDPReadTest` add FDP-specific RUAMW checks. Helper functions `get_fdp_status()`, `update_ruh()`, `update_all_ruhs()`, and `check_all_ruhs()` shell out to `nvme fdp status/update` and parse JSON. Constants `FIO_MAX_DP_IDS` and `DP_MAX_SCHEME_ENTRIES` mirror fio data-placement limits, while globals `FIO_FDP_MAX_RUAMW` and `FIO_FDP_NUMBER_PLIDS` are initialized from the device.

Control flow: `main()` parses `--dut`, creates an artifact directory, resolves fio, injects the target filename into every `TEST_LIST` case, resets all RUHs, records the baseline maximum RUAMW, then calls `run_fio_tests()`. Each test assembles fio arguments, runs via fiotestlib, checks JSON data-direction counters, validates requested iodepth when present, and finally resets/validates RUH state. Multiple-PLID tests expand dynamic expressions using runtime device facts, optionally emit a temporary placement scheme or iolog, then compare observed RUAMW to round-robin, random, or scheme expectations.

State and persistence: the script mutates the target namespace and FDP reclaim handles. It writes artifact output through fiotestlib plus temporary `lba.scheme` and `iolog` files in the test directory for scheme/iolog tests. Class/static state is limited to mutable `TEST_LIST` entries and runtime globals, so repeated in-process runs would inherit modified fio options.

Dependencies and integration points: depends on Python 3, `fiotestlib`, `fiotestcommon.SUCCESS_NONZERO`, fio built with NVMe passthrough support, sudo-capable `nvme-cli`, and an FDP-capable NVMe character device with at least five placement IDs and 4096-byte LBA data. It is integrated by `run-fio-tests.py` as executable test 101? style NVMe passthrough coverage when `Requirements.nvmecdev` is available.

Risks and test signals: risk is high because it is destructive and assumes RUAMW behavior and PLID ordering reported by `nvme fdp status`. `eval()` is used on formatted arithmetic strings from the local test list, so additions must not allow untrusted input. Test success signals include expected fio exit status, correct JSON direction activity, iodepth bucket 8 over 95 percent when requested, and exact or aggregate RUAMW deltas. Negative cases expect non-zero fio exits for invalid FDP/dataplacement combinations and PLID ranges.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_fdp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_pi.py -->
# sources/test-tools/fio/t/nvmept_pi.py

Purpose: destructive end-to-end protection information coverage for fio NVMe passthrough. It formats a target namespace through supported LBA formats, protection types, protection information locations, and metadata modes, then runs read/write and error tests for DIF/DIX options.

Important APIs and types: `DifDixTest` extends `FioJobCmdTest` and emits fio options such as `md_per_io_size`, `pi_act`, `pi_chk`, `apptag`, and `apptag_mask`. Device discovery helpers include `get_lbafs()`, `get_guard_pi()`, and `get_capabilities()`. `format_device()` wraps `nvme format`, and `difdix_test()` rewrites each test case for the current LBA format, PI type, and extended-LBA mode.

Control flow: `main()` parses fio path, target device, optional LBA formats, and ioengine. It discovers metadata-capable LBA formats, guard PI width, and namespace PI capabilities, injects filename/ioengine into `TEST_LIST`, then iterates over the cartesian product of `lbaf`, `pil`, `pitype`, and `elba`. For each combination it formats the device, creates a per-configuration artifact directory, adjusts block-size ranges and metadata buffer sizes, drops `REFTAG` checks for Type 3 PI, marks incompatible tests skipped, and invokes `run_fio_tests()`.

State and persistence: the namespace is reformatted multiple times with `sudo nvme format --force`, destroying data and changing metadata layout. Test dictionaries are mutated in place for each configuration. JSON outputs and logs persist under the selected artifact root. No rollback to the original format is attempted.

Dependencies and integration points: requires Python, fio, fiotestlib, nvme-cli, sudo, and a namespace with metadata and end-to-end data protection capability. It can use `io_uring_cmd` or `xnvme`; the xNVMe path adds `--thread=1` and `--xnvme_async=io_uring_cmd`. It plugs into the broader fio test system as a standalone executable harness.

Risks and test signals: risks include destructive formatting, stale mutable test options between product iterations, and device-specific behavior when `nvme nvm-id-ns` is unavailable, where the script assumes 16-bit guard PI. Positive tests require fio success and valid PI read/write behavior; negative tests intentionally use mismatched application tags, bad block sizes, or too-small metadata buffers and expect non-zero exits. Runtime and skipped counts are accumulated across all device configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_pi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_streams.py -->
# sources/test-tools/fio/t/nvmept_streams.py

Purpose: destructive regression coverage for NVMe streams directives through fio `io_uring_cmd` passthrough and `dataplacement=streams`. It verifies that selected placement IDs become active stream identifiers and that invalid stream configurations fail.

Important APIs and types: `StreamsTest` builds fio command lines and validates JSON data-direction counters. `StreamsTestRR` checks expected first-N stream use for round-robin selection; `StreamsTestRand` expects the random selection not to match the first-N round-robin pattern. Device helpers `get_device_stream_ids()`, `release_stream()`, and `release_all_streams()` call `nvme dir-receive` and `nvme dir-send`.

Control flow: `main()` parses target NVMe character device, creates artifacts, resolves fio, injects filename into all tests, releases existing streams, then runs `TEST_LIST`. Each test runs fio with stream placement options. `check_result()` always attempts to release streams in a `finally` block after checking fio output, iodepth, and active stream ID state.

State and persistence: the script changes stream directive state on the device and writes normal fiotestlib artifacts. It relies on active streams being queryable after fio completion, then clears them after each case. It has no persistent state beyond artifacts and mutated test dictionaries.

Dependencies and integration points: depends on fio with NVMe passthrough, `nvme-cli`, sudo for `dir-receive`, a stream-capable NVMe device, and fiotestlib. It is designed to be invoked directly or from the fio umbrella test runner with an NVMe character device requirement.

Risks and test signals: stream selection validation can be probabilistic for random selection, as the comments note false positives are possible if random picks the same first-N set. Device setup must have streams enabled externally. Success signals are fio exit status, JSON direction counters, iodepth level when requested, exact active stream ID set for ordinary and round-robin tests, and expected non-zero failure for invalid PLIDs or missing stream IDs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_streams.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_trim.py -->
# sources/test-tools/fio/t/nvmept_trim.py

Purpose: destructive NVMe passthrough dataset-management trim coverage for `io_uring_cmd`, including legacy trim workloads, multi-range trims, rate/accounting checks, invalid configurations, and data-pattern verification around deallocated ranges.

Important APIs and types: `TrimTest` extends `FioJobCmdTest` and centralizes fio argument construction and JSON data-direction validation. `RangeTrimTest` adds `get_bs()` for exact or average block-size calculation from `bs`, `bssplit`, or `bsrange`, and overrides `check_result()` to verify bandwidth, IOPS, total IO counts, and rate expectations for multi-range trim requests.

Control flow: `main()` parses fio path and destructive `--dut`, creates artifacts, injects filename, and calls `run_fio_tests()`. The test list first covers plain trim/randtrim/trimwrite/randtrimwrite and iodepth cases, then multi-range trim sizes and variable block sizes, then expected-failure invalid combinations, then a multi-step data-integrity scenario: write a pattern, verify it, trim half the namespace, confirm the trimmed half no longer returns the old pattern, and verify the untrimmed half.

State and persistence: the target namespace is modified by writes and trims. fiotestlib persists JSON and stdout/stderr artifacts. The script does not restore data, and multi-step tests depend on earlier steps preserving device state for later checks.

Dependencies and integration points: depends on Python, fio, fiotestlib, `SUCCESS_NONZERO`, Linux NVMe character device passthrough support, and a target device safe for destructive testing. It is included in `run-fio-tests.py` as an NVMe character-device executable test.

Risks and test signals: accounting checks use averages for `bssplit` and `bsrange`, so they tolerate fuzz rather than proving every range offset. There is a repeated `verify` option in the option allowlist and a likely typo `fixedbuffs` in one test option, useful for regression awareness. Success signals are fio return code, JSON direction counters, iodepth bucket checks, calculated byte totals within 5 percent, IO count match within tolerance, rate within 5 percent, and expected non-zero exits for unsupported range trimwrite or too many ranges.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_trim.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_write_mode.py -->
# sources/test-tools/fio/t/nvmept_write_mode.py

Purpose: destructive NVMe passthrough write-mode coverage for fio `io_uring_cmd`, including pure `write`, `verify`, `zeroes`, `uncor`, mixed percentage parsing, and verification behavior after write-zeroes or write-uncorrectable commands.

Important APIs and types: `WriteModeTest` builds common fio arguments and validates JSON data directions. `WriteModeSplit` parses `write_mode` percentage syntax, reads fio debug output, maps selected NVMe opcodes (`write`, `write_uncor`, `write_zeroes`, `verify`) to counters, and checks distribution within 10 percent. `WriteModeVerify` extends that by counting debug verification messages for uncorrectable and zeroes paths.

Control flow: `main()` parses `--dut`, creates artifacts, resolves fio from the build tree by default, injects filename, and runs `TEST_LIST`. The test matrix preconditions the device, checks verify-only workloads, writes zeroes and validates zero reads, creates uncorrectable ranges and expects subsequent reads/verifies to fail, then exercises valid and invalid mixed-mode expressions. Verification tests require `--debug=io,verify` so the checker can infer opcode and verify activity.

State and persistence: the target device is modified by writes, write zeroes, and write uncorrectable operations. The script persists fio output files and parses those files after execution. Test ordering is meaningful because preconditioning tests feed later verification tests.

Dependencies and integration points: depends on fio write-mode support, NVMe passthrough via `io_uring_cmd`, fiotestlib, and `SUCCESS_NONZERO`. It is registered in `run-fio-tests.py` as an NVMe character-device executable test.

Risks and test signals: debug-output parsing is sensitive to fio message text such as `op selected`, `errored io_u`, and `verifying write zeroes`. Mixed-mode expected counts use integer rounding, so small total IO counts would be noisy; the configured 16M filesize provides enough samples. Success signals include correct fio exit status, JSON direction activity, opcode mix distribution, expected parser failures for bad `write_mode`, and matching counts for special writes and their verify handling.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/nvmept_write_mode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/one-core-peak.sh -->
# sources/test-tools/fio/t/one-core-peak.sh

Purpose: root-only performance helper that tunes the host and block devices, chooses CPUs on the first physical core, and runs `t/io_uring` to estimate one-core block I/O peak throughput, optionally with latency reporting.

Important APIs and functions: shell functions handle argument parsing (`check_args()`), root/binary validation, CPU selection (`detect_first_core()`), sysfs device tuning (`check_io_scheduler()`, `check_sysblock_value()`), CPU governor tuning, NVMe/device reporting, kernel config reporting, and final command construction. `block_dev_name()` and `get_sys_block_dir()` normalize `/dev/*` paths into sysfs paths.

Control flow: after parsing `-h` and `-l`, the script requires root, validates tools, detects the local CPU/core for a single NVMe drive or falls back to CPU 0 for multiple drives, prints system and device metadata, forces scheduler and queue settings, checks NVMe poll queues, sets CPU scaling and idle governors, computes thread count from device count and sibling CPUs, then executes `taskset -c ... t/io_uring ...`.

State and persistence: it writes to `/sys/block/*/queue/*`, CPU frequency governor state, and CPU idle governor state. It does not restore prior settings. Output is printed to stdout/stderr only.

Dependencies and integration points: requires bash, root, `t/io_uring`, `lscpu`, `taskset`, `cpupower`, `dmidecode`, common coreutils, and optionally `nvme`, `journalctl`, `getenforce`, kernel config files, and NVMe sysfs topology. It is a manual tuning and benchmark helper rather than a fiotestlib unit.

Risks and test signals: risks include persistent host tuning changes, shell word-splitting around unquoted paths, assumptions about NVMe sysfs `address` and PCI locality, and failure on systems without cpupower or SELinux tools. The main signal is successful command execution and printed system/device context; warnings identify non-fatal missing optimizations such as disabled NVMe poll queues.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/one-core-peak.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/random_seed.py -->
# sources/test-tools/fio/t/random_seed.py

Purpose: regression tests for fio random seed semantics. It ensures `randseed` overrides repeat settings, repeat-enabled runs are deterministic, and repeat-disabled runs produce different seeds unless an explicit seed is supplied.

Important APIs and types: `FioRandTest` extends `FioJobCmdTest`, runs the null ioengine with `--debug=random`, and extracts `rand_seeds[]` from output. `TestRR` keeps class-level seed lists for `[all]randrepeat` values 0 and 1. `TestRS` keeps a class-level dictionary keyed by explicit `randseed`.

Control flow: `main()` parses common run controls, creates an artifact directory, resolves fio, builds a 17-case test list, and calls `run_fio_tests()`. Each case captures debug output. `TestRR.check_result()` stores the first seed sequence for a repeat mode and compares later runs for expected equality or inequality. `TestRS.check_result()` does the same per explicit seed and also compares against other explicit seeds.

State and persistence: class variables persist seed baselines across test cases in the same process. Artifacts include fio output files under the run directory. The tests use null I/O and do not modify external storage.

Dependencies and integration points: depends on fio debug output format, Python 3, fiotestlib, and the umbrella runner. `run-fio-tests.py` registers this as executable test 1013.

Risks and test signals: parsing is fragile if debug line wording changes, and `get_rand_seeds()` silently proceeds if `FIO_RAND_NR_OFFS` is not found. The central success signal is matching or non-matching seed arrays according to repeat and explicit seed rules, plus the underlying fio process success.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/random_seed.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/read-to-pipe-async.c -->
# sources/test-tools/fio/t/read-to-pipe-async.c

Purpose: standalone latency experiment that reads a file in blocks and writes it to stdout while avoiding coordinated omission. If a read does not finish within a configured threshold, later reads can be issued by additional one-off threads so slow requests do not stop new submissions.

Important APIs and types: core structs are `stats`, `thread_data`, `writer_thread`, `reader_thread`, and `work_item`. Timing helpers include `utime_since()`, `add_lat()`, `plat_val_to_idx()`, `plat_idx_to_val()`, `calc_percentiles()`, and `show_latencies()`. Work scheduling is handled by `queue_work()`, `reader_fn()`, `reader_one_off()`, `reader_work()`, `writer_fn()`, `write_work()`, and `prune_done_entries()`.

Control flow: `main()` parses `-f`, `-b`, `-t`, and `-w`, opens and stats the input file, initializes reader and writer thread state, then loops over file blocks. For each block it allocates a `work_item`, queues it, waits up to `max_us` on the item's condition, and advances offsets regardless of whether the read completed. Finished reads are written in sequence by a separate writer thread by default. Shutdown waits for reader and writer completion, prints read/write latency percentiles and rates, and closes the file.

State and persistence: heap-allocated buffers and work items move through flists protected by pthread locks. Latency histograms use atomic increments. Output data is streamed to stdout; metrics and threshold violations go to stderr. No files are written by the program itself.

Dependencies and integration points: depends on pthreads, POSIX file APIs, fio internal `flist.h`, `log.h`, compiler helpers, and optional `CONFIG_PTHREAD_CONDATTR_SETCLOCK`. It is built as an auxiliary C tool rather than a Python harness.

Risks and test signals: inline writing is explicitly described as broken. There is careful sequence ordering for the separate writer, but memory cleanup depends on `prune_done_entries()` progress during loop and writer shutdown. The code assumes full writes to stdout and asserts otherwise. Signals are latency percentile output, over-threshold counts, read/write rates, and non-zero exits for option/open/stat failures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/read-to-pipe-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/readonly.py -->
# sources/test-tools/fio/t/readonly.py

Purpose: compact fio option test for `--readonly`. It confirms read workloads are allowed while write and trim workloads fail when `--readonly` is provided either before or after job options, and that all three workloads run without `--readonly`.

Important APIs and types: `FioReadOnlyTest` extends `FioJobCmdTest` and constructs a null-engine, one-second, time-based command. `TEST_LIST` defines nine cases with `SUCCESS_DEFAULT` or `SUCCESS_NONZERO` expectations.

Control flow: `main()` parses fio path and run filters, creates an artifact directory, resolves fio, then calls `run_fio_tests()`. `setup()` inserts `--readonly` at the beginning when `readonly-pre` is present, appends it when `readonly-post` is present, and otherwise omits it.

State and persistence: the null ioengine means no storage is modified. Only fiotestlib artifacts are written.

Dependencies and integration points: depends on Python, fio, fiotestlib, and fiotestcommon success constants. It is included in `run-fio-tests.py` as executable test 1003.

Risks and test signals: the main risk is that the test checks exit status only and not specific error messages, so it detects regressions in allow/fail behavior but not diagnostics. Success is the expected pass/fail matrix across read, write, trim, and option position.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/readonly.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/run-fio-tests.py -->
# sources/test-tools/fio/t/run-fio-tests.py

Purpose: umbrella test launcher for fio's Python/job-file/executable regression tests. It centralizes the test manifest, environment construction, requirement checking, artifact directory setup, pass-through arguments, and final failure exit code.

Important APIs and types: specialized `FioJobFileTest_*` classes extend `FioJobFileTest` for job-specific assertions around JSON totals, latency fields, offset logs, trimwrite pairing, log file formats, pattern files, and random offset distribution. It imports `FioExeTest`, `FioJobFileTest`, `run_fio_tests`, and all `fiotestcommon` requirement and success constants. `TEST_LIST` maps numeric IDs to job files or executables with expected status and requirements.

Control flow: custom classes override `check_result()` or `setup()` to inspect artifacts after the base class validates fio execution. `main()` parses root, fio path, artifacts, skip/run-only, requirement bypass, pass-through arguments, NVMe character device, cleanup, and debug settings. It resolves `fio_root` and `fio_path`, warns if fio is missing, creates `fio-test-*`, optionally initializes `Requirements`, builds `test_env`, and delegates execution to `run_fio_tests()`.

State and persistence: artifacts are created under a timestamped root and may be cleaned for passing tests when requested through the shared library. Some tests generate pattern files or parse per-job logs in test directories. The manifest itself is static, but pass-through arguments are stored in `test_env`.

Dependencies and integration points: depends on Python, statsmodels runs test, fiotestlib, fiotestcommon, platform-specific requirements, job files under `t/`, compiled helper binaries, optional CUnit, zbd/null_blk support, libaio, io_uring, NVMe character devices, and multiple executable Python harnesses. It is the primary integration point tying many files in this subset into fio CI-style execution.

Risks and test signals: several checks have tolerance bands or statistical assumptions and can be workload or host sensitive. The manifest includes destructive NVMe tests only behind requirements and an explicit `--nvmecdev`. Success signals include base execution status, specialized JSON/log assertions, requirement skip accounting, and process exit equal to the failed test count.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/run-fio-tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/sgunmap-perf.py -->
# sources/test-tools/fio/t/sgunmap-perf.py

Purpose: manual performance comparison tool for fio's `sg` ioengine. It trims a character device with a reference fio build, then compares random read and random write IOPS between candidate and reference builds.

Important APIs and functions: `fulldevice()` runs a full-device trim-like fio job and returns JSON job data. `runtest()` runs one time-based sg workload with configurable rw, queue depth, batch size, block size, and runtime. `runtests()` repeats `runtest()` and returns per-trial total IOPS plus the mean.

Control flow: `main()` parses character device, block device, candidate fio, and reference fio. It trims the character device with the reference build, runs five candidate and five reference random-read trials, then five candidate and five reference random-write trials, printing means and trial lists. The parsed block device argument is present but not used in the executed sequence.

State and persistence: the character device is destructively trimmed and exercised with sg I/O. Results are printed to stdout; no artifacts are written.

Dependencies and integration points: requires Python 2/3 compatibility imports, `six.moves.range`, fio builds that emit JSON, an sg character device, and sufficient permissions. It is not included in the main `run-fio-tests.py` manifest despite a TODO mentioning sgunmap tests.

Risks and test signals: this is performance observation rather than pass/fail validation; it does not exit non-zero for regressions or compare candidate/reference statistically. Risks include destructive device trimming, unused `bdev`, and sensitivity to device state and host load. Signals are printed IOPS means and trial variance.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/sgunmap-perf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/sgunmap-test.py -->
# sources/test-tools/fio/t/sgunmap-test.py

Purpose: destructive functional smoke test for fio's `sg` ioengine unmap/trim behavior. It checks reported iodepth, submit, and complete histograms for read, write, and trim workloads on sg character and block devices.

Important APIs and functions: `check()` validates JSON `iodepth_level`, `iodepth_submit`, and `iodepth_complete` buckets based on device type, queue depth, batch size, and rw mode. `runalltests()` executes read/write/trim for both character and block devices. `runcdevtrimtest()` targets additional character-device trim queue-depth/batch combinations.

Control flow: `main()` parses character device, block device, and fio executable. It first runs multiple high-depth character-device trim cases, then calls `runalltests()` for qd/batch pairs 1/1, 16/2, and 16/16. Each fio invocation emits JSON to stdout, which is parsed immediately and passed to `check()`.

State and persistence: workloads are destructive on supplied devices. The script writes no artifacts and prints parameter lists plus pass/failure details.

Dependencies and integration points: supports Python 2 and 3 via future imports, depends on fio JSON output, sg-capable devices, and permissions. It is a standalone manual test and not part of the umbrella manifest.

Risks and test signals: `check()` prints assertion failures but does not return failure status to callers, so the script may continue and potentially exit success after failed assertions. Bucket thresholds are tied to fio's histogram keys (`4`, exact batch, `>=64`). Success signals are printed `passed` messages and absence of assertion diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/sgunmap-test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/sprandom.py -->
# sources/test-tools/fio/t/sprandom.py

Purpose: fio `sprandom` feature tests. It validates accepted sparse-random configurations and expected failures for incompatible random generators, random-map settings, read mode, too many regions, and chunk sizes equal to the whole file.

Important APIs and types: `FioSPrandomTest` extends `FioJobCmdTest`. `SPRANDOM_OPT_LIST` defines options copied from test dictionaries into fio arguments, including `spr_op`, `spr_num_regions`, `spr_cs`, `size`, `norandommap`, `random_generator`, and `rw`.

Control flow: `main()` parses fio path and test filters, creates a timestamped artifact root, builds `test_env`, and runs `TEST_LIST`. `setup()` uses libaio, direct I/O, `iodepth=16`, `sprandom=1`, a fixed filename, and a configurable `bs` parameter, defaulting to `rw=randwrite` if not specified.

State and persistence: it creates or overwrites `sprandom_testfile` in the current working directory via fio and writes fiotestlib artifacts. No explicit cleanup is performed in this script.

Dependencies and integration points: requires Linux/libaio according to the umbrella test requirements, Python, fio sprandom support, fiotestlib, and fiotestcommon success constants. `run-fio-tests.py` registers it as executable test 1019.

Risks and test signals: the script checks process success/failure rather than distribution quality. The fixed filename can collide with concurrent runs in the same directory. Success signals are the expected exit status for each valid or invalid option combination.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/sprandom.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/steadystate_tests.py -->
# sources/test-tools/fio/t/steadystate_tests.py

Purpose: direct functional and parser tests for fio steady-state detection. It verifies parse-time debug messages for `--ss` options and runtime JSON steady-state fields for null-engine read workloads.

Important APIs and functions: `check()` recalculates either slope or maximum deviation over fio's steady-state data for IOPS or bandwidth, in absolute or percent terms, using SciPy linear regression for slope mode. The main block performs all parsing and workload tests without fiotestlib classes.

Control flow: after parsing a fio executable path, it runs parse-only commands and searches debug output for expected strings. It then defines several read workload scenarios, invokes fio with JSON output files, loads each JSON file, and for every reported job checks attained/not-attained state, minimum runtime versus ramp/duration, criterion equality, and threshold comparison. It prints per-job pass/fail lines and exits with the failure count.

State and persistence: writes `steadystate_jobN.json` files in the current directory and leaves them behind. It has no external storage side effects because it uses the null ioengine.

Dependencies and integration points: requires Python with SciPy, fio JSON output, and subprocess access. It is invoked by `run-fio-tests.py` as executable test 1004.

Risks and test signals: comments acknowledge limited coverage: option parsing and read tests only. Runtime tolerance and steady-state behavior can be sensitive to timing, though null engine reduces variance. Success signals are matching parser messages, JSON criterion recalculation, correct runtime behavior, and final zero failure exit.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/steadystate_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/stest.c -->
# sources/test-tools/fio/t/stest.c

Purpose: standalone stress test for fio's smalloc allocator. It repeatedly allocates random small buffers up to an aggregate limit, verifies zeroed memory from `scalloc()`, checks list/magic integrity, frees entries, and interleaves larger allocations during the free phase.

Important APIs and types: `struct elem` stores guard magic values, an intrusive `flist_head`, and allocation size. `do_rand_allocs()` drives allocation/free validation. It uses fio internal `scalloc()`, `sfree()`, `sinit()`, `smalloc_debug()`, `cleanup()`, `flist` helpers, `arch_init()`, and `debug_init()`.

Control flow: `main()` initializes architecture, smalloc, and debug state, calls `do_rand_allocs()`, prints smalloc debug information, cleans up, and returns the error count. `do_rand_allocs()` repeats `LOOPS` rounds, optionally reseeds with `STEST_SEED`, fills a global list until `MAXSMALLOC`, validates zero fill, assigns magic markers, then frees while checking magic and trying `LARGESMALLOC` allocations.

State and persistence: all state is in smalloc-managed memory and a static list. No files are written. The allocator global state is initialized and cleaned in-process.

Dependencies and integration points: built against fio internals (`smalloc.h`, `flist.h`, `arch.h`, `debug.h`). It is registered in `run-fio-tests.py` as executable test 1005 with `SUCCESS_STDERR`.

Risks and test signals: assertions catch list corruption, while explicit checks count allocation failure and non-zeroed memory. The test is memory intensive, up to roughly 120 MiB per round plus large allocation probes. Success is zero return status, expected diagnostic output, and no assertion abort.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/stest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/strided.py -->
# sources/test-tools/fio/t/strided.py

Purpose: regression tests for `zonemode=strided`. It verifies that random reads stay inside the current zone/range and, when random mapping or LFSR makes uniqueness meaningful, that each block in a range is touched exactly once before wrap.

Important APIs and types: `StridedTest` extends `FioJobCmdTest`. `setup()` builds fio commands with `--zonemode=strided`, `--log_offset=1`, `--write_iops_log`, and zone size/range/block options. `check_result()` parses the IOPS log lines supplied by fiotestlib and validates offsets.

Control flow: `main()` creates artifacts, resolves fio, optionally stats a user-supplied target file/device, populates each test with either a real filename/filesize or null-engine filesize, then calls `run_fio_tests()`. The matrix covers randommap-enabled, LFSR, and `norandommap` cases with equal, larger, and smaller `zonesize` versus `zonerange`, plus optional offsets.

State and persistence: with no `--dut`, null engine avoids storage changes. With a supplied target file/device, the script performs random reads only. It writes logs and output artifacts under the artifact root.

Dependencies and integration points: depends on Python, fio, fiotestlib, and optionally a target file/device. It is included in `run-fio-tests.py` as executable test 1006.

Risks and test signals: some `io_size` constants appear to use `256*1024*204`, likely intentional historical coverage or a typo that reduces size below the associated `size`. `check_result()` prints and returns on failures without explicitly setting `self.passed = False` in several branches, so some detected violations may not fail the test. Intended success signals are offsets within zone bounds and complete unique coverage where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/strided.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/t64-switch.sh -->
# sources/test-tools/fio/t/t64-switch.sh

Purpose: shell regression test proving fio automatically switches to `tausworthe64` when the file-size/block-size space exceeds the default 32-bit random generator. It compares duplicate offset counts between forced 32-bit and automatic generator selection.

Important operations: it accepts optional fio path and IO count, runs two null-engine random-read fio commands over a 1T file with 1-byte blocks and `--norandommap`, parses `--debug=io` completion offsets with `grep`, `cut`, `sort`, `uniq -D`, and `wc -l`, then computes a duplicate-count ratio.

Control flow: `t32` is measured with `--random_generator=tausworthe`; `t64` is measured without forcing the generator. If `t64` is non-zero the ratio is `t32/t64`, otherwise it is `t32`. The script prints both counts and passes if the ratio is at least 10.

State and persistence: uses the null ioengine and writes no persistent files. It can be CPU-heavy because the default count is one million IOs and debug output is piped through sorting.

Dependencies and integration points: requires bash, fio, and common Unix text tools. It is invoked by `run-fio-tests.py` as executable test 1020 on non-Windows systems.

Risks and test signals: debug-output format changes can break parsing. The output label says `tausworthe62`, a typo for 64. Statistical duplicate ratios may vary with count, but the threshold is intentionally coarse. Success signal is `result: pass` and exit 0; otherwise it prints `result: fail` and exits 1.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/t64-switch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/time-test.c -->
# sources/test-tools/fio/t/time-test.c

Purpose: arithmetic exploration and regression test for converting CPU clock ticks to nanoseconds using multiplier/shift strategies, two-stage conversion, seqlock-updated conversion, and native 128-bit arithmetic.

Important APIs and types: conversion modes are encoded in an enum (`CLOCK64_MULT_SHIFT`, `CLOCK64_EMULATE_128`, `CLOCK64_2STAGE`, `CLOCK64_LOCK`, `CLOCK128_MULT_SHIFT`). Core functions are `calc_mult_shift()`, `_get_nsec()`, `get_nsec()`, `update_clock()`, `discontinuity()`, and `test_clock()`. It uses fio's `lib/seqlock.h` for the lock-based mode.

Control flow: `main()` allocates a large nanosecond scratch array, then calls `test_clock()` for `CLOCK64_LOCK` across several cycle-per-usec frequencies and expected tick/nsec deltas. `test_clock()` computes multipliers and shifts, checks conversion at maximum and representative times, and can run discontinuity scans when not in fast mode. In the current main path, fast tests are enabled, so full billion-entry scans are skipped.

State and persistence: global conversion parameters, seqlock state, and scratch memory are updated in-process. No files are read or written.

Dependencies and integration points: depends on a compiler supporting `__uint128_t` for the 128-bit path, fio seqlock helpers, and enough memory to allocate `LEN * sizeof(unsigned long long)` even though fast mode does not heavily use it. It is an auxiliary C test/tool rather than registered in the shown umbrella manifest.

Risks and test signals: the emulated 128-bit multiply/divide helpers are explicitly not implemented, so that mode is unsafe if exercised. The huge allocation can be wasteful. Assertions enforce expected continuity constraints. Success is normal exit after printed conversion diagnostics and no assertion failures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/time-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/verify-state.c -->
# sources/test-tools/fio/t/verify-state.c

Purpose: diagnostic utility that decodes fio verify-state files into plain text. It validates the file header size and CRC before printing per-thread verify state and inflight write numbers.

Important APIs and types: it consumes `struct verify_state_hdr`, `struct thread_io_list`, and inflight entries from `verify-state.h`. `show_s()` prints one thread record. `show()` performs little-endian conversion for each variable-length thread record. `show_verify_state()` validates header metadata and CRC using `fio_crc32c()`. `show_file()` handles file I/O.

Control flow: `main()` initializes debugging, requires at least one state-file path, and processes files in order until one fails. `show_file()` opens, stats, allocates a buffer, reads the entire file, and calls `show_verify_state()`. The decoder checks header size, verifies CRC over the payload, rejects unsupported versions, then iterates through thread records using `__thread_io_list_sz(depth)`.

State and persistence: read-only over input files. It allocates a whole-file buffer per state file and frees it after printing. No output files are written.

Dependencies and integration points: depends on fio internals for logging, OS endian helpers, verify-state layout, CRC32C, and debug initialization. It is useful alongside fio verify-state-save features and tests, but it is not shown as a direct umbrella test entry in this subset.

Risks and test signals: malformed files with inconsistent sizes stop decoding cleanly, but the loop in `show()` assumes the remaining payload is exactly a sequence of valid variable-length records. Success signals are printed version/size/CRC plus thread details; failures produce log errors for open/stat/read, short read, size mismatch, CRC mismatch, or unsupported version.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/verify-state.c -->
