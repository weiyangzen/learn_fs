# Research Group: subset-b-009234

This grouped report covers the requested fio test, helper, option, timing, error, and tooling files. Each section preserves the original source path and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/verify-trim.py -->
# sources/test-tools/fio/t/verify-trim.py

## Purpose
`verify-trim.py` is a Python 3 fio regression harness for the verify-trim path. It checks that fio emits trim operations alongside verified writes for sequential and random write workloads, validates trim count accounting from JSON output, and verifies that readonly mode rejects trim-producing configurations.

## Important APIs, Types, and Functions
The main type is `VerifyTrimTest`, a `fiotestlib.FioJobCmdTest` subclass. `setup()` builds a single fio command named `verifytrim` with `--verify=md5`, a caller-selected target filename, `--rw`, `--trim_percentage`, `--trim_backlog`, and optional entries from `VERIFY_OPT_LIST`. `check_result()` delegates base result parsing, then for JSON output compares `jobs[0].trim.total_ios` against `write.total_ios * trim_percentage / 100` with a 10 percent tolerance. `parse_args()` exposes fio path, fio root, artifact root, skip/run-only controls, requirement skipping, and `--dut`. `main()` provisions artifacts, resolves fio paths, checks requirements, optionally creates a Linux `null_blk` device with discard support, injects the chosen device into every test case, and runs `run_fio_tests()`.

## Control Flow and State
State is concentrated in `TEST_LIST` dictionaries and the artifact directory created for each run. If no device is provided, `main()` removes any existing `null_blk`, loads `null_blk memory_backed=1 discard=1`, uses `/dev/nullb0`, and removes the module afterward. Each test mutates `test['fio_opts']['filename']` before dispatch.

## Dependencies and Integration Points
It imports `FioJobCmdTest`, `run_fio_tests`, `SUCCESS_NONZERO`, and `Requirements` from fio's Python test framework. Runtime integration depends on Linux, `sudo modprobe`, `/dev/nullb0`, the fio binary, and JSON output shape from fio.

## Risks and Test Signals
Risks include privilege requirements, global `null_blk` module churn, tolerance masking small trim-count bugs, and cleanup not running if the process is killed hard. Test signals are nonzero exit count, base `FioJobCmdTest` pass/fail state, stderr/stdout/output dumps on failure, and JSON trim/write totals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/verify-trim.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/verify.py -->
# sources/test-tools/fio/t/verify.py

## Purpose
`verify.py` is the broad fio verify-options regression suite. It exercises checksum methods, verify-only reads, header seed/sequence behavior, async verify, verify backlog, verify interval/offset, pattern verification, random/sequential workloads, and deliberate corruption detection.

## Important APIs, Types, and Functions
`VerifyTest` wraps straightforward fio invocations and logs failed stderr/stdout/output artifacts. `VerifyCSUMTest` creates a multi-phase fio job: layout, expected-success verify-only/read phases, a `mangle` random write phase that corrupts data, and expected-failure verify-only/read phases. Its `check_result()` expects six named jobs and verifies corruption failures report `errno.EILSEQ`, except for `verify=null`.

Helper functions mutate shared test dictionaries before calling `run_fio_tests()`: `verify_test()` runs the base matrix across data directions and checksums; `verify_test_csum()` configures corruption tests and expected success semantics; `verify_test_header()` builds a matrix for mode and sequence behavior; `verify_test_vpi()` covers `verify_pattern_interval`. `CSUM_LIST1` is the default small checksum set, while `CSUM_LIST2` is selected by `--complete`.

## Control Flow and State
`main()` creates a top-level artifact directory, resolves fio root and binary, checks requirements, maps placeholder engines to platform-specific async/sync engines, then loops through products of directions, checksum methods, mangle block sizes, header modes/sequences, and pattern interval parameters. Read-only workloads reuse artifact directories from earlier write workloads so data exists for verification.

## Dependencies and Integration Points
The script depends on fio's test framework, platform-specific engine names, JSON output, `errno.EILSEQ`, and artifact-directory naming conventions used to locate prior write data. Some tests require four CPUs and skip on macOS.

## Risks and Test Signals
The suite mutates global `TEST_LIST*` structures repeatedly, so stale options must be explicitly removed. It can be long-running, especially with `--complete`. Risks include platform-specific engine differences, flakiness from CPU affinity or macOS file behavior, and reliance on directory-name replacement. Strong test signals include named job validation, expected error numbers, skipped counts, and exhaustive matrix coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/verify_state_save.py -->
# sources/test-tools/fio/t/verify_state_save.py

## Purpose
`verify_state_save.py` provides superficial but practical regression coverage for fio's verify state persistence. It confirms that jobs can save verification state, then reload that state in verify-only and read modes across synchronous and async engines.

## Important APIs, Types, and Functions
`VerifyStateSaveTest` subclasses `FioJobCmdTest`. `setup()` builds a fio job named `verify-state` and passes through many io_uring, verification, block-size, rate, offset, directory, aux-path, and workload options when present. `check_result()` extends base validation by checking that JSON I/O counters match the expected direction set for the configured `rw`: reads only, writes only, read/write for verified writes, trim only, or trim/write.

`TEST_LIST` defines nine base random-write/random-read-write workloads over `TEST_SIZE=4M`, combining default, `verify_policy=completed`, and `verify_policy=fsynced` with optional `fsync=16` and `rwmixread=70`.

## Control Flow and State
`main()` creates an artifact root and resolves fio. For each platform-selected async and sync engine, it runs three phases. First it writes data with `verify_state_save=1`. Second it runs `verify_state_load=1` plus `verify_only=1`, pointing `directory` and `aux-path` at the saved-state phase using relative paths. Third it changes write modes to read modes and reruns state-load verification, skipping randrw cases that have no pure-read equivalent.

## Dependencies and Integration Points
It integrates with fio's JSON output, verify-state side files under job artifact directories, and `run_fio_tests()`. Platform selection maps Linux to `libaio` and `psync`, Windows to `windowsaio` and `sync`, and other platforms to `posixaio` and `psync`.

## Risks and Test Signals
Because tests mutate shared dictionaries across phases, correct removal of `verify_only`, `verify_state_load`, `directory`, and `aux-path` is essential. Relative directory computation can break if artifact layout changes. Signals are base fio exit status, JSON direction counters, and phase totals for saved, verify-only, and read verification.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/verify_state_save.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/zbd/functions -->
# sources/test-tools/fio/t/zbd/functions

## Purpose
`t/zbd/functions` is a shared Bash library for fio zoned block device tests. It abstracts discovery, geometry parsing, zone operations, capacity accounting, and fio log parsing across Linux `blkzone`, libzbc tools, SCSI inquiry data, NVMe ZNS devices, null_blk, block devices, and SG character devices.

## Important APIs, Types, and Functions
Command variables (`blkzone`, `sg_inq`, `zbc_report_zones`, `zbc_reset_zone`, `zbc_close_zone`, `zbc_info`) are initialized at load time and validated. Capability helpers include `has_command`, `is_nvme_zns`, `is_nullb_with_zone_cap`, `check_blkzone`, and `blkzone_reports_capacity`. Geometry helpers include `first_sequential_zone`, `first_online_zone`, `last_online_zone`, `total_zone_capacity`, `zone_cap_bs`, `max_open_zones`, `max_active_zones`, `min_seq_write_size`, `urswrz`, `zbc_physical_block_size`, and `zbc_disk_sectors`.

Device mutation helpers are `reset_zone()` and `close_zone()`, selecting `blkzone` or libzbc operations. Log helpers `fio_io()`, `fio_read()`, `fio_written()`, and `fio_reset_count()` parse human-readable fio output.

## Control Flow and State
The file is sourced by test scripts and immediately validates tool availability. Many functions depend on globals set by callers, especially `use_libzbc`, `is_zbd`, and `zone_size`. Most outputs are shell-printed values consumed by command substitutions.

## Dependencies and Integration Points
It integrates with `/sys/block`, `/sys/kernel/config/nullb`, SCSI VPD pages via `sg_inq`, `blkzone report/reset/close`, and libzbc report/reset/close/info tools. It is central to `test-zbd-support` and the null_blk/scsi_debug wrappers.

## Risks and Test Signals
Risks include fragile parsing of external command output, mixed hex/decimal handling, assumptions about 512-byte sectors, and global variable dependence. Strong signals are early command availability failures, geometry sanity failures, parsed fio byte counts, and reset-count extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/zbd/functions -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/zbd/run-tests-against-nullb -->
# sources/test-tools/fio/t/zbd/run-tests-against-nullb

## Purpose
`run-tests-against-nullb` orchestrates repeated runs of `t/zbd/test-zbd-support` against many synthetic `null_blk` layouts. It creates conventional, fully zoned, mixed conventional/sequential, zone-capacity-limited, max-open-limited, and max-active-limited configurations.

## Important APIs, Types, and Functions
`cleanup_nullb()` removes configfs nullb devices and unloads/reloads `null_blk`. `create_nullb()` loads the module with `nr_devices=0` and creates `/sys/kernel/config/nullb/nullb0`. `configure_nullb()` writes configfs attributes including block size, size, memory backing, zoned mode, zone size/capacity, conventional-zone count, max open, max active, and optional badblock controls. `show_nullb_config()` prints the active test layout.

`section1()` through `section25()` define the layout matrix. CLI options choose sections, individual test cases, max-open limits, repeat count, write-zone-remainder mode, quit-on-error behavior, list-only mode, and cleanup.

## Control Flow and State
The script discovers feature support from `/sys/kernel/config/nullb/features`, then loops over runs and selected sections. Each section resets globals such as `conv_pcnt`, `zone_size`, `zone_capacity`, `max_open`, and `max_active`, configures nullb, prints the layout, and invokes `./test-zbd-support` with accumulated options against `/dev/nullb0`.

## Dependencies and Integration Points
It requires root-level module and configfs access, the Linux `null_blk` module, and the sibling `test-zbd-support` script. Feature detection controls whether unsupported zone-capacity, conventional-zone, or max-active sections are skipped.

## Risks and Test Signals
Risks include destructive interaction with existing null_blk devices, module unload failure, configfs attribute drift across kernels, and global shell state leaking between sections. Signals are section output, skipped unsupported sections (`rc == 2`), child test return codes, total elapsed time, and optional early stop with `-q`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/zbd/run-tests-against-nullb -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/zbd/run-tests-against-scsi_debug -->
# sources/test-tools/fio/t/zbd/run-tests-against-scsi_debug

## Purpose
`run-tests-against-scsi_debug` prepares a zoned `scsi_debug` device specifically for zbd write-error recovery tests, then runs `test-zbd-support` cases 72 and 73 through multiple access paths.

## Important APIs, Types, and Functions
The script is linear rather than function-oriented. It unloads any existing `scsi_debug`, reloads it with `add_host=1 zbc=host-managed zone_nr_conv=0`, scrapes recent `dmesg` output for the attached SCSI disk name, verifies the block device VPD page mentions `scsi_debug`, locates the matching `scsi_generic` node, and invokes `test-zbd-support`.

## Control Flow and State
State is held in `dev`, `sg`, and `scriptdir`. Three runs are performed: standard engine against `/dev/sdX`, libzbc engine against the block device, and libzbc engine against the SG node. The target tests are `-t 72 -t 73`, which exercise badblock/error-injection recovery paths.

## Dependencies and Integration Points
It depends on root/module access, `modprobe`, kernel `scsi_debug`, `dmesg` output format, sysfs VPD page layout, and the sibling `test-zbd-support`. It integrates with libzbc mode via `-l`.

## Risks and Test Signals
Risks include unreliable device discovery from `dmesg | tail -5`, lack of cleanup after the run, accidental interference with existing scsi_debug instances, and kernel-debugfs availability for later error injection. Signals are VPD verification failure, explicit run banners, and return codes from `test-zbd-support`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/zbd/run-tests-against-scsi_debug -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/t/zbd/test-zbd-support -->
# sources/test-tools/fio/t/zbd/test-zbd-support

## Purpose
`test-zbd-support` is fio's main shell regression suite for zoned block device behavior. It validates zonemode option parsing, sequential-zone read/write semantics, conventional/sequential mixed devices, max-open and max-active accounting, zone reset behavior, trim behavior, verify interaction, write pointer recovery, and error handling across block and libzbc engines.

## Important APIs, Types, and Functions
Harness helpers include `ioengine()`, `set_io_scheduler()`, `run_fio()`, `run_one_fio_job()`, `write_and_run_one_fio_job()`, `run_fio_on_seq()`, `prep_write()`, and log checkers `check_read()`, `check_written()`, `check_reset_count()`, and `check_log()`. Requirement helpers (`require_zbd`, `require_regular_block_dev`, `require_seq_zones`, `require_conv_zones`, `require_max_open_zones`, `require_badblock`, and others) return `SKIP_TESTCASE=255` with `SKIP_REASON`.

The test body is a numbered function suite `test1()` through `test75()`. Families include invalid option rejection, empty-zone reads, direct-I/O enforcement, random/sequential write verification, mixed conventional zone behavior, boundary rounding, `z` suffix parsing, zone reset thresholds, max-open/max-active limits, trim/open-zone accounting, verify backlog, and `continue_on_error` recovery with null_blk/scsi_debug injection.

## Control Flow and State
CLI parsing sets global modes for valgrind, libzbc, reset behavior, write-zone-remainder, selected tests, max-open override, start test, quit-on-error, zbd debug, and io_uring substitution. After sourcing `functions`, startup derives `realdev`, `disk_size`, `first_sequential_zone_sector`, `zone_size`, `sectors_per_zone`, `min_seq_write_size`, `max_open_zones`, `max_active_zones`, `unrestricted_reads`, `zone_cap_bs`, scheduler, and optional zone resets. It then enumerates selected `testN` functions, removes the per-test log, evals the test, classifies PASS/SKIP/FAIL, writes status to the log, and summarizes counts.

## Dependencies and Integration Points
The script depends heavily on `t/zbd/functions`, fio at `../../fio`, `/sys`, `dmsetup` for mapped devices, `blkzone` or libzbc, optional valgrind, timeout, null_blk/scsi_debug error injection, and kernel scheduler controls.

## Risks and Test Signals
Risks include privileged device mutation, fragile parsing of sysfs/tool output, global option arrays affecting tests, use of `eval`, typo-sensitive fio options in individual tests, time-based flakiness, and destructive zone resets. Signals are per-test log files, PASS/SKIP/FAIL classification, grep checks for expected error text, byte-count comparisons, reset-count checks, assertion/crash grep in logs, and aggregate exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/t/zbd/test-zbd-support -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/td_error.c -->
# sources/test-tools/fio/td_error.c

## Purpose
`td_error.c` implements fio thread error classification, default non-fatal error selection, and aggregate error counting.

## Important APIs, Types, and Functions
`td_error_type(enum fio_ddir ddir, int err)` maps `EILSEQ` to verification errors, read directions to read errors, and all other directions to write errors. `td_non_fatal_error(struct thread_data *td, enum error_type_bit etype, int err)` decides whether an error should be ignored/continued based on `td->o.continue_on_error` and `td->o.ignore_error`. If no explicit ignore list exists for an error type, it installs the static default list `{ EIO, EILSEQ }`. `update_error_count()` increments `td->total_err_count` and records the first error.

## Control Flow and State
The only file-local persistent state is `__NON_FATAL_ERR`. `td_non_fatal_error()` mutates `thread_options.ignore_error[etype]` and `ignore_error_nr[etype]` when defaults are needed. Error counts live in `struct thread_data`.

## Dependencies and Integration Points
The file includes `fio.h`, `io_ddir.h`, and `td_error.h`. It is consumed by fio I/O, verify, and error handling paths that need to distinguish read/write/verify error policies.

## Risks and Test Signals
Risks include the default ignore list being shared static memory, all non-read/non-verify directions mapping to write, and callers needing a valid `etype` index. Test signals are `continue_on_error` behavior, `ignore_error` option behavior, first-error reporting, and zbd tests that expect recovery/continue behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/td_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/td_error.h -->
# sources/test-tools/fio/td_error.h

## Purpose
`td_error.h` defines fio's error-type bit ABI for read, write, and verify error handling and declares helper functions implemented in `td_error.c`.

## Important APIs, Types, and Functions
`enum error_type_bit` provides array indexes and bit positions: `ERROR_TYPE_READ_BIT`, `ERROR_TYPE_WRITE_BIT`, `ERROR_TYPE_VERIFY_BIT`, and `ERROR_TYPE_CNT`. `enum error_type` provides bit masks used by options such as `continue_on_error`: `ERROR_TYPE_NONE`, `ERROR_TYPE_READ`, `ERROR_TYPE_WRITE`, `ERROR_TYPE_VERIFY`, and broad `ERROR_TYPE_ANY`. Function declarations expose `td_error_type()`, `td_non_fatal_error()`, and `update_error_count()`.

## Control Flow and State
This header has no runtime control flow. Its state significance is ABI-like: `ERROR_TYPE_CNT` sizes arrays in `thread_options`, while the bit values define persisted option semantics and mask behavior.

## Dependencies and Integration Points
It includes `io_ddir.h` for data direction types and is included by `thread_options.h` and error-handling C files. The enum values must remain consistent with option parsing, packed thread option structures, and network/client/server conversions.

## Risks and Test Signals
Changing enum order or count can break option arrays, packed conversions, and compatibility. `ERROR_TYPE_ANY=0xffff` intentionally exceeds the three current bits. Signals include build failures, option conversion tests, and runtime behavior of `continue_on_error` and `ignore_error`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/td_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/thread_options.h -->
# sources/test-tools/fio/thread_options.h

## Purpose
`thread_options.h` is fio's central job-option schema. It defines in-memory `struct thread_options`, packed/network `struct thread_options_pack`, option-related enums and helper structs, and conversion/parser function prototypes.

## Important APIs, Types, and Functions
Enums include `fio_zone_mode`, `fio_memtype`, and `dedupe_mode`. Helper structs model split syntax: `split`, `split_prio`, `bssplit`, and `zone_split`. `struct thread_options` contains the live option set used by jobs: filenames, ioengine, direction, sizes, block sizes, verification, randomization, logs, rate limiting, cgroups, flow, zbd controls, FDP, latency, and many booleans/counters. `struct thread_options_pack` is the packed representation used for client/server or cross-endian conversion, with fixed-size string fields and trailing `patterns[]`.

Declared APIs include `convert_thread_options_to_cpu()`, `thread_options_pack_size()`, `convert_thread_options_to_net()`, `fio_test_cconv()`, `options_default_fill()`, `str_split_parse()`, `split_parse_ddir()`, and `split_parse_prio_ddir()`.

## Control Flow and State
The file is declarative, but it defines persistence and compatibility state. `set_options` tracks which options were set; `OPT_MAGIC` validates option structs; fixed maxima such as `BSSPLIT_MAX`, `ZONESPLIT_MAX`, `ERROR_STR_MAX`, and `FIO_TOP_STR_MAX` bound packed data. The packed layout is marked `__attribute__((packed))`, making field order and widths highly sensitive.

## Dependencies and Integration Points
It includes architecture, OS, option, stat, time, pattern, and error headers. It is integrated with option parsing, job creation, network protocol conversion, JSON/status reporting, zbd code, verification, logging, and ioengine-specific behavior.

## Risks and Test Signals
Risks are high: adding/reordering fields can break client/server compatibility, endian conversion, default filling, and option persistence. Pointer fields in live options require explicit packing. Test signals include cconv tests, client/server option transfer, build-time struct users, and broad fio regression tests that exercise specific option families.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/thread_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tickmarks.c -->
# sources/test-tools/fio/tickmarks.c

## Purpose
`tickmarks.c` computes human-friendly graph tick labels for fio plotting code using a Graphics Gems-style nice-number algorithm.

## Important APIs, Types, and Functions
`nicenum(double x, int round)` chooses 1, 2, 5, or 10 times a power of ten for ranges and tick spacing. `calc_tickmarks(double min, double max, int nticks, struct tickmark **tm, int *power_of_ten, int use_KMG_symbols, int base_offset)` computes graph min/max, spacing, fractional formatting, allocates an array of `struct tickmark`, fills values and labels, then calls `shorten()`. `shorten()` detects common trailing zeros and optionally replaces them with K/M/G/P/E suffixes, adjusting `power_of_ten`.

## Control Flow and State
The caller owns the allocated `*tm` array and must free it. `power_of_ten` is an out-parameter communicating scale shortening. `shorten()` edits label strings in place.

## Dependencies and Integration Points
It depends on libm (`floor`, `ceil`, `log10`, `pow`), C allocation/string APIs, and `tickmarks.h`. It is used by fio graph-generation components that need stable axis labels.

## Risks and Test Signals
Risks include undefined behavior when `min == max`, `nticks < 2`, nonpositive ranges, allocation failure not checked, and fixed 20-byte label buffers. The inactive `#if 0` main function documents manual test cases. Signals are plotted axis readability, no crashes for typical ranges, and correct suffix scaling.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tickmarks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tickmarks.h -->
# sources/test-tools/fio/tickmarks.h

## Purpose
`tickmarks.h` exposes the tick mark data structure and calculation entry point used by fio graphing code.

## Important APIs, Types, and Functions
`struct tickmark` contains a numeric `double value` and a fixed `char string[20]` label. `calc_tickmarks()` returns the number of tick marks and allocates/fills an array through `struct tickmark **tm`; it also returns the selected power-of-ten scaling and supports K/M/G-style symbols.

## Control Flow and State
This header has no executable control flow. The ownership contract is important: callers receive heap storage and are responsible for releasing it.

## Dependencies and Integration Points
It is included by `tickmarks.c` and any graph/report code that consumes generated ticks. The struct string size is part of the interface.

## Risks and Test Signals
Risks include buffer-size constraints for labels, caller leaks if `tm` is not freed, and lack of documentation for invalid ranges. Signals are compile compatibility and correct axis labels in generated plots.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tickmarks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/time.c -->
# sources/test-tools/fio/time.c

## Purpose
`time.c` implements fio timing helpers, sleep/spin behavior, global genesis time, job epoch fields, and ramp-period state transitions.

## Important APIs, Types, and Functions
`timespec_add_msec()` mutates a timespec by milliseconds. `usec_spin()` and `cycles_spin()` busy-wait for fine-grained timing. `usec_sleep()` combines nanosleep with spin compensation based on measured `ns_granularity`, waking periodically to observe `td->terminate`. `time_since_genesis()`, `mtime_since_genesis()`, and `utime_since_genesis()` report elapsed time from global `genesis`.

Ramp APIs include `in_ramp_period()`, global `ramp_period_enabled`, `ramp_period_check()`, `ramp_period_over()`, and `td_ramp_period_init()`. They support ramp by time or bytes, group-reporting semantics, offload parent/child propagation, and stats reset at ramp completion. `fio_time_init()` initializes clock support and measures nanosleep granularity. `set_genesis_time()`, `set_epoch_time()`, and `fill_start_time()` initialize job timestamps.

## Control Flow and State
File-static state includes `genesis` and `ns_granularity`. Ramp state lives in each `thread_data.ramp_period_state` and global `ramp_period_enabled`. `ramp_period_check()` iterates all thread data, optionally locks async workers while reading I/O bytes, and marks jobs/groups finishing.

## Dependencies and Integration Points
It depends on `fio.h`, clock helpers, thread iteration macros, thread runstate transitions, stats reset functions, and async locking. It affects runtime accounting, logs, ETA, ramp exclusion, and job start epoch output.

## Risks and Test Signals
Risks include busy-spin CPU burn, nanosleep granularity over/under-compensation, group byte accounting depending on thread iteration order, and ramp-size consistency enforcement. Signals include ramp-time/ramp-size tests, stable job_start/alternate_epoch log fields, and absence of hangs during termination.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/fio.service -->
# sources/test-tools/fio/tools/fio.service

## Purpose
`fio.service` is a minimal systemd unit for running fio in server mode as a system service.

## Important APIs, Types, and Functions
The unit declares `Description=Flexible I/O tester server`, starts after `network.target`, runs as `Type=simple`, and executes `/usr/bin/fio --server`. Installation targets `multi-user.target`.

## Control Flow and State
Systemd owns the lifecycle. There is no explicit restart policy, environment, user, working directory, or sandboxing. The service state is the fio server process.

## Dependencies and Integration Points
It integrates with systemd and expects fio to be installed at `/usr/bin/fio`. It exposes fio's server mode to clients over fio's normal server protocol.

## Risks and Test Signals
Risks include running as the default systemd service user, typically root if installed system-wide, no hardening directives, no explicit network readiness beyond `After=network.target`, and path mismatch for custom fio installs. Signals are `systemctl status fio`, journal output, and client ability to connect to the fio server.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/fio.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/fio_generate_plots -->
# sources/test-tools/fio/tools/fio_generate_plots

## Purpose
`fio_generate_plots` is a shell utility that turns fio log files into SVG graphs using gnuplot. It generates latency, IOPS, submission latency, completion latency, and bandwidth plots.

## Important APIs, Types, and Functions
The script takes a required subtitle/title and optional `xres yres`. It finds `gnuplot`, sets many default gnuplot snippets for colors, terminal, fonts, axes, range, grid, key, and source label, then defines `plot()`. `plot()` scans for files matching `*_<tag>.log` and `*_<tag>.*.log`, extracts a queue-depth label from the filename, builds a gnuplot `plot` expression using time column `$1/1000` and scaled value column `$2/SCALE`, and writes `$TITLE-$FILETYPE.svg`.

## Control Flow and State
Global shell variables hold title, resolution, `SAMPLE_DURATION`, default plot commands, and the currently accumulated `PLOT_LINE`. The script calls `plot()` five times with different tags and y-axis scales.

## Dependencies and Integration Points
It depends on POSIX shell, gnuplot 4.4+, fio log naming conventions, and SVG-capable viewers. It consumes fio logs created by `write_*_log` options.

## Risks and Test Signals
Risks include unquoted filename/title handling, brittle queue-depth extraction, a likely unused/undefined `DEFAULT_GRID_LINE` variable in `DEFAULT_OPTS`, hard-coded data-source label, and exit on first missing plot family. Signals are generated SVG files and gnuplot errors.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/fio_generate_plots -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/fio_jsonplus_clat2csv -->
# sources/test-tools/fio/tools/fio_jsonplus_clat2csv

## Purpose
`fio_jsonplus_clat2csv` converts fio `json+` latency histogram bins into per-job CSV files, including per-duration counts, cumulative counts, and percentiles for read, write, and trim submission/completion/total latencies.

## Important APIs, Types, and Functions
Constants `DDIR_LIST` and `LAT_LIST` define the output matrix. `parse_args()` accepts source JSON, destination stub, `--debug`, and `--validate`. `percentile()` computes cumulative fraction for a bin index. `more_bins()` drives a multi-list merge across latency streams. `get_csvfile()` appends `_jobN` to the destination. `validate()` reconstructs bins from generated CSV files and compares them to JSON bin dictionaries. `main()` loads JSON, builds column labels, optionally validates, otherwise creates one CSV per job.

## Control Flow and State
For each job, the script builds sorted `[nsec, count]` lists for each direction/latency pair, precomputes cumulative totals, then repeatedly emits the smallest remaining latency across all streams. Missing streams produce blank CSV fields.

## Dependencies and Integration Points
It depends on Python 2/3 compatibility helpers from `six`, fio `json+` output shape, and filesystem access for generated CSVs. It integrates with validation workflows that compare CSV output back to source JSON.

## Risks and Test Signals
Risks include assuming `jsondata['jobs'][job][ddir]` exists for all directions, large memory use for huge histograms, exact string comparison of CSV headers in validation, and a hard-coded large initial `min_lat`. Signals are generated `_jobN.csv` files, validation messages, and assertion/mismatch failures.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/fio_jsonplus_clat2csv -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/fiograph/fiograph.conf -->
# sources/test-tools/fio/tools/fiograph/fiograph.conf

## Purpose
`fiograph.conf` configures colors, labels, styles, and ioengine-specific option lists for the `fiograph.py` fio-job visualization tool.

## Important APIs, Types, and Functions
The `[fio_jobs]` section defines Graphviz HTML label templates, colors, box shape/style, cluster style, and title/item formatting. Sections such as `[exec_prerun]`, `[exec_postrun]`, `[numjobs]`, and `[ioengine]` override colors or display formats. Numerous `[ioengine_*]` sections list engine-specific options that should be highlighted near the ioengine line rather than treated as generic job options.

## Control Flow and State
This is declarative configuration parsed by `configparser.RawConfigParser`. Whitespace-separated `specific_options` values are split by `fiograph.py`.

## Dependencies and Integration Points
It is tightly coupled to `fiograph.py` option lookup names and to fio ioengine option names. It also embeds Graphviz HTML-like label syntax, so malformed templates can break rendering.

## Risks and Test Signals
Risks include stale ioengine option lists as fio evolves, double spaces creating empty option names, Graphviz HTML syntax errors, and color/style assumptions. Signals are visual output from `fiograph.py`, absence of config lookup failures, and correct highlighting of engine-specific options.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/fiograph/fiograph.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/fiograph/fiograph.py -->
# sources/test-tools/fio/tools/fiograph/fiograph.py

## Purpose
`fiograph.py` renders fio job files into Graphviz diagrams showing jobs, execution groups, selected options, dependencies, runtime/size self-loops, and a legend.

## Important APIs, Types, and Functions
Config accessors (`get_section_option`, `get_config_option`, color/style getters, `get_specific_options`) mediate fio and visualization config. `render_option()` appends option rows unless the option is skipped or already represented graphically. `render_options()` builds each job node's HTML label, handling `numjobs`, early options, ioengine-specific options, generic sorted options, and late options. `render_section()` adds a node plus runtime or size self-loop. `create_sub_graph()` creates clustered execution groups. `create_legend()` builds a Graphviz legend. `fio_to_graphviz()` parses a fio file and constructs the full graph. `setup_commandline()` and `main()` handle CLI and output file movement.

## Control Flow and State
Globals `config_file` and `fio_file` hold parsed config. `main()` resolves config path, renders to a UUID temporary filename, renames the image to the requested/default output, and optionally preserves the `.gv` source. Job dependencies are inferred from `stonewall`, `wait_for_previous`, and `wait_for`, with clusters representing groups of parallel jobs.

## Dependencies and Integration Points
It depends on Python `graphviz`, Graphviz `dot`, `configparser`, fio job-file INI syntax, and `fiograph.conf`. It uses `RawConfigParser` with `default_section="global"` for fio files.

## Risks and Test Signals
Risks include a Python logic bug where `('stonewall' or 'wait_for_previous') in section` only checks `stonewall`, HTML label injection from unescaped option values, dependency references to missing jobs, and output rename failures. Signals are generated image files, optional `.gv` content, and Graphviz/render exceptions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/fiograph/fiograph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/fiologparser.py -->
# sources/test-tools/fio/tools/fiologparser.py

## Purpose
`fiologparser.py` parses one or more fio time-series logs with non-uniform sample spacing and reports interval sums, averages, full per-series values, all-stat percentiles, or a weighted overall default value.

## Important APIs, Types, and Functions
`parse_args()` defines interval, divisor, output modes, and input files. Output helpers include `print_full()`, `print_sums()`, `print_averages()`, `print_all_stats()`, and `print_default()`. `median()` and `percentile()` support all-stats mode. `TimeSeries` reads a log file into `Sample` objects, tracks the last sample, and provides `get_samples()` and `get_value()` for intervals. `Sample.get_contribution()` weights a sample by interval overlap and divisor.

## Control Flow and State
The main path builds a `TimeSeries` per input file and dispatches to one print mode. Each time series treats a line's timestamp as the sample end and the previous timestamp as its start.

## Dependencies and Integration Points
It uses Python 2/3 compatibility imports and expects fio log lines formatted as `time, value, ...`. It is a post-processing tool for bandwidth, latency, and similar logs.

## Risks and Test Signals
Risks include O(N^2) interval stats noted by a FIXME, Python 3 division bugs in `median()` because list indexes use `/`, empty interval failures in all-stats mode, global `ctx` use inside `TimeSeries.add_sample()` and `Sample.get_contribution()` instead of instance fields, and strict comma-space parsing. Signals are numeric CSV-like output and exceptions for malformed or empty data.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/fiologparser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/genfio -->
# sources/test-tools/fio/tools/genfio

## Purpose
`genfio` is a Bash generator for fio job files that benchmark selected disks/files across block sizes, read/write modes, sequential scheduling, parallel scheduling, or both.

## Important APIs, Types, and Functions
`show_help()` documents options. `gen_template()` writes the `[global]` section to a temporary file; `finish_template()` appends iodepth, runtime/time_based, and direct I/O controls. `diskname_to_printable()` normalizes disk paths for names. `gen_seq_suite()` and `gen_para_suite()` append fio job sections for one disk/mode/block-size in sequential or parallel form, including bandwidth and IOPS log filenames. `gen_fio()` dispatches by selected mode. `parse_cmdline()` handles disks, block sizes, runtime, modes, prefix, file size, iodepth, cached I/O, pre/post commands, and output filename. `check_mode_order()` warns when reads precede writes.

## Control Flow and State
Global variables hold generator configuration, ETA, output path, and temporary template path. Main flow creates the template, parses CLI, finalizes defaults, warns about mode order, copies the template to the output file, appends generated jobs for each block size, and prints ETA.

## Dependencies and Integration Points
It depends on Bash, `mktemp`, `hostname`, `basename`, `sed`, `cp`, and fio job-file syntax. Generated jobs use `ioengine=libaio`, `invalidate=1`, `ramp_time=5`, optional `direct=1`, and `write_*_log` options.

## Risks and Test Signals
Risks include unquoted shell expansions around disk paths/prefixes, destructive benchmarking if disks are raw devices, limited validation of runtime/block/mode inputs, and generated read tests before data exists. Signals are generated `.fio` file content, ETA output, and warning delay when mode order is suspicious.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/genfio -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/tools/hist/fio-histo-log-pctiles.py -->
# sources/test-tools/fio/tools/hist/fio-histo-log-pctiles.py

## Purpose
`fio-histo-log-pctiles.py` parses fio histogram logs without pandas, aligns multiple thread logs to a common time quantum, aggregates buckets, and reports latency percentiles per time interval. It can also run embedded unit tests via the `UNITTEST` environment variable.

## Important APIs, Types, and Functions
`FioHistoLogExc` models parse errors. `parse_hist_file()` validates CSV histogram records, enforces nonnegative integers, direction values, monotonic timestamps per direction, block-size limits, and expected bucket counts, then estimates start/end timestamps. `time_ranges()` maps fio v2/v3 histogram bucket indexes to latency ranges. `get_time_intervals()` computes quantum count. `align_histo_log()` weights raw histogram buckets into aligned intervals by overlap fraction. `add_to_histo_from()`, `get_samples()`, and `get_pctiles()` aggregate and interpolate percentile results. `compute_percentiles_from_logs()` is the CLI entry point.

## Control Flow and State
CLI arguments select fio version, bucket groups/bits, requested percentiles, time quantum, optional log interval, output unit, and files. The script parses each log, chooses the time range common to all threads, aligns each per-thread histogram, sums them into `all_threads_histograms`, and prints CSV-like percentile rows. Unit tests cover parsing validation, bucket range computation, alignment, and percentile interpolation.

## Dependencies and Integration Points
It depends on Python 2/3-compatible standard libraries plus optional `unittest2`. It consumes fio histogram log format and mirrors fio `stat.h` bucket semantics. Output can feed analysis pipelines.

## Risks and Test Signals
Risks include assumptions that all threads run the same workload duration, limited read/write separation for randrw, fragile next-record direction matching, missing `nsec` output-unit handling, and possible exceptions when only one epoch-style record lacks `log_hist_msec`. Signals are explicit parse errors, unit tests, printed parameter echo, and percentile rows with sample counts.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/tools/hist/fio-histo-log-pctiles.py -->
