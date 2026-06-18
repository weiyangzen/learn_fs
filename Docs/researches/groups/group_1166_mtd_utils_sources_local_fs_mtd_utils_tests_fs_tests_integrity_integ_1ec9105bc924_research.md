# Group Research: group_1166_mtd_utils_sources_local_fs_mtd_utils_tests_fs_tests_integrity_integ_1ec9105bc924

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/mtd-utils`. Every file listed in this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/integrity/integck.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/integrity/integck.c

## Purpose
Full filesystem integrity stress test for a mounted test filesystem. It randomly creates, mutates, syncs, renames, unlinks, and remounts files/directories/symlinks/hardlinks while maintaining an in-memory model of expected namespace and file data.

## Key Elements
Defines models for `write_info`, `file_info`, `dir_info`, `dir_entry_info`, `symlink_info`, and open descriptors. Records deterministic random write ranges, truncations, holes, link counts, and clean/dirty state. `create_test_data()` fills then partly drains the filesystem; `update_test_data()` repeats grow/shrink/mutation cycles; `integck()` creates the test tree, remounts, verifies, repeats, and cleans up. It can also run power-cut recovery loops and UBI reattach.

## Dependencies
Uses POSIX filesystem APIs, `statvfs/statfs`, `mmap`, mount table parsing, `mount/umount`, `backtrace`, project `common.h`, and `libubi.h`.

## Behavior/Risks
Destructive inside the specified mount point and may unmount/remount it. Power-cut mode expects write failures as `EROFS` or sometimes `EIO` and can reattach MTD devices through `/dev/ubi_ctrl`. Recursion and cleanup depend on `dirent.d_type`, and most invariants terminate via `CHECK()`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/integrity/integck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/lib/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/lib/Makefile

## Purpose
Build helper for the shared fs-test support library object.

## Key Elements
Defaults `CC` to `gcc`, appends `-Wall -g -O2`, builds `tests.o`, and declares `tests.o` depends on `tests.h`.

## Dependencies
Plain make and a C compiler.

## Behavior/Risks
The `tests` target only echoes, so this directory has no runtime test beyond compiling `tests.o`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/lib/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.c

## Purpose
Shared runtime library for the mtd-utils filesystem test programs.

## Key Elements
Provides common argument parsing, mount directory/type configuration from environment, assertion reporting, free/total space queries, deterministic filled-file and fragment-file writers/checkers, orphan creation, directory cleanup, random entry create/remove helpers, remount/unmount/mount helpers, root/current-FS checks, and PID-safe name building.

## Dependencies
Uses POSIX file APIs, `statvfs/statfs`, mount table parsing, Linux mount flags, `linux/fs.h`, `linux/jffs2.h`, and `tests.h`.

## Behavior/Risks
Designed for destructive tests under `TEST_FILE_SYSTEM_MOUNT_DIR`, defaulting to `/mnt/test_file_system`. `tests_get_args()` sets `rootok = 1`, so root filesystem rejection is effectively disabled for callers using defaults. Cleanup relies on `dirent.d_type`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.h -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.h

## Purpose
Public interface for the shared fs-test support library.

## Key Elements
Defines `CHECK`, default mount directory/type, empty-directory size estimate, helper prototypes for argument parsing, file creation/checking, fragment/orphan operations, remounting, cleanup, and shared global option variables.

## Dependencies
Includes `stdint.h`; declarations also require POSIX types such as `off_t`, `size_t`, and `pid_t` from including translation units.

## Behavior/Risks
The API exposes mutable global configuration rather than explicit context objects, so callers assume single-process global test state.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/run_all.sh -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/run_all.sh

## Purpose
Top-level shell runner for the fs-tests suite.

## Key Elements
Chooses `$TEST_FILE_SYSTEM_MOUNT_DIR` or `/mnt/test_file_system`, clears it between tests, runs simple tests, `integrity/integck`, selected stress atoms, then `stress00.sh` and `stress01.sh` for 360 seconds each.

## Dependencies
Requires built test binaries, shell, `rm -rf`, and a safe mounted test directory.

## Behavior/Risks
Repeatedly executes unquoted `rm -rf ${TEST_DIR}/*`. A bad test directory setting is dangerous.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/run_all.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/Makefile

## Purpose
Builds simple standalone filesystem tests.

## Key Elements
Targets `test_1`, `test_2`, `ftrunc`, `orph`, and `perf`, all linked with `../lib/tests.o`. The `tests` target runs them with selected sync options.

## Dependencies
Uses `gcc`, shared `../lib/tests.o`, and include path `../lib`.

## Behavior/Risks
The `tests` target runs destructive filesystem tests immediately against the configured test mount.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/ftrunc.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/ftrunc.c

## Purpose
Simple truncate test for a large file.

## Key Elements
Creates `ftrunc_test_file`, writes up to `tests_size_parameter` bytes of PID-seeded random data, truncates the file by one byte if nonempty, closes it, and unlinks it.

## Dependencies
Uses POSIX open/write/ftruncate/unlink and shared `tests.h`.

## Behavior/Risks
Treats `ENOSPC` during writing as expected. It verifies syscall success but does not reread final contents.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/ftrunc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/orph.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/orph.c

## Purpose
Exercises open-but-unlinked orphan file handling.

## Key Elements
Creates `orph_test_dir_<pid>`, repeatedly creates up to one million unlinked open files, writes deterministic fragment data, verifies all open orphan contents, optionally fills remaining space through the last descriptor, sleeps, closes descriptors, and repeats.

## Dependencies
Uses shared orphan/fragment helpers from `tests.h`.

## Behavior/Risks
Can exhaust file descriptors or filesystem space by design. It expects `ENOSPC` or `EMFILE` as stopping conditions and relies on closing all orphan descriptors for cleanup.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/orph.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/perf.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/perf.c

## Purpose
Measures write, unmount, mount, and read timing for a test file.

## Key Elements
Writes a PID-seeded file of `tests_size_parameter` bytes, fsyncs and closes it, unmounts and remounts the test filesystem, reads it back in 32 KiB blocks, deletes it, and prints timings plus KiB/s rates.

## Dependencies
Uses shared mount helpers from `tests.h`, POSIX timing, and file APIs.

## Behavior/Risks
Unmounts/remounts the test filesystem and assumes privilege. `speed()` divides by elapsed microseconds, so extremely fast operations could risk divide-by-zero.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/perf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_1.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_1.c

## Purpose
Tests filesystem behavior when a large unlinked file remains open while the filesystem is filled.

## Key Elements
Creates a half-free-space `big_file`, opens it, edits beginning/end sentinels, unlinks it, fills the directory with smaller files until full, checks the open deleted file, deletes filler files, restores original bytes/truncates, verifies data, closes the orphan, and removes the test directory.

## Dependencies
Uses shared fill/check/delete helpers and optional sync support from `tests.h`.

## Behavior/Risks
Intentionally fills the filesystem and relies on correct open deleted-file accounting.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_2.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_2.c

## Purpose
Tests many small files plus one large unlinked open file under repeated overwrites.

## Key Elements
Creates up to 1000 fragment files, appending 400 bytes round-robin until full; deletes half; creates a large file using two-thirds of free space; opens and unlinks it; repeatedly overwrites small-file ranges and rewrites the big open file; validates all remaining files after each phase.

## Dependencies
Uses shared fragment and filled-file helpers from `tests.h`.

## Behavior/Risks
Heavy space-pressure and overwrite test. It assumes deterministic fragment data remains valid across partial overwrites because the same per-file random stream is reused.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/Makefile

## Purpose
Delegating makefile for stress tests.

## Key Elements
Defines `SUBDIRS = atoms`, forwards `all`, `tests`, and `clean` to subdirectories, and removes `run_pdf_test_file_*` during clean.

## Dependencies
Requires recursive make.

## Behavior/Risks
No direct binaries here; all C stress atoms are delegated to `stress/atoms`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/Makefile

## Purpose
Builds atomic stress-test executables.

## Key Elements
Targets `stress_1`, `stress_2`, `stress_3`, `pdfrun`, `rndwrite00`, `fwrite00`, `rmdir00`, `rndrm00`, `rndrm99`, and `gcd_hupper`, linking each with `../../lib/tests.o`.

## Dependencies
Uses `gcc`, include path `../../lib`, and shared test library object.

## Behavior/Risks
Contains a likely stale dependency rule for `../lib/tests.o` while targets actually link `../../lib/tests.o`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/fwrite00.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/fwrite00.c

## Purpose
Configurable file write stress atom.

## Key Elements
Creates `filestress00_test_file_<pid>`, optionally unlinks it while open, writes either full random data or sparse-hole marker bytes, optionally closes/reopens, sleeps, deletes, and repeats according to shared options.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Handles `ENOSPC` as normal. In unlink mode it stresses open-deleted-file behavior; in hole mode it creates large sparse extents with marker writes every 10 MB.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/fwrite00.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/gcd_hupper.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/gcd_hupper.c

## Purpose
Sends `SIGHUP` repeatedly to the JFFS2 garbage-collector daemon for the tested MTD device.

## Key Elements
Scans `/proc/*/stat` for process names beginning with `jffs2_gcd_mtd`, derives the mounted MTD index from mount table device names, finds the matching GC PID, then sends `SIGHUP` with optional repeat and sleep.

## Dependencies
Uses `/proc`, mount table parsing, signals, and shared `tests.h`.

## Behavior/Risks
Requires permission to signal the target task. Process-name and MTD-index parsing are JFFS2-specific and fragile outside legacy MTD naming.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/gcd_hupper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/pdfrun.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/pdfrun.c

## Purpose
Creates/overwrites a large file in the current directory, but only if current directory is not on the test filesystem.

## Key Elements
Caps requested size to half of total memory from `/proc/meminfo`, creates `run_pdf_test_file_<pid>`, repeatedly writes PID-seeded random data, rewinds between repeats, then closes and unlinks.

## Dependencies
Uses POSIX file APIs, `/proc/meminfo`, and shared current-FS helper.

## Behavior/Risks
No-ops when the current directory is on the test filesystem. Intended to create external write pressure during test-FS stress.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/pdfrun.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rmdir00.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rmdir00.c

## Purpose
Repeatedly creates and removes directories and small files.

## Key Elements
Creates `rmdir00_test_dir_<pid>`, clears it at the start of each repeat, fills it with random small files/directories until a size target or ENOSPC, optionally sleeps, then clears and removes the directory.

## Dependencies
Uses shared random entry and cleanup helpers from `tests.h`.

## Behavior/Risks
Can fill the filesystem when `-z0` is used. Cleanup relies on recursive directory clearing.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rmdir00.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm00.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm00.c

## Purpose
Random create/remove namespace stress test.

## Key Elements
Creates `rndrm00_test_dir_<pid>`, grows the namespace with a 2:1 create/remove tendency until the size target or ENOSPC, then shrinks with a 2:1 remove/create tendency until the tree is much smaller. Repeats and sleeps according to options.

## Dependencies
Uses shared random entry, remove, and cleanup helpers from `tests.h`.

## Behavior/Risks
Can run forever with `-n0` and can fill the filesystem with `-z0`. It assumes `tests_remove_entry()` is called only when entries exist often enough for its random selection logic.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm00.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm99.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm99.c

## Purpose
Instrumented variant of random create/remove namespace stress.

## Key Elements
Duplicates the `rndrm00` grow/shrink pattern but adds counters for files/directories created/removed, reports net size, and times individual filesystem calls. Calls taking at least 8 seconds are logged with current stats.

## Dependencies
Uses POSIX file APIs, directory APIs, timing, `statvfs/statfs` includes, and shared helpers from `tests.h`.

## Behavior/Risks
Verbose diagnostic stress tool. It intentionally reports slow operations and ENOSPC events, can fill the filesystem, and uses the same recursive cleanup assumptions as other stress tests.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm99.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndwrite00.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndwrite00.c

## Purpose
Random in-place write verification test for a large file.

## Key Elements
Creates `rndwrite00_test_file_<pid>`, allocates an in-memory copy of the requested file size, writes initial random contents, repeatedly writes random 1-4095 byte blocks at random offsets, updates the memory mirror, periodically verifies the file, and optionally deletes it.

## Dependencies
Uses POSIX file APIs, heap memory proportional to requested file size, and shared option/random helpers from `tests.h`.

## Behavior/Risks
If `actual_size` is below 8192, `check_every = actual_size / 8192` can become zero before the modulo check. Large `-z` values allocate matching RAM.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndwrite00.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_1.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_1.c

## Purpose
Basic large file create/write stress atom.

## Key Elements
Creates `stress_1_test_file_<pid>`, fills it with PID-seeded random data up to `tests_size_parameter` or ENOSPC, closes it, and optionally unlinks it.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Does not verify file contents. Leaves the file behind unless delete option is specified.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_2.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_2.c

## Purpose
Repeated overwrite stress for an open deleted file.

## Key Elements
Creates `stress_2_test_file`, immediately unlinks it while holding the descriptor, repeatedly rewinds and writes `tests_size_parameter` bytes of random data, then closes the descriptor.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Stresses orphan inode data accounting and ENOSPC behavior. No content verification.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_3.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_3.c

## Purpose
Sparse-file hole allocation and truncate stress atom.

## Key Elements
Creates `stress_3_test_file_<pid>`, seeks to `tests_size_parameter`, writes one byte to create a hole, rewinds and fills the hole with random data until full or complete, truncates the file to zero, closes it, and optionally deletes it.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Intentionally exercises sparse extent allocation and truncate after ENOSPC. It treats `ENOSPC` from `ftruncate` as acceptable.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_3.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress00.sh -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress00.sh

## Purpose
Concurrent stress scenario runner.

## Key Elements
Determines test directory and free space, sets each worker size to one-fifteenth of free space, builds optional duration argument, then runs many `fwrite00` variants, `rndwrite00`, and `pdfrun` under `../utils/fstest_monitor`.

## Dependencies
Requires `../utils/free_space`, `../utils/fstest_monitor`, atom binaries, shell arithmetic, and a mounted test directory.

## Behavior/Risks
Runs many destructive workers concurrently and clears `${TEST_DIR}/*` unquoted at the end.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress00.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress01.sh -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress01.sh

## Purpose
Smaller concurrent stress scenario runner.

## Key Elements
Computes free-space-based file size and runs fewer long-lived `fwrite00` and `rndwrite00` workloads under `fstest_monitor`, optionally bounded by duration.

## Dependencies
Requires `../utils/free_space`, `../utils/fstest_monitor`, atom binaries, shell arithmetic, and a mounted test directory.

## Behavior/Risks
Destructive concurrent stress. Performs unquoted final `rm -rf ${TEST_DIR}/*`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/stress/stress01.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/utils/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/utils/Makefile

## Purpose
Builds utility binaries used by stress scripts.

## Key Elements
Targets `fstest_monitor` and `free_space`, using `-Wall -g -O2 -I../lib`. The `tests` target runs `fstest_monitor` and suppresses `free_space` output.

## Dependencies
Plain make and a C compiler.

## Behavior/Risks
`tests` is minimal and does not validate monitor behavior under real child workloads.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/utils/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/utils/free_space.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/utils/free_space.c

## Purpose
Reports available filesystem space in bytes.

## Key Elements
Accepts an optional directory argument, defaults to `.`, handles `-h/--help`, calls `statvfs`, and prints `f_bavail * f_frsize`.

## Dependencies
Uses standard C and `sys/statvfs.h`.

## Behavior/Risks
Returns failure if `statvfs` fails. Help exits with status 1 rather than success.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/utils/free_space.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/utils/fstest_monitor.c -->
# File Research: sources/local-fs/mtd-utils/tests/fs-tests/utils/fstest_monitor.c

## Purpose
Concurrent command supervisor for stress workloads.

## Key Elements
Parses optional `-d/--duration`, forks each command string, parses quoted command lines into argv arrays, execs children, tracks child state, terminates all children on failure or signal, and exits success when duration alarm intentionally stops workers.

## Dependencies
Uses fork/execve/wait, signals, alarm, and simple local command-line parsing.

## Behavior/Risks
Command parser is limited and allocates argument storage that children do not free before exec. Termination escalates only to SIGTERM because the SIGKILL block is commented out.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/fs-tests/utils/fstest_monitor.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/JitterTest.c -->
# File Research: sources/local-fs/mtd-utils/tests/jittertest/JitterTest.c

## Purpose
Standalone wake-jitter measurement tool intended for filesystem/JFFS2 latency experiments.

## Key Elements
Uses one-shot `setitimer(ITIMER_REAL)` alarms, measures elapsed time versus requested period, writes jitter lines to an output file and console/log file, optionally pads each write, reads a byte from a chosen file each cycle, optionally runs as `SCHED_RR`, locks memory with `mlockall`, snapshots `/proc/profile` on large jitter, and can SIGSTOP/SIGCONT a GC task around writes.

## Dependencies
Uses POSIX signals, timers, scheduler APIs, `mlockall`, synchronous file IO, `/proc/profile`, and root privileges for real-time scheduling or GC signaling.

## Behavior/Risks
Infinite until SIGINT. Signal handlers perform non-async-signal-safe work such as formatted IO, file IO, and malloc-adjacent routines. Filename buffers are small fixed arrays.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/JitterTest.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/jittertest/Makefile

## Purpose
Builds jitter test utilities.

## Key Elements
Defines `CC=gcc`, optimized `CCFLAGS`, builds `JitterTest` and `plotJittervsFill`, and includes old `makedepend` dependency output.

## Dependencies
Requires gcc and libc; `JitterTest` is linked with `-lm`.

## Behavior/Risks
Rules hardcode `gcc` instead of `$(CC)`. `clean` removes `JitterTest` but not `plotJittervsFill`.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/filljffs2.sh -->
# File Research: sources/local-fs/mtd-utils/tests/jittertest/filljffs2.sh

## Purpose
Simple loop to repeatedly fill and clear a JFFS2/MTD-backed filesystem target.

## Key Elements
Forever copies argument 1 to argument 2, removes argument 2, writes `df | grep mtd` output to `/dev/console`, echoes sleep duration, and sleeps for argument 3 seconds.

## Dependencies
Uses bash, `cp`, `rm`, `df`, `grep`, and `/dev/console`.

## Behavior/Risks
Infinite loop with unvalidated positional parameters. Can repeatedly delete the destination path supplied by the caller.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/filljffs2.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/plotJittervsFill.c -->
# File Research: sources/local-fs/mtd-utils/tests/jittertest/plotJittervsFill.c

## Purpose
Extracts plot data from combined `JitterTest` and `df` logs.

## Key Elements
Parses options for input file, jitter threshold, version/help, and debug. Scans log lines for jitter values above threshold, buffers them until a later `df` percentage line, and emits used-percent plus jitter pairs to stderr.

## Dependencies
Uses stdio/string parsing and assumes log formats produced by `JitterTest` plus `df`.

## Behavior/Risks
Parsing is format-fragile. It uses `abs()` on a float expression after conversion, losing fractional precision and relying on implicit conversion.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/jittertest/plotJittervsFill.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/Makefile -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/Makefile

## Purpose
Builds UBI test binaries and local `libubi.a`.

## Key Elements
Sets libubi/header paths, kernel header include path, target list for UBI tests, includes `../../common.mk`, builds `libubi.a` from `ubi-utils/libubi.c` with `-DUDEV_SETTLE_HACK`, and links test targets with helpers plus libubi.

## Dependencies
Requires mtd-utils common build system, libubi sources, pthread, kernel headers, and UBI utility headers.

## Behavior/Risks
Builds a local static libubi variant with a udev settle hack, which may differ from normal libubi behavior.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.c -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.c

## Purpose
Common helper implementation for UBI tests.

## Key Elements
Checks prerequisites for a UBI character device, requiring enough available eraseblocks and an empty device. Provides formatted error/failure reporting, validates created volume properties against `ubi_mkvol_request`, checks a volume is filled with a byte pattern, updates a volume with a byte pattern through `ubi_update_start`, and seeds libc random using time plus PID.

## Dependencies
Uses libubi APIs, POSIX file IO, time/PID APIs, and declarations from `helpers.h`.

## Behavior/Risks
`__update_vol_patt()` writes fixed 512-byte chunks even when requested byte count is not a multiple of 512, then detects overshoot after the write. Tests using it need suitable aligned sizes.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.h -->
# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.h

## Purpose
Shared declarations and convenience macros for UBI tests.

## Key Elements
Defines volume node pattern, minimum available eraseblocks, page size, error/failure macros, wrappers that inject program/function/line metadata, `check_failed`, and an `ALIGNMENTS(s)` test vector around eraseblock fractions and boundaries.

## Dependencies
Includes `string.h` and `stdio.h`, but declarations depend on libubi types and `uint8_t` being visible from other includes.

## Behavior/Risks
Macros assume common global names such as `PROGRAM_NAME`, `libubi`, and `dev_info` exist in test translation units.
<!-- END FILE RESEARCH: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.h -->