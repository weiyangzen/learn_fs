# Research: subset-b-006891

Grouped source research for timer, tmpfs, TPM2, TTY, turbostat, and ublk selftest files. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/posix_timers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/posix_timers.c

## Purpose
This kselftest exercises Linux POSIX and interval timer behavior across wall-clock timers, CPU-time timers, signal delivery modes, overrun accounting, `SIGEV_NONE`, and timer ID restoration. It is a broad regression suite for timer creation, arming, signal queuing, deletion, rearming, and per-thread/process CPU accounting.

## Important APIs, Types, and Functions
Core timer APIs are `setitimer()`, `timer_create()`, `timer_settime()`, `timer_gettime()`, `timer_delete()`, `clock_gettime()`, `gettimeofday()`, and raw `timer_create`/`timer_delete` syscalls. `check_itimer()` covers `ITIMER_VIRTUAL`, `ITIMER_PROF`, and `ITIMER_REAL`; `check_timer_create()` covers `CLOCK_THREAD_CPUTIME_ID` and `CLOCK_PROCESS_CPUTIME_ID`; `check_sig_ign()`, `check_rearm()`, `check_delete()`, `check_sigev_none()`, `check_gettime()`, and `check_overrun()` cover signal queue semantics. `check_timer_create_exact()` uses `prctl(PR_TIMER_CREATE_RESTORE_IDS, ...)` and raw syscalls to verify restored timer IDs.

## Control Flow
`main()` emits a kselftest plan, runs the timer ID restore test, checks interval timers and POSIX CPU timers, verifies CPU timer signal distribution, optionally runs newer `SIG_IGN` semantics on kernels at least 6.13, and finishes with overrun checks on monotonic/process/thread clocks. Signal handlers update volatile counters and overrun totals. CPU timers are driven by busy loops, while real-time timers sleep through `pause()` or blocked signal waits.

## State and Persistence
State is in process-local globals such as `done`, `ctd_count`, `ctd_failed`, and per-test `struct tmrsig` counters. Timers and signal dispositions are kernel state and are deleted or restored before each test exits. The timer ID restore test temporarily enables a task `prctl` mode and explicitly disables it again.

## Dependencies and Integration Points
The test depends on pthreads, signal delivery, VDSO time constants, raw syscalls, `kselftest.h`, and kernel support for `PR_TIMER_CREATE_RESTORE_IDS`. It integrates with the timers selftest directory and reports every check through `ksft_test_result*` and `ksft_finished()`.

## Risks
The suite is timing-sensitive: CPU load, scheduler jitter, or unrelated threads can cause false negatives, which the test acknowledges for CPU timers. Several checks assume precise overrun counts after one-second sleeps with 100 ms intervals. Newer SIG_IGN expectations are kernel-version gated, and timer ID restoration may be skipped on kernels without the prctl.

## Test Signals
Passing signals include 2 second timer deltas within a 0.5 second tolerance, CPU timer signals delivered to the running thread only, expected SIG_IGN queue/drop semantics, `timer_gettime()` interval wraps, exact overrun counts, and restored timer ID allocation behavior. Failures indicate regressions in timer accounting, signal delivery, or timer lifecycle handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/posix_timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/raw_skew.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/raw_skew.c

## Purpose
This test estimates drift between `CLOCK_MONOTONIC` and `CLOCK_MONOTONIC_RAW` and compares that measured drift to the kernel frequency adjustment reported by `adjtimex()`. It validates that raw and disciplined monotonic clocks diverge consistently with the configured NTP frequency correction.

## Important APIs, Types, and Functions
Important helpers are `ts_to_nsec()`, `nsec_to_ts()`, `diff_timespec()`, and `get_monotonic_and_raw()`. The program uses `clock_gettime(CLOCK_MONOTONIC[_RAW])`, `adjtimex()`, `sleep(120)`, and VDSO nanosecond constants. `shift_right()` preserves signed right-shift behavior for scaled ppm conversion.

## Control Flow
`main()` verifies raw clock availability, samples `adjtimex()` and the initial monotonic/raw delta, sleeps for 120 seconds, samples again, computes estimated ppm from delta change over elapsed monotonic time, compares it with averaged `tx.freq`, and passes if the difference is within 1 ppm scaled as 1000 milli-ppm units. External time adjustment causes a skip when offsets, frequency, or tick values change.

## State and Persistence
There is no persistent state. The test samples kernel timekeeping state before and after a long interval and does not modify it.

## Dependencies and Integration Points
It depends on `CLOCK_MONOTONIC_RAW`, `adjtimex`, VDSO time constants, and kselftest exit codes. It is a long-running timers selftest intended to run where NTP or other time daemons are not actively changing frequency/offset during the sample.

## Risks
The 120 second runtime is expensive for automated suites. External time synchronization or offset correction makes the estimate unreliable and is treated as skip when detected. Short clock-read latency is mitigated by sampling three bracketing monotonic/raw reads and choosing the narrowest monotonic window.

## Test Signals
Pass means estimated monotonic/raw drift matches kernel frequency correction within tolerance. Skip means time was externally adjusted or counters were unavailable. Failure means raw/monotonic skew is inconsistent with `adjtimex` frequency state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/raw_skew.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/rtcpie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/rtcpie.c

## Purpose
This RTC test validates periodic interrupt emulation through `/dev/rtc0` or a user-provided RTC device. It confirms that periodic IRQ rates can be read/set and that reads block roughly for the configured interrupt period.

## Important APIs, Types, and Functions
The test uses `/dev/rtc*`, `ioctl(RTC_IRQP_READ)`, `RTC_IRQP_SET`, `RTC_PIE_ON`, `RTC_PIE_OFF`, blocking `read()`, and `gettimeofday()`. It stores and restores the old periodic interrupt rate.

## Control Flow
`main()` chooses the RTC path, skips if the default device is absent, opens the device, reads the current PIE rate, then loops through 2, 4, 8, 16, 32, and 64 Hz. For each rate it enables periodic interrupts, reads 20 events, measures the time between reads, fails if the interval exceeds 110% of the expected period, disables interrupts, and finally restores the old rate.

## State and Persistence
Kernel RTC PIE state and rate are modified temporarily. The old rate is restored in the `done` path, but hard failures before that path can leave the device in an altered state until process exit or subsequent cleanup.

## Dependencies and Integration Points
The test depends on Linux RTC UAPI definitions, an RTC class device, and permissions to change requested PIE rates. It integrates as a kselftest-style standalone executable but prints most progress directly to stderr.

## Risks
Some RTC devices do not support periodic IRQs or changing the rate; those cases go to the successful `done` path instead of failing. Timing is sensitive to scheduler delays. Privilege restrictions can affect higher rates, though this test only uses 2 to 64 Hz.

## Test Signals
The main signal is 20 blocking reads per rate with measured intervals near the configured period. `EINVAL` from RTC IRQ operations indicates unsupported functionality rather than a kernel regression for devices without PIE support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/rtcpie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-2038.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-2038.c

## Purpose
This meta-test sets the realtime clock near major time boundaries and runs other timer tests to detect Y2038, ktime, and time_t rollover issues. It is intentionally invasive because it changes system time.

## Important APIs, Types, and Functions
`settime()` wraps `settimeofday()` with second-only values. `do_tests()` runs `date`, `./inconsistency-check -c 0 -t 20`, `./nanosleep`, and `./nsleep-lat`. Boundary constants include `YEAR_1901`, `YEAR_1970`, `YEAR_2038`, `YEAR_2262`, and `YEAR_MAX`; `is32bits()` gates dangerous 32-bit rollover cases.

## Control Flow
`main()` parses `-d` to enable dangerous 32-bit cases, saves the current time, verifies impossible values are rejected, sets time to 1970 and near 2038, and runs the dependent tests after each change. On 32-bit systems it skips the most dangerous rollover tests unless `-d` is provided. It restores the original time in the common exit path.

## State and Persistence
The test modifies global system realtime clock state. It attempts to restore the starting `time(0)` value on every structured exit path, but a crash or forced termination would leave host time changed.

## Dependencies and Integration Points
It requires permission to call `settimeofday()` and assumes companion executables `inconsistency-check`, `nanosleep`, and `nsleep-lat` are present in the current directory. It uses kselftest exit helpers.

## Risks
This test can disrupt the host, filesystems, logs, TLS, and other tests because it changes wall time. The dependent test binaries are invoked with `system()`, so working directory and executable availability are part of correctness. The dangerous 32-bit path can expose severe rollover failures.

## Test Signals
Pass means invalid extreme times were rejected, dependent time tests survived edge values, and the clock was restored. Failure means an invalid bound was accepted or one of the companion timer tests failed under an edge timestamp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-2038.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tai.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tai.c

## Purpose
This test validates setting and reading the kernel TAI offset through `adjtimex(ADJ_TAI)`.

## Important APIs, Types, and Functions
`set_tai()` writes `struct timex.modes = ADJ_TAI` and `constant = offset`. `get_tai()` calls `adjtimex()` in query mode and returns `tx.tai`.

## Control Flow
`main()` prints the initial TAI offset, then sets offsets from 1 through 60 and verifies that each value is returned by the next query. It exits fail on the first mismatch and pass after the full range.

## State and Persistence
This modifies global kernel timekeeping TAI offset and does not restore the initial value. The ending TAI offset is 60 on success.

## Dependencies and Integration Points
The test requires privileges for `adjtimex(ADJ_TAI)` and depends on `sys/timex.h` plus kselftest exit helpers.

## Risks
Not restoring the starting TAI offset can affect later TAI-clock tests or system behavior. It does not inspect `adjtimex()` return codes before reading back state, so failures are detected only by mismatch.

## Test Signals
Pass means the kernel accepted every TAI offset in the tested range and reported it back accurately. Failure means `ADJ_TAI` did not take effect or was blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-timer-lat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-timer-lat.c

## Purpose
This latency test arms POSIX timers on all supported wall-time style clocks and checks that they do not fire early, have reasonable maximum latency, and one-shot timers fire exactly once.

## Important APIs, Types, and Functions
Key functions are `clockstring()`, `timespec_sub()`, `sigalarm()`, `setup_timer()`, `check_timer_latency()`, `check_alarmcount()`, `do_timer()`, and `do_timer_oneshot()`. It uses `timer_create()`, `timer_settime()`, `timer_delete()`, `clock_gettime()`, realtime signal `SIGRTMAX`, and `select()` for one-shot wait.

## Control Flow
`main()` installs a signal handler and iterates clock IDs up to `CLOCK_TAI`, skipping CPU, raw, coarse, and deprecated hardware-specific clocks. For each remaining clock, it runs periodic and one-shot timers in both absolute and relative modes. The signal handler computes the delta from expected expiry and records early fires and maximum latency.

## State and Persistence
Per-run state lives in globals `alarmcount`, `clock_id`, `start_time`, `max_latency_ns`, and `timer_fired_early`. Timers are deleted after each subtest. No persistent system state is changed.

## Dependencies and Integration Points
The test depends on Linux clock IDs, POSIX timer support, realtime signal delivery, and kselftest exit codes. Alarm clocks may require `CAP_WAKE_ALARM`; unsupported alarm timers are reported as unsupported and do not fail the run.

## Risks
The `UNRESONABLE_LATENCY` threshold is 40 ms, so heavily loaded or virtualized hosts can fail despite correct kernel behavior. Signal scheduling delays directly affect max latency. The test walks numeric clock IDs and relies on known skip cases.

## Test Signals
Pass requires no early signal and maximum latency below 40 ms for periodic and one-shot modes, plus exactly one signal for one-shot timers. Unsupported alarm timers are accepted as environment limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-timer-lat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tz.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tz.c

## Purpose
This test validates legacy timezone fields accepted by `settimeofday(NULL, &timezone)`, particularly allowed and rejected `tz_minuteswest` ranges.

## Important APIs, Types, and Functions
`set_tz()` calls `settimeofday()` with a `struct timezone`. `get_tz_min()` and `get_tz_dst()` read timezone data via `gettimeofday()`.

## Control Flow
`main()` records the original minutes-west and DST fields, iterates from -15 hours to +15 hours in 30 minute steps and verifies each set, checks that out-of-range values such as +/-15h plus one minute and +/-24h are rejected, restores the original timezone, and exits pass or fail.

## State and Persistence
The test modifies global kernel timezone state and restores the original values in both success and error paths.

## Dependencies and Integration Points
It depends on privilege to set timezone state and on the historical `struct timezone` interface. It is a standalone kselftest executable.

## Risks
The timezone interface is legacy and may be constrained differently by kernels or containers. A crash before cleanup would leave timezone state changed.

## Test Signals
Pass means valid half-hour increments in the allowed range are reflected by `gettimeofday()` and invalid values are rejected. Failure indicates range validation or readback regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/skew_consistency.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/skew_consistency.c

## Purpose
This meta-test stresses timekeeping consistency while the kernel frequency adjustment is changed asynchronously. It watches whether companion inconsistency checks survive repeated `ADJ_FREQUENCY` changes.

## Important APIs, Types, and Functions
The program uses `fork()`, `system("./inconsistency-check -t 60")`, `waitpid(..., WNOHANG)`, `adjtimex(ADJ_FREQUENCY)`, and `usleep()`.

## Control Flow
The child process runs `inconsistency-check` for 60 seconds. The parent alternates frequency between +500 ppm and -500 ppm every 500 ms while the child is alive. After the child exits, the parent attempts to reset frequency to zero and passes only if the child command returned success.

## State and Persistence
The test modifies global kernel frequency adjustment. It attempts to reset frequency to zero, which may not restore a previous nonzero NTP state.

## Dependencies and Integration Points
It requires permission for `adjtimex(ADJ_FREQUENCY)` and requires the `inconsistency-check` binary in the current directory. It integrates with kselftest pass/fail exits.

## Risks
It can interfere with system time discipline and does not preserve the original frequency value. The external command and working directory are required. Running NTP or another time daemon concurrently can fight the test.

## Test Signals
Pass means the inconsistency checker reported no monotonicity failures under rapid frequency changes. Failure means the companion test found time inconsistencies or exited unsuccessfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/skew_consistency.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/threadtest.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/threadtest.c

## Purpose
This threaded clock test stresses `clock_gettime(CLOCK_MONOTONIC)` consistency across multiple CPUs and under lock contention. It detects non-monotonic timestamp sequences generated by shared or independent worker threads.

## Important APIs, Types, and Functions
`checklist()` scans ordered `timespec` samples for backward movement. `shared_thread()` fills a global sample list under `list_lock`; `independent_thread()` fills a private list. `main()` parses `-t`, `-n`, and `-i`, creates pthreads, and manages runtime.

## Control Flow
By default eight threads run for 30 seconds using the shared global list path. With `-i`, each thread samples independently. Any detected inconsistency sets global `done`, prints the surrounding timestamp list under `print_lock`, and causes the main thread to fail after joining workers.

## State and Persistence
State is process-local: mutexes, `done`, `global_list`, and `listcount`. No kernel state is modified.

## Dependencies and Integration Points
The test depends on pthreads, `CLOCK_MONOTONIC`, and kselftest exit helpers. Command-line options allow runtime and thread-count scaling.

## Risks
The comparison condition is intended to detect time going backward but checks seconds and nanoseconds with a conservative expression; false output quality depends on synchronized printing. High thread counts are capped at 128.

## Test Signals
Pass means no sampled sequence showed a monotonic timestamp regression for the configured runtime. Failure prints the sample window bracketing the inconsistent pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/threadtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/valid-adjtimex.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/valid-adjtimex.c

## Purpose
This test validates valid, out-of-range, and invalid `adjtimex()` frequency inputs plus valid and invalid `ADJ_SETOFFSET` values for microsecond and nanosecond modes.

## Important APIs, Types, and Functions
`clock_adjtime()` wraps the raw syscall. `clear_time_state()` clears NTP status. `validate_freq()` applies arrays of valid, out-of-range, and invalid `tx.freq` values. `set_offset()`, `set_bad_offset()`, and `validate_set_offset()` exercise `ADJ_SETOFFSET` with and without `ADJ_NANO`.

## Control Flow
`main()` runs frequency validation first, then set-offset validation. Frequency tests expect valid values to set, out-of-range values to be clamped or rejected without storing the exact value, and 64-bit `LONG_MAX/MIN` values to fail. Offset tests apply normalized positive and negative offsets and reject malformed subsecond fields.

## State and Persistence
The test modifies kernel frequency and realtime offset. It resets frequency to zero after `validate_freq()`, but it does not otherwise restore external time synchronization state.

## Dependencies and Integration Points
It depends on `adjtimex`, raw `clock_adjtime`, VDSO time constants, and privileges for time adjustment. It uses kselftest exit helpers.

## Risks
The test can perturb system clock discipline and should not run with active time synchronization unless isolated. It defines `ADJ_SETOFFSET` locally, so it assumes the UAPI value is stable. The checks are sensitive to how kernels clamp out-of-range frequency values.

## Test Signals
Pass means accepted frequency values persist as requested, disallowed values are not accepted as exact active frequency, invalid 64-bit sentinels fail, normalized offsets apply, and malformed subsecond offsets are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/timers/valid-adjtimex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/Makefile

## Purpose
This Makefile builds the tmpfs selftest binary `bug-link-o-tmpfile`.

## Important APIs, Types, and Functions
It sets `CFLAGS += -Wall -O2`, declares `TEST_GEN_PROGS += bug-link-o-tmpfile`, and includes `../lib.mk` to integrate with kselftest build/run rules.

## Control Flow
There is no runtime control flow. During `make`, kselftest infrastructure compiles the listed C program and includes it in generated test binaries.

## State and Persistence
The Makefile only affects build outputs under the kselftest output directory.

## Dependencies and Integration Points
It depends on `tools/testing/selftests/lib.mk` and the adjacent `bug-link-o-tmpfile.c`.

## Risks
The narrow build configuration means any additional tmpfs tests must be added to `TEST_GEN_PROGS` or they will not run.

## Test Signals
Successful build of `bug-link-o-tmpfile` is the only signal from this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/bug-link-o-tmpfile.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/bug-link-o-tmpfile.c

## Purpose
This tmpfs regression test verifies that linking an `O_TMPFILE` inode into a tiny tmpfs mount does not corrupt inode accounting. It specifically exercises creating an anonymous tmpfile, linking it, and then creating another anonymous tmpfile when the mount has only three inodes.

## Important APIs, Types, and Functions
The program uses `unshare(CLONE_NEWNS)`, `mount(MS_PRIVATE|MS_REC)`, `mount(..., "tmpfs", ..., "nr_inodes=3")`, `openat(..., O_TMPFILE)`, and `linkat(..., AT_EMPTY_PATH)`. It reports through `kselftest.h`.

## Control Flow
`main()` sets a one-test plan, skips unless running as root, creates a private mount namespace, makes `/` private, mounts a constrained tmpfs on `/tmp`, opens one `O_TMPFILE`, links it to `/tmp/1`, closes it, opens a second `O_TMPFILE`, and passes if that succeeds.

## State and Persistence
The test mutates the process mount namespace and mounts tmpfs over `/tmp`. Because it unshares the mount namespace first, the mount changes should not leak to the parent namespace. File descriptors are closed on normal paths.

## Dependencies and Integration Points
It requires root, mount namespace support, tmpfs, anonymous tmpfile support, `AT_EMPTY_PATH`, and kselftest reporting.

## Risks
If `unshare()` fails due to missing support or permission it skips on expected errors. Running without a private namespace would make `/tmp` mount changes dangerous, but the test fails before mount if namespace setup fails unexpectedly. The `linkat()` failure path calls `ksft_exit_fail_msg()` before a close statement that is effectively unreachable.

## Test Signals
Pass means tmpfs inode accounting allows the second anonymous tmpfile after the first is linked, with one root inode, one permanent inode, and one tmpfile inode. Failure points to tmpfs `O_TMPFILE`/link accounting regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tmpfs/bug-link-o-tmpfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/Makefile

## Purpose
This Makefile registers TPM2 shell tests and Python helper files with kselftest.

## Important APIs, Types, and Functions
It includes `../lib.mk`, sets `TEST_PROGS := test_smoke.sh test_space.sh test_async.sh`, and exports Python helpers through `TEST_PROGS_EXTENDED := tpm2.py tpm2_tests.py`.

## Control Flow
There is no runtime logic. kselftest runs the shell wrappers and copies extended Python files for execution.

## State and Persistence
Build/run state is managed by kselftest output directories only.

## Dependencies and Integration Points
The Makefile integrates shell wrappers with the Python unittest module and depends on kselftest `lib.mk`.

## Risks
Adding new Python unittest classes without a wrapper would not make them part of default test execution.

## Test Signals
The file's signal is that the three TPM2 wrappers and helper modules are available in the test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_async.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_async.sh

## Purpose
This wrapper runs TPM2 asynchronous/nonblocking unittest coverage when both the raw TPM and resource-manager devices are present.

## Important APIs, Types, and Functions
The script checks `/dev/tpm0` and `/dev/tpmrm0`, defines kselftest skip code `4`, and invokes `python3 -m unittest -v tpm2_tests.AsyncTest`.

## Control Flow
It exits skip if either required device node is missing. Otherwise it runs the `AsyncTest` unittest class and forwards combined output.

## State and Persistence
The script does not persist state; Python tests open TPM device files and close them.

## Dependencies and Integration Points
It depends on TPM2 character devices, Python 3, and adjacent `tpm2.py`/`tpm2_tests.py`.

## Risks
Device-node existence does not guarantee a TPM2 implementation or permission. Nonblocking behavior can vary with driver/resource-manager state.

## Test Signals
Pass means the `AsyncTest` unittest class succeeds. Exit code 4 means the environment lacks required TPM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_async.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_smoke.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_smoke.sh

## Purpose
This wrapper runs TPM2 smoke tests for sealing, unsealing, PCR policy, command validation, and partial read behavior.

## Important APIs, Types, and Functions
It checks `/dev/tpm0`, reads `/sys/class/tpm/tpm0/tpm_version_major`, requires version `2`, and invokes `python3 -m unittest -v tpm2_tests.SmokeTest`.

## Control Flow
The script skips if `/dev/tpm0` is missing or if the kernel reports a non-2 TPM version. Otherwise it runs the smoke unittest class.

## State and Persistence
The shell script itself has no persistent state. The Python smoke tests create transient TPM objects, extend PCRs, and flush contexts where possible.

## Dependencies and Integration Points
It depends on sysfs TPM version reporting, Python 3, and adjacent TPM2 helper modules.

## Risks
Smoke tests can alter PCR values, which are not reversible until reboot or reset depending on PCR bank. Device permissions and TPM ownership state can affect results.

## Test Signals
Pass means TPM2 command protocol operations in `SmokeTest` behave as expected. Skip indicates absent or non-TPM2 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_space.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_space.sh

## Purpose
This wrapper runs TPM resource-manager space tests against `/dev/tpmrm0`.

## Important APIs, Types, and Functions
It checks `/dev/tpmrm0`, uses kselftest skip code `4`, and invokes `python3 -m unittest -v tpm2_tests.SpaceTest`.

## Control Flow
The script skips when the resource-manager device is missing and otherwise runs the `SpaceTest` unittest class.

## State and Persistence
The wrapper does not persist state. The underlying tests create and flush TPM transient objects in separate resource-manager spaces.

## Dependencies and Integration Points
It depends on Linux TPM resource manager support and adjacent Python tests.

## Risks
The wrapper checks only device presence, so permission or unsupported command issues are surfaced by Python failures.

## Test Signals
Pass means resource-manager spaces isolate transient handles and return layered command-code errors as expected. Skip means `/dev/tpmrm0` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/test_space.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2.py

## Purpose
This Python module is a lightweight TPM2 protocol client used by the TPM2 selftests. It constructs binary TPM2 commands, parses responses, maps TPM return codes to names, and exposes higher-level helpers for PCR, policy, seal/unseal, capabilities, resource-manager spaces, and nonblocking operation.

## Important APIs, Types, and Functions
Constants define TPM2 command codes, algorithms, handles, return codes, capabilities, and feature values. `ProtocolError` decodes TPM RC families. `AuthCommand`, `SensitiveCreate`, and `Public` serialize TPM structures. Utility functions include `get_digest_size()`, `get_hash_function()`, `get_algorithm()`, and `hex_dump()`. `Client` owns the device file and implements `send_cmd()`, `read_pcr()`, `extend_pcr()`, `start_auth_session()`, `policy_pcr()`, `policy_password()`, `get_policy_digest()`, `flush_context()`, `create_root_key()`, `seal()`, `unseal()`, `reset_da_lock()`, `get_cap()`, and `get_cap_pcrs()`.

## Control Flow
`Client.__init__()` opens `/dev/tpm0` or `/dev/tpmrm0` based on `FLAG_SPACE` and optionally enables `O_NONBLOCK`. `send_cmd()` writes a fully packed command, polls if nonblocking, reads the response, optionally hex-dumps it, and raises `ProtocolError` on nonzero response code. Higher-level methods pack command-specific request bodies, call `send_cmd()`, and slice response payloads. `unseal()` first loads a sealed blob under a parent key, then unseals it with either password or policy session auth, and always flushes the loaded data handle.

## State and Persistence
The client holds an open TPM character device and, under resource-manager mode, a kernel TPM space. TPM transient objects and sessions are kernel state and must be flushed by callers. PCR extension mutates TPM PCR state. The module itself keeps no global mutable state except constants.

## Dependencies and Integration Points
It depends on Python `struct`, `hashlib`, `fcntl`, `select`, Linux TPM character devices, and TPM2 command wire formats. It is imported by `tpm2_tests.py` and run by shell wrappers.

## Risks
The module hand-packs TPM binary protocol and response offsets; mistakes in structure length or response slicing can produce brittle failures. `UnknownAlgorithmIdError.__str__()` and related methods reference local names rather than `self.*`, which could itself fail if stringified. PCR byte concatenation in `__calc_pcr_digest()` relies on Python bytearray behavior over collected PCR bytes. Operations can change PCR state and depend on TPM owner hierarchy being usable.

## Test Signals
Protocol-level success is a zero TPM RC in `send_cmd()`. Higher-level tests use expected data equality, known RC values such as `TPM2_RC_AUTH_FAIL`, `TPM2_RC_POLICY_FAIL`, `TPM2_RC_SIZE`, and resource-manager layered `TPM2_RC_COMMAND_CODE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2_tests.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2_tests.py

## Purpose
This unittest suite validates TPM2 driver and resource-manager behavior through the local `tpm2.Client`. It covers sealing/unsealing, PCR-bound policies, wrong-auth and wrong-policy failures, malformed command handling, partial reads, TPM spaces, invalid command handling, and nonblocking clients.

## Important APIs, Types, and Functions
`SmokeTest` creates a raw `Client` and root key, then tests auth sealing, PCR policy sealing, wrong auth, wrong PCR policy, too-long auth, too-short commands, partial reads, response overwrite after partial read, and two in-flight command rejection. `SpaceTest` opens `Client.FLAG_SPACE` resource-manager clients to test multiple spaces, flushing, handle visibility, and invalid command RC layering. `AsyncTest` uses `Client.FLAG_NONBLOCK` with and without `FLAG_SPACE`.

## Control Flow
Each smoke test starts with a root key in `setUp()` and flushes it in `tearDown()`. Policy tests create trial sessions to compute policy digests, then real policy sessions to authorize unseal. Wrong-policy mutates a non-policy PCR first to prove success, then mutates a policy PCR to expect failure. Space tests create clients against `/dev/tpmrm0` and inspect handles visible in a specific space. Async tests invoke capability and invalid flush operations through nonblocking reads.

## State and Persistence
The tests create TPM transient objects and sessions and generally flush roots/sessions they own. PCR extension in the policy test mutates PCRs and is persistent until TPM reset/reboot. Log files `SpaceTest.log` and `AsyncTest.log` may be created in the working directory.

## Dependencies and Integration Points
It depends on the local `tpm2.py`, Python unittest, TPM2 hardware or emulator, `/dev/tpm0`, `/dev/tpmrm0`, and resource-manager semantics.

## Risks
PCR mutation can affect later tests and cannot be undone by the suite. Several `try/except: pass` blocks in raw I/O tests can mask unexpected exceptions before assertions check derived variables. Timing and nonblocking behavior depend on driver implementation. TPM dictionary lockout or hierarchy authorization state can affect object creation and unseal outcomes.

## Test Signals
Signals include successful seal/unseal data equality, exact TPM RCs for auth/policy/size/invalid-command failures, correct partial response lengths for `GET_RANDOM`, `IOError` on malformed or concurrent raw commands, per-space handle isolation, and `EINVAL` for invalid nonblocking context flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tpm2/tpm2_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/Makefile

## Purpose
This Makefile builds the TTY selftest binaries for timestamp updates and `TIOCSTI` behavior.

## Important APIs, Types, and Functions
It sets `CFLAGS = -O2 -Wall`, declares `TEST_GEN_PROGS := tty_tstamp_update tty_tiocsti_test`, adds `LDLIBS += -lcap`, includes `../lib.mk`, and explicitly links `tty_tiocsti_test` with libcap.

## Control Flow
There is no runtime control flow. The build compiles the two test programs and links libcap for capability inspection/manipulation.

## State and Persistence
Only build outputs are affected.

## Dependencies and Integration Points
It depends on kselftest `lib.mk`, libcap development headers/libraries, and the adjacent C tests.

## Risks
Systems without libcap build dependencies cannot build `tty_tiocsti_test`.

## Test Signals
Successful compilation of both TTY selftests is this file's signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/config

## Purpose
This kselftest config fragment requests kernel support needed by the TIOCSTI legacy behavior test.

## Important APIs, Types, and Functions
It contains `CONFIG_LEGACY_TIOCSTI=y`.

## Control Flow
No runtime control flow exists. The config is consumed by selftest/kernel config tooling.

## State and Persistence
It does not mutate runtime state.

## Dependencies and Integration Points
It integrates with kselftest config checks to indicate that legacy TIOCSTI support should be enabled for this test area.

## Risks
If kernels are built without this option, parts of `tty_tiocsti_test` may skip or behave differently.

## Test Signals
The signal is configuration intent rather than executable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tiocsti_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tiocsti_test.c

## Purpose
This kselftest harness validates `TIOCSTI` input injection behavior across the `dev.tty.legacy_tiocsti` sysctl, `CAP_SYS_ADMIN`, controlling-terminal status, and file descriptor passing via `SCM_RIGHTS`. It also demonstrates the credential model where the current process credentials, not opener credentials, control injection permission.

## Important APIs, Types, and Functions
The file uses `kselftest_harness.h` fixtures and variants. Helpers include `send_fd_via_socket()`, `recv_fd_via_socket()`, `has_cap_sys_admin()`, `drop_all_privs()`, `get_legacy_tiocsti_setting()`, `set_legacy_tiocsti_setting()`, `test_tiocsti_injection()`, `run_basic_tiocsti_test()`, and `run_fdpass_tiocsti_test()`. It uses `openpty()`, `ioctl(TIOCSTI)`, `ioctl(TIOCSCTTY)`, `socketpair()`, `sendmsg/recvmsg(SCM_RIGHTS)`, `cap_get_proc()`, `cap_set_proc()`, `setuid/setgid`, and `prctl(PR_SET_NO_NEW_PRIVS)`.

## Control Flow
Fixture variants enumerate basic PTY tests and FD-passing tests for controlling and non-controlling terminals, permissive/restricted sysctl settings, and with/without `CAP_SYS_ADMIN`. Setup creates a PTY, reads/restores the sysctl, checks initial capabilities, and skips unsupported combinations. The single fixture test forks: basic mode performs injection in the child after optional privilege drop and optional controlling-terminal setup; FD-passing mode has the child create/pass a PTY slave FD and the privileged parent attempts injection through the received FD.

## State and Persistence
The fixture temporarily changes `/proc/sys/dev/tty/legacy_tiocsti` and restores it in teardown. Children may create sessions, controlling terminals, PTYs, and dropped credentials. File descriptors are closed in normal paths.

## Dependencies and Integration Points
It depends on libcap, PTYs, Unix domain sockets, root/CAP_SYS_ADMIN for several variants, kernel sysctl `dev.tty.legacy_tiocsti`, and the kselftest harness.

## Risks
The test assumes uid/gid 1000 exist for privilege dropping. Missing sysctl or insufficient permission causes skips. Because it forks and manipulates sessions/controlling terminals, assertion failures in children are reported through wait status. The FD-passing cases intentionally exercise a security-sensitive behavior and require careful interpretation of expected success.

## Test Signals
Expected results are exact `0`, `-EIO`, or `-EPERM` outcomes from `ioctl(TIOCSTI)`. Passing means the kernel enforces legacy sysctl and capability/controlling-terminal checks exactly as represented by the matrix, including current-credential behavior after FD passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tiocsti_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tstamp_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tstamp_update.c

## Purpose
This test verifies that writing to `/dev/tty` updates the access or modification timestamps of the process's controlling terminal device.

## Important APIs, Types, and Functions
`tty_valid()` accepts `/dev/tty*` and `/dev/pts*` paths. `write_dev_tty()` opens `/dev/tty` for read/write and prints a line. `main()` uses `readlink("/proc/self/fd/0")`, `stat()`, `sleep(10)`, and kselftest result reporting.

## Control Flow
The program reads fd 0's terminal path, skips if it is not a recognized tty path, stats it, sleeps 10 seconds to cross timestamp granularity/lazytime thresholds, writes to `/dev/tty`, stats it again, and passes if either atime or mtime seconds changed.

## State and Persistence
It writes a visible line to the controlling terminal and updates device inode timestamps. No files are created.

## Dependencies and Integration Points
It requires a valid controlling terminal on stdin, `/dev/tty` access, and kselftest output helpers.

## Risks
Non-interactive test runners often lack a tty and will skip. Timestamp behavior can depend on filesystem/device timestamp policies, but the 10 second sleep is designed to observe known delayed updates.

## Test Signals
Pass means terminal timestamps changed after a `/dev/tty` write. Skip means stdin is not a supported tty path. Failure means write/stat failed or timestamps did not update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tstamp_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/added_perf_counters.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/added_perf_counters.py

## Purpose
This Python selftest validates turbostat's `--add perf/...` support by adding available perf counters and checking that turbostat output contains the requested columns in normal and debug modes.

## Important APIs, Types, and Functions
`PerfCounterInfo` formats perf event names and turbostat `--add` IDs. `PERF_COUNTERS_CANDIDATES` includes MSR counters and core/package C-state residency events. `check_perf_access()` probes counters with `perf stat`. `check_columns_or_fail()` compares expected and actual tab-separated output columns. The script uses `which()`, `subprocess.run()`, `turbostat --list`, and `timeout`.

## Control Flow
The script probes readable perf counters, skips if none are usable, locates `turbostat` and `timeout`, builds `--add` arguments for present counters with cpu/core/package scopes, runs turbostat with `--show CPU`, validates output columns, appends `--debug`, and validates the debug header including default debug columns.

## State and Persistence
It does not persist state. It launches short-lived `perf`, `timeout`, and `turbostat` processes.

## Dependencies and Integration Points
It depends on installed `perf`, `turbostat`, `timeout`, PMU counter availability, and permissions to read perf events.

## Risks
Hardware-dependent counters may be absent or permission-restricted. The script exits 0 when no counters are readable, using printed `SKIP` text rather than kselftest's numeric skip code. Header matching is exact and can fail on harmless column renames/order changes.

## Test Signals
Pass means all requested `--add` perf counters appear as columns in normal mode and debug mode includes `usec`, `Time_Of_Day_Seconds`, `APIC`, `X2APIC`, plus requested columns. Failure means turbostat execution or header generation regressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/added_perf_counters.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/defcolumns.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/defcolumns.py

## Purpose
This Python test checks that turbostat's default output header matches `turbostat --list`, with debug-only columns handled separately.

## Important APIs, Types, and Functions
The script uses `which()`, `subprocess.run()`, `turbostat --list`, `timeout --preserve-status -s SIGINT`, and byte-string header comparisons. It derives `expected_columns_debug` from `--list`, then removes `usec`, `Time_Of_Day_Seconds`, `X2APIC`, and `APIC` for normal expected columns.

## Control Flow
It locates `turbostat` and `timeout`, captures `turbostat --list`, runs turbostat briefly with `-i 0.250`, compares the first output line to expected normal columns, reruns with `--debug`, and compares to debug columns.

## State and Persistence
No persistent state is written. The script runs short external commands.

## Dependencies and Integration Points
It depends on turbostat and coreutils timeout. It integrates with turbostat selftests as an executable Python script.

## Risks
The test compares exact byte headers, so column ordering, separator, default list, or debug-only column changes must be reflected in the script. It exits 1 rather than kselftest skip when required binaries are absent.

## Test Signals
Pass means normal and debug turbostat headers match `--list`-derived expectations. Failure indicates default column reporting drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/defcolumns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/smi_aperf_mperf.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/smi_aperf_mperf.py

## Purpose
This test validates turbostat columns that depend on SMI, APERF, and MPERF data across MSR-backed and perf-backed counter sources.

## Important APIs, Types, and Functions
`check_perf_access()` probes `msr/mperf/`, `msr/aperf/`, and `msr/smi/` with `perf stat`. `check_msr_access()` opens `/dev/cpu/<BASE_CPU>/msr` and uses `pread()` on IA32_MPERF and IA32_APERF MSRs. The script optionally uses `ctypes.CDLL(None).sched_getcpu()` to choose a base CPU. It runs turbostat with `--show` on `SMI`, `Avg_MHz`, `Busy%`, `Bzy_MHz`, and `IPC` when perf is available.

## Control Flow
The script discovers MSR and perf access, builds counter source options `--no-perf` and/or `--no-msr`, skips entirely if neither is available, locates turbostat and timeout, then for each dependent column and source option runs turbostat normally and with `--debug`, comparing exact headers.

## State and Persistence
No persistent state is written. It reads MSR device files and launches external processes.

## Dependencies and Integration Points
It depends on x86 MSR devices, perf event access, turbostat, timeout, and optional ctypes access to `sched_getcpu()`.

## Risks
Hardware and permission sensitivity is high. Missing MSR or perf access prunes parts of coverage. Exact header matching is brittle. `IPC` is skipped for `--no-perf` because it requires perf.

## Test Signals
Pass means each selected counter source reports the requested dependent column alone in normal mode and with default debug columns in debug mode. Skip text indicates unavailable counter sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/smi_aperf_mperf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/Makefile

## Purpose
This Makefile builds the ublk selftest userspace daemon `kublk`, the `metadata_size` utility, and a large suite of shell-driven ublk tests. It also defines convenience targets for running test groups sequentially or in parallel.

## Important APIs, Types, and Functions
It sets `CFLAGS` with optimization, warnings, UAPI include path, and optional `-Werror`; links pthread, math, and liburing; declares many `TEST_PROGS`; sets `TEST_GEN_PROGS_EXTENDED = kublk metadata_size`; and defines `run_<group>` and `run_all` targets parameterized by `JOBS`.

## Control Flow
`kublk` is built from all `.c` files except `metadata_size.c`; `metadata_size` is a standalone utility. The `check` target runs shellcheck. Group targets derive groups from `test_<group>_<num>.sh` names and either run through kselftest `RUN_TESTS` or `xargs -P` for parallel execution.

## State and Persistence
Build outputs are generated in the selftest output directory. Test runs create runtime devices and temporary files through shell scripts, not through this Makefile directly.

## Dependencies and Integration Points
It depends on liburing, pthreads, UAPI headers, kselftest `lib.mk`, shellcheck for `check`, and all adjacent ublk C/shell files.

## Risks
Parallel execution intentionally ignores aggregate `xargs` failure with `|| true`, so group parallel targets may need external result collection. The generated group list is naming-convention-dependent.

## Test Signals
Build success for `kublk` and `metadata_size` plus kselftest registration of shell scripts are the primary signals. Group targets provide operator-level smoke/stress execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/batch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/batch.c

## Purpose
This file implements `UBLK_F_BATCH_IO` support for the `kublk` userspace server. It manages batched prep/fetch/commit buffers, multishot fetch commands, command completion handling, and queue-to-thread mapping for batched ublk I/O.

## Important APIs, Types, and Functions
Buffer helpers include `ublk_get_commit_buf()`, `ublk_alloc_commit_buf()`, `ublk_free_commit_buf()`, `ublk_commit_elem_buf_size()`, and `ublk_commit_buf_size()`. Allocation paths are `ublk_batch_prepare()`, `ublk_batch_alloc_buf()`, and `ublk_batch_free_buf()`. I/O command paths include `ublk_batch_start_fetch()`, `ublk_batch_queue_prep_io_cmds()`, `ublk_batch_compl_cmd()`, `ublk_batch_prep_commit()`, `ublk_batch_complete_io()`, `ublk_batch_commit_io_cmds()`, and `ublk_batch_setup_map()`.

## Control Flow
At thread initialization, `ublk_batch_prepare()` computes per-thread queue count, commit element size, commit buffer counts, and command flags. `ublk_batch_alloc_buf()` allocates mlocked commit buffers and registered provided-buffer rings for fetch buffers. Startup prepares each mapped queue with `UBLK_U_IO_PREP_IO_CMDS` and posts two multishot `UBLK_U_IO_FETCH_IO_CMDS` per queue. CQEs either deliver fetched tags to target `queue_io`, complete prep/commit buffers, or restart fetch commands when buffers end.

## State and Persistence
State lives in `struct ublk_thread`: commit-buffer allocator, `batch_commit_buf` array, fetch buffers, buffer rings, command counters, and per-thread queue mapping. It is runtime-only and freed at thread teardown.

## Dependencies and Integration Points
It depends on `kublk.h`, liburing, ublk UAPI batch commands, queue target callbacks, and the allocator utilities. `kublk.c` calls these functions when `UBLK_F_BATCH_IO` is enabled.

## Risks
Batch mode has strict buffer-index and queue/thread mapping assumptions. Incorrect CQE sizes or duplicate fetched tags trigger assertions/logs. The mapping supports N:M threads/queues, but comments note some commit paths still assume constrained behavior. mlock failures are logged but not fatal.

## Test Signals
Batch shell tests exercise basic filesystem use, 4 threads/1 queue, and 1 thread/4 queues. Success indicates prep/fetch/commit command sequencing, buffer index calculation, and multishot fetch restart behavior are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/common.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/common.c

## Purpose
This file provides common backing-file setup and teardown for ublk targets that map block I/O onto regular files or block devices.

## Important APIs, Types, and Functions
`backing_file_tgt_init()` opens target backing files with `O_RDWR` and optional `O_DIRECT`, determines size via `fstat()` or `ioctl(BLKGETSIZE64)`, stores file descriptors in `dev->fds`, and records sizes. `backing_file_tgt_deinit()` fsyncs and closes backing file descriptors.

## Control Flow
Initialization asserts that only the ublk char device fd is registered, then iterates configured files. Regular files use `st_size`; block devices use `BLKGETSIZE64`; other file types fail. Teardown fsyncs/closes all backing fds from index 1 onward.

## State and Persistence
It opens and stores file descriptors in `struct ublk_dev`, and writes final data to backing files via fsync during teardown. File contents are persistent because target I/O uses these descriptors.

## Dependencies and Integration Points
It depends on `kublk.h`, Linux block ioctl definitions, and target initialization in `file_backed.c` and `stripe.c`.

## Risks
Partial initialization failures can leave earlier opened fds for caller cleanup. `O_DIRECT` requirements depend on filesystem alignment and target I/O buffer alignment.

## Test Signals
Successful target startup using loop or stripe backends indicates backing files were opened, sized, and registered correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/config

## Purpose
This config fragment requests the ublk kernel driver for the ublk selftests.

## Important APIs, Types, and Functions
It contains `CONFIG_BLK_DEV_UBLK=m`.

## Control Flow
No runtime control flow exists. The fragment is consumed by kselftest config tooling.

## State and Persistence
It does not mutate state.

## Dependencies and Integration Points
The shell tests call `modprobe ublk_drv`; this config declares the needed driver as a module.

## Risks
If the driver is built out or absent, most ublk tests skip or fail due to missing `/dev/ublk-control`.

## Test Signals
The signal is configuration intent for kernel test environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/fault_inject.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/fault_inject.c

## Purpose
This target implements a synthetic ublk backend for fault-injection tests. It behaves like a large null device but can delay completions and intentionally kill the server during request fetch.

## Important APIs, Types, and Functions
`struct fi_opts` stores `delay_ns` and `die_during_fetch`. `ublk_fault_inject_tgt_init()` configures a 250 GiB device and integrity parameters. `ublk_fault_inject_pre_fetch_io()` can `SIGKILL` the server before fetching tag 1. `ublk_fault_inject_queue_io()` submits an io_uring timeout. `ublk_fault_inject_tgt_io_done()` completes the ublk I/O after `-ETIME`. Command parsing supports `--delay_us` and `--die_during_fetch`.

## Control Flow
Target initialization rejects auto zero-copy fallback, creates params, and stores options. Each queued I/O becomes a timeout SQE with duration derived from `delay_us`; completion expects `-ETIME` and returns the requested byte count. The pre-fetch hook can submit live commands and kill the process to simulate incomplete fetch teardown.

## State and Persistence
Runtime state is the heap `fi_opts` stored in `dev->private_data`. No backing storage exists.

## Dependencies and Integration Points
It depends on `kublk.h`, target callbacks, ublk params, io_uring timeout operations, and tests `test_generic_06.sh` and `test_generic_17.sh`.

## Risks
The target intentionally kills the process, so cleanup relies on kernel ublk teardown/recovery. Delay is nanosecond timeout based and scheduler-sensitive.

## Test Signals
Generic fault-injection tests expect fast I/O failure after daemon death and successful device deletion after incomplete recovery teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/fault_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/file_backed.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/file_backed.c

## Purpose
This file implements the `loop` ublk target, mapping ublk read/write/flush requests to a single data backing file, with optional integrity metadata file, zero-copy, auto buffer registration, shared-memory zero-copy, and user-copy integration.

## Important APIs, Types, and Functions
`ublk_to_uring_op()` maps ublk read/write to io_uring ops. `loop_queue_flush_io()`, `loop_queue_shmem_zc_io()`, `loop_queue_tgt_rw_io()`, and `loop_queue_tgt_io()` prepare target SQEs. `ublk_loop_queue_io()` queues target work. `ublk_loop_io_done()` aggregates completion results. `ublk_loop_memset_file()` initializes integrity metadata. `ublk_loop_tgt_init()` opens backing files and configures `struct ublk_params`.

## Control Flow
For read/write, the target chooses shared-memory zero-copy if `UBLK_IO_F_SHMEM_ZC` is set, otherwise handles integrity I/O to a second file when requested, then either submits direct read/write, auto-zc fixed-buffer operations, or explicit register/read/unregister sequences for zero-copy. Flush maps to `fsync`. Completion records the shortest data result, translates integrity bytes back to data length when needed, accounts for skipped buffer-register CQEs, and commits the ublk request when all target SQEs complete.

## State and Persistence
Persistent state is the backing data file and optional integrity file. Runtime state includes per-I/O buffers, integrity buffers, shared-memory registrations in `shmem_table`, and open fds stored in `dev->fds`.

## Dependencies and Integration Points
It depends on `common.c` backing file helpers, `kublk.c` shared-memory registration, liburing, ublk UAPI flags, and shell tests using `-t loop`, `-g`, `--auto_zc`, batch mode, and integrity options.

## Risks
Correctness depends on buffer alignment, fixed-file indexes, shared-memory index/offset decoding, and matching data/integrity file sizes. Unsupported discard/write-zeroes return `-ENOTSUP`. Auto-zc fallback is rejected at init.

## Test Signals
Filesystem mount tests and fio verify tests over loop-backed ublk devices signal correct data path behavior. Integrity tests depend on proper metadata sizing and initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/file_backed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.c

## Purpose
`kublk.c` is the main userspace ublk test daemon and CLI. It creates, starts, stops, recovers, lists, and resizes ublk devices; launches I/O handler threads; dispatches ublk requests to target backends; supports batch I/O, zero-copy, auto buffer registration, user-copy, integrity metadata, per-I/O daemon distribution, safe stop, and shared-memory zero-copy registration.

## Important APIs, Types, and Functions
Control wrappers include `ublk_ctrl_*()` functions for add/delete/start/stop/try-stop/recovery/get-info/set/get-params/features/update-size/quiesce. Device/thread setup includes `ublk_ctrl_init()`, `ublk_dev_prep()`, `ublk_queue_init()`, `ublk_thread_init()`, `ublk_start_daemon()`, `ublk_io_handler_fn()`, and `ublk_process_io()`. I/O paths include `ublk_queue_io_cmd()`, `ublk_submit_fetch_commands()`, `ublk_handle_uring_cmd()`, `ublk_handle_cqe()`, and target CQE dispatch. CLI commands are `add`, `recover`, `del`, `stop`, `list`, `features`, `update_size`, and `quiesce`.

## Control Flow
`main()` parses global and target-specific options into `struct dev_ctx`, validates incompatible copy modes and integrity requirements, lets the chosen target parse its options, and dispatches to a command. `cmd_dev_add()` usually double-forks a daemon, using shared memory and eventfd to report the allocated device ID back to the parent. `__cmd_dev_add()` queries kernel features, adds or starts recovery, initializes target and queues, starts handler threads, sets params, starts the device, and waits for threads to exit. Non-batch threads issue fetch/commit uring commands per tag; batch threads use batch prep/fetch/commit helpers. Delete/stop/list/update/quiesce commands issue synchronous control uring commands.

## State and Persistence
Runtime state is stored in `struct ublk_dev`, queues, thread rings, open fds, mapped command buffers, shared-memory registration table, and child daemon process state. Persistent state may be backing files and kernel ublk devices. The daemon creates `/run/ublk/ublkb<id>.sock` for shared-memory registration and removes it on shutdown.

## Dependencies and Integration Points
It depends on `/dev/ublk-control`, `/dev/ublkcN`, `/dev/ublkbN`, Linux ublk UAPI, liburing, pthreads, SysV shared memory, eventfd, inotify, Unix sockets, and target ops from `null.c`, `file_backed.c`, `stripe.c`, and `fault_inject.c`. Shell tests call this binary through `test_common.sh`.

## Risks
The daemon is concurrency-heavy: failures can stem from queue/thread mapping, fixed file indexes, CQE accounting, daemon death, recovery race windows, and cleanup of forked children. It rejects several incompatible option combinations, but newer kernel features require `feat_map` updates or `test_generic_13.sh` fails. Shared-memory zero-copy depends on fd passing, mmap lifetime, and registered virtual address matching.

## Test Signals
Signals come from shell tests: successful add/list/del, fio and filesystem I/O over targets, correct feature listing, update-size propagation, safe-stop busy behavior, per-I/O task balancing, fast daemon-death cleanup, and recovery teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.h

## Purpose
This internal header defines the shared data structures, constants, target interface, inline helpers, and cross-file prototypes for the `kublk` ublk selftest daemon.

## Important APIs, Types, and Functions
Major types include `struct dev_ctx`, `struct ublk_ctrl_cmd_data`, `struct ublk_io`, `struct ublk_tgt_ops`, `struct ublk_tgt`, `struct ublk_queue`, `struct ublk_thread`, `struct ublk_dev`, and batch/shmem helper structures. Inline helpers cover batch checks, integrity length conversion, user-copy offsets, encoded `user_data`, SQE allocation, fixed/raw fd mapping, buffer register commands, I/O completion, queue flags, and target dispatch accounting.

## Control Flow
The header has no standalone control flow, but its inline helpers are on hot paths. `build_user_data()` and decoders route CQEs to queue/tag/op/target handlers. `ublk_complete_io()` chooses batch commit or ordinary commit/fetch command. `ublk_queued_tgt_io()` either completes failed target setup immediately or tracks target SQE count.

## State and Persistence
It defines runtime state layouts for all ublk daemon objects. Persistent behavior is indirect through target backing files and kernel devices.

## Dependencies and Integration Points
It includes liburing, pthread/semaphore, mmap/ioctl/inotify/eventfd, `ublk_dep.h`, Linux `ublk_cmd.h`, and `utils.h`. All ublk C files include it.

## Risks
Bit packing in `build_user_data()` is central to CQE correctness; queue count/tag/op width assumptions are asserted but must stay aligned with constants. Inline buffer-index helpers must match batch and zero-copy registration behavior.

## Test Signals
Successful compilation and all ublk tests exercise this header. Failures often manifest as bad CQE routing, wrong buffer indexes, or incorrect completion accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/metadata_size.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/metadata_size.c

## Purpose
This standalone utility queries logical block metadata capabilities from a block device for ublk integrity tests.

## Important APIs, Types, and Functions
`main()` opens a block device and calls `ioctl(FS_IOC_GETLBMD_CAP, struct logical_block_metadata_cap *)`, then prints `metadata_size`, `pi_offset`, and `pi_tuple_size`.

## Control Flow
It requires exactly one device path argument, opens it read-only, performs the ioctl, prints fields on success, and exits nonzero on usage, open, or ioctl failure.

## State and Persistence
It reads kernel block-device metadata capability state and does not modify anything.

## Dependencies and Integration Points
It depends on Linux `fs.h` exposing `FS_IOC_GETLBMD_CAP` and `logical_block_metadata_cap`. `test_common.sh` invokes it through `_get_metadata_size()`.

## Risks
It assumes the queried device supports the ioctl. Output parsing in shell helpers depends on exact field labels.

## Test Signals
Printed numeric metadata fields allow integrity shell tests to assert the ublk device reports expected metadata settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/metadata_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/null.c

## Purpose
This file implements the synthetic `null` ublk target. It completes I/O without backing storage, while exercising normal completion, zero-copy, auto buffer registration, fallback registration failure, DMA alignment, and segment limit reporting.

## Important APIs, Types, and Functions
`ublk_null_tgt_init()` sets a 250 GiB device with basic, DMA, and segment params. `__setup_nop_io()` prepares `IORING_OP_NOP` with injected result and fixed-buffer flags. `null_queue_zc_io()` registers buffer, submits NOP, and unregisters. `null_queue_auto_zc_io()` submits a fixed-buffer NOP. `ublk_null_queue_io()` chooses normal, zc, or auto-zc behavior. `ublk_null_io_done()` aggregates CQEs. `ublk_null_buf_index()` can return an invalid index to force fallback.

## Control Flow
On normal non-zc I/O, the target immediately completes with requested byte count. On zero-copy paths, it queues io_uring NOP operations that inject a completion result and optionally wrap explicit buffer register/unregister commands. Completion ignores skipped successful register CQEs, records failures, and commits when all target SQEs are done.

## State and Persistence
No persistent data exists. Runtime state is per-I/O target counters and buffer indexes.

## Dependencies and Integration Points
It depends on io_uring NOP injected-result behavior, ublk params, target callbacks, and tests for zero-copy, auto buffer registration, safe stop, update size, balancing, and feature behavior.

## Risks
NOP fixed-buffer flags are guarded by local definitions in case headers lag kernel support. Auto-zc fallback intentionally returns invalid buffer indexes, so behavior depends on kernel fallback handling.

## Test Signals
Tests inspect sysfs DMA/segment limits, run fio over null devices, verify auto-zc fallback, check update-size and safe-stop, and trace per-thread I/O distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/stripe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/stripe.c

## Purpose
This file implements the `stripe` ublk target, distributing a single ublk block device across multiple equal-sized backing files using fixed-size chunks.

## Important APIs, Types, and Functions
Types `stripe_conf`, `stripe`, and `stripe_array` describe stripe layout and per-file iovec fragments. Helpers include `calculate_nr_vec()`, `alloc_stripe_array()`, `calculate_stripe_array()`, `stripe_to_uring_op()`, `stripe_queue_tgt_rw_io()`, `handle_flush()`, `ublk_stripe_queue_io()`, `ublk_stripe_io_done()`, `ublk_stripe_tgt_init()`, `ublk_stripe_cmd_line()`, and `ublk_stripe_usage()`.

## Control Flow
Read/write requests are split into one or more per-backing-file iovec runs based on start sector, chunk size, and number of files. The target submits readv/writev SQEs to registered backing file indexes, optionally wrapped in zero-copy buffer register/unregister. Flush submits fsync to every backing file. Initialization validates chunk size, opens all backing files, aligns sizes to chunk boundaries, requires equal sizes, computes aggregate capacity, and sizes SQ/CQ depths by queue depth and file count.

## State and Persistence
Persistent data is striped across backing files. Runtime state includes `stripe_conf` in `dev->private_data` and a per-I/O `stripe_array` freed after completion.

## Dependencies and Integration Points
It depends on `common.c` backing file setup, liburing readv/writev, target ops, and shell tests using `-t stripe`, `--auto_zc`, batch mode, and multiple backing files.

## Risks
All backing files must be equal size after chunk alignment. Integrity and auto-zc fallback are rejected. Incorrect stripe math can corrupt data placement or produce short I/O errors. Zero-copy uses a single buffer index across multiple vector SQEs.

## Test Signals
Mount and fio tests over stripe devices signal correct mapping. Batch and auto-zc tests add coverage for mixed feature paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/stripe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_01.sh

## Purpose
This shell test exercises basic `UBLK_F_BATCH_IO` behavior for loop and stripe targets.

## Important APIs, Types, and Functions
It sources `test_common.sh`, checks `_have_feature "BATCH_IO"`, uses `_prep_test`, `_create_backfile`, `_add_ublk_dev`, `_mkfs_mount_test`, `_cleanup_test`, and `_show_result`.

## Control Flow
The script skips without batch support, creates two 256 MiB backing files, adds a loop device with `-q 2 -b`, mounts/formats it, then adds a stripe device with `-b --auto_zc` over two files and runs the mount test.

## State and Persistence
Temporary backing files and ublk devices are created and removed by common cleanup.

## Dependencies and Integration Points
It depends on root, ublk driver, `kublk`, batch feature support, mkfs/mount helpers, and loop/stripe target implementations.

## Risks
Filesystem creation and mount require root and available ext4 tooling. The second device uses auto-zc with batch, so kernel feature mismatches can skip/fail.

## Test Signals
Pass means batch I/O supports basic filesystem operations for loop and stripe targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_01.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_02.sh

## Purpose
This test validates batch I/O with more userspace server threads than hardware queues: four threads servicing one queue.

## Important APIs, Types, and Functions
It uses `_have_feature "BATCH_IO"`, `_have_program fio`, `_create_backfile`, `_add_ublk_dev -t loop -q 1 --nthreads 4 -b`, and fio read/write workload.

## Control Flow
The script skips without batch or fio, creates a 512 MiB file, adds a one-queue loop device in batch mode with four threads, runs fio read/write with four jobs, records fio exit code, and cleans up.

## State and Persistence
It creates a temporary backing file and ublk device, both cleaned up after the test.

## Dependencies and Integration Points
It depends on `kublk` batch queue-to-thread mapping and fio.

## Risks
The scenario stresses N:M batch mapping, buffer indexes, and completion routing. Fio/environment failures surface as test failures.

## Test Signals
Pass means one queue can be serviced by multiple batch threads under fio load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_03.sh

## Purpose
This test validates batch I/O with fewer userspace server threads than hardware queues: one thread servicing four queues.

## Important APIs, Types, and Functions
It uses `_have_feature "BATCH_IO"`, `_have_program fio`, `_create_backfile`, `_add_ublk_dev -t loop -q 4 --nthreads 1 -b`, and fio read/write workload.

## Control Flow
The script skips without batch or fio, creates a 512 MiB backing file, adds a four-queue loop device with one batch thread, runs fio with four jobs, then cleans up.

## State and Persistence
Temporary backing file and ublk device state are removed by cleanup.

## Dependencies and Integration Points
It depends on `ublk_batch_setup_map()` assigning multiple queues to one thread and on loop target correctness.

## Risks
This stresses per-thread commit buffers for multiple queues and can expose queue index/buffer index bugs.

## Test Signals
Pass means one batch thread can service four queues under fio read/write load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_common.sh

## Purpose
This shell library provides shared setup, cleanup, device management, fio workloads, recovery workflows, feature detection, and result reporting for ublk selftests.

## Important APIs, Types, and Functions
Important helpers include `_have_program()`, `_ublk_sleep()`, `_get_disk_dev_t()`, `_get_disk_size()`, `_run_fio_verify_io()`, `_create_backfile()`, `_mkfs_mount_test()`, `_check_root()`, `_prep_test()`, `_cleanup_test()`, `_have_feature()`, `_create_ublk_dev()`, `_add_ublk_dev()`, `_recover_ublk_dev()`, `__ublk_quiesce_dev()`, `__ublk_kill_daemon()`, `_ublk_del_dev()`, `run_io_and_remove()`, `run_io_and_kill_daemon()`, `run_io_and_recover()`, and `_get_metadata_size()`.

## Control Flow
Test scripts source this file, call `_prep_test()` to require root, modprobe `ublk_drv`, create a temp test directory, and log to `/dev/kmsg`. Device creation wraps `kublk add/recover`, captures device IDs, optionally settles udev, and records devices for cleanup. Cleanup deletes tracked devices, removes temporary files, and logs completion. Reusable workflows run fio while deleting, killing, or recovering devices.

## State and Persistence
It manages `UBLK_TEST_DIR`, `UBLK_TMP`, `UBLK_BACKFILES`, and `.ublk_devs`. It creates temporary files/directories, ublk devices, filesystems, mounts, and kernel log messages. Cleanup is best effort.

## Dependencies and Integration Points
It depends on root, `modprobe`, `udevadm`, `fio`, `mkfs.ext4`, `mount`, `lsblk`, `stat`, and the local `kublk`/`metadata_size` binaries. All requested ublk shell tests use it.

## Risks
Cleanup failures can leave ublk devices or temp files. Some helpers use `sed -i`, `kill -9`, and background fio, so signal/error handling is important. Parallel test support uses `JOBS` to alter sleeps and can amplify resource contention.

## Test Signals
The library reports `[PASS]`, `[SKIP]`, or `[FAIL]` through `_show_result()` and exits nonzero on failures. Individual tests rely on its device creation and cleanup correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_02.sh

## Purpose
This test checks that ublk multi-queue dispatch does not reorder sequential writes unexpectedly.

## Important APIs, Types, and Functions
It uses `_have_program bpftrace`, `_have_program fio`, `_add_ublk_dev -t null -q 2`, `_get_disk_dev_t()`, `bpftrace trace/seq_io.bt`, `taskset`, and fio sequential write workload.

## Control Flow
The script skips without bpftrace or fio, adds a two-queue null device, starts a bpftrace probe waiting for a `BPFTRACE_READY` marker, runs a CPU-pinned direct sequential write workload, stops bpftrace, and fails if the trace output contains `out_of_order:`.

## State and Persistence
It creates a ublk null device, temporary trace output file, and background bpftrace process, all cleaned up on normal paths.

## Dependencies and Integration Points
It depends on trace scripts under `trace/`, bpftrace permissions, fio, taskset, and null target behavior.

## Risks
Probe attachment timing is handled by polling the ready marker. Tracing permissions or missing BTF can skip/fail. CPU pinning is used to focus queue behavior.

## Test Signals
Pass means no out-of-order events were observed by bpftrace during sequential writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_02.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_03.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_03.sh

## Purpose
This test verifies sysfs queue limits reported by a zero-copy null ublk device.

## Important APIs, Types, and Functions
It uses `_add_ublk_dev -t null -z` and reads `/sys/block/ublkbN/queue/dma_alignment`, `max_segments`, and `max_segment_size`.

## Control Flow
The script creates a zero-copy null device and expects DMA alignment `4095`, `max_segments` `32`, and `max_segment_size` `32768`. Any mismatch sets failure before cleanup.

## State and Persistence
It creates a temporary null ublk device and removes it after checking sysfs.

## Dependencies and Integration Points
It depends on null target params and kernel block queue sysfs reporting.

## Risks
Kernel queue-limit representation changes can break exact string checks. Zero-copy feature absence may cause device creation skip through common helpers.

## Test Signals
Pass means the null target's DMA and segment parameters are reflected in sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_03.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_06.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_06.sh

## Purpose
This fault-injection test checks that I/O fails quickly when the ublk server dies with I/O outstanding in the server.

## Important APIs, Types, and Functions
It creates a fault-inject device with `--delay_us 2000000`, starts a direct `dd` write from `/dev/urandom`, uses `__ublk_kill_daemon()` to force the daemon to `DEAD`, and measures shell `SECONDS`.

## Control Flow
The script starts one delayed direct write, kills the daemon, waits for `dd`, and fails if `dd` exits successfully or if elapsed time is at least 5 seconds. It expects fast failure rather than waiting for long block I/O timeout.

## State and Persistence
It creates a temporary fault-inject ublk device and background `dd` process, then cleans up.

## Dependencies and Integration Points
It depends on `fault_inject.c`, daemon death handling in the ublk driver, and common shell cleanup.

## Risks
Timing is scheduler-dependent, but the 5 second threshold allows some tolerance. If device cleanup hangs, the test runner may time out externally.

## Test Signals
Pass means outstanding I/O observes server death quickly and returns an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_06.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_07.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_07.sh

## Purpose
This test validates `UBLK_F_NEED_GET_DATA` mode on the loop target.

## Important APIs, Types, and Functions
It uses `_create_backfile`, `_add_ublk_dev -t loop -q 2 -g`, `_run_fio_verify_io()`, and `_mkfs_mount_test()`.

## Control Flow
The script skips without fio, creates a 256 MiB backing file, adds a loop device with get-data mode, runs fio write/verify across 256 MiB, then formats/mounts the device if fio succeeds.

## State and Persistence
Temporary backing file and ublk device are cleaned up by common cleanup.

## Dependencies and Integration Points
It depends on `kublk` handling `UBLK_IO_RES_NEED_GET_DATA`, loop target user data flow, fio, and ext4 mount tooling.

## Risks
The test exercises extra data fetch sequencing and can expose missing user-copy/data-copy transitions. It requires root and sufficient temp storage.

## Test Signals
Pass means fio verify and filesystem mount both succeed in get-data mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_07.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_08.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_08.sh

## Purpose
This test validates `UBLK_F_AUTO_BUF_REG` with loop and stripe targets.

## Important APIs, Types, and Functions
It checks `_have_feature "AUTO_BUF_REG"`, creates two backing files, adds `-t loop --auto_zc`, then adds `-t stripe --auto_zc`, and runs `_mkfs_mount_test()` on both.

## Control Flow
The script skips without auto-buffer registration support, creates backing files, verifies a loop auto-zc device with a mount test, then verifies a stripe auto-zc device with a mount test.

## State and Persistence
Temporary files and ublk devices are removed by cleanup.

## Dependencies and Integration Points
It depends on kernel auto buffer registration, loop and stripe target auto-zc paths, and mount tooling.

## Risks
Auto-zc depends on buffer indexes from target helpers and kernel registration behavior. Stripe rejects fallback mode, so only normal auto-zc is covered.

## Test Signals
Pass means filesystem operations work on both loop and stripe devices with automatic buffer registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_08.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_09.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_09.sh

## Purpose
This test covers auto buffer registration fallback on the null target.

## Important APIs, Types, and Functions
It checks `_have_feature "AUTO_BUF_REG"`, requires fio, creates a null device with `-z --auto_zc --auto_zc_fallback`, and runs fio read/write.

## Control Flow
The script adds the fallback-mode null device, runs a 256 MiB fio read/write workload, records exit status, cleans up, and reports.

## State and Persistence
Only a synthetic ublk null device is created and removed.

## Dependencies and Integration Points
It depends on null target invalid buffer-index fallback behavior and kernel `UBLK_IO_RES_NEED_REG_BUF` handling.

## Risks
The test relies on fallback being triggered by intentionally invalid buffer indexes. Fio availability and permissions are required.

## Test Signals
Pass means auto-zc fallback completes fio I/O successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_09.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_10.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_10.sh

## Purpose
This test verifies the ublk update-size feature.

## Important APIs, Types, and Functions
It checks `_have_feature "UPDATE_SIZE"`, creates a null device, reads size with `_get_disk_size()`, invokes `kublk update_size -n <id> -s <bytes>`, and reads the size again.

## Control Flow
The script halves the current block-device size, asks `kublk` to update the device size, and fails if the command fails or the observed block size does not equal the requested value.

## State and Persistence
It mutates the kernel-reported size of a temporary null ublk device and removes the device afterward.

## Dependencies and Integration Points
It depends on kernel `UBLK_F_UPDATE_SIZE`, `kublk` `update_size` command, and `lsblk`.

## Risks
Size must be aligned to logical block size; halving the default null size preserves alignment. Udev/lsblk timing can affect observed result.

## Test Signals
Pass means the block device reports the new requested size after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_10.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_12.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_12.sh

## Purpose
This test validates per-I/O daemon task distribution when load is imbalanced toward one queue.

## Important APIs, Types, and Functions
It uses bpftrace `trace/count_ios_per_tid.bt`, fio, `_add_ublk_dev -t null -q 4 -d 16 --nthreads 6 --per_io_tasks`, CPU-pinned fio, and trace output counting.

## Control Flow
The script starts bpftrace for the ublk device, issues direct writes pinned to CPU 0, stops tracing, and counts trace lines containing `@`. It expects all six server threads to handle some I/O.

## State and Persistence
It creates a null ublk device, background bpftrace process, and temporary output file, then cleans up.

## Dependencies and Integration Points
It depends on `kublk` per-I/O task scheduling, bpftrace, fio, and trace scripts.

## Risks
Tracing can fail due to permissions. The test checks participation, not equal distribution, because tag allocation may not be round-robin yet.

## Test Signals
Pass means every configured server thread handled at least one I/O despite CPU-pinned workload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_12.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_13.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_13.sh

## Purpose
This test ensures `kublk features` knows every feature bit exposed by the running kernel driver.

## Important APIs, Types, and Functions
It runs `${UBLK_PROG} features` and searches output for `unknown`.

## Control Flow
After standard prep, the script fails if any feature bit is printed as unknown, then cleans up.

## State and Persistence
No ublk device is created. A temporary test directory is created and removed by common setup/cleanup.

## Dependencies and Integration Points
It depends on `cmd_dev_get_features()` in `kublk.c` and its `feat_map`.

## Risks
Running an older selftest suite against a newer kernel with new ublk features will fail intentionally until the feature map is updated.

## Test Signals
Pass means every kernel-advertised ublk feature bit has a symbolic name in `kublk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_13.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_16.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_16.sh

## Purpose
This test validates `kublk stop --safe`, which should stop idle devices but reject devices with active openers.

## Important APIs, Types, and Functions
It checks `_have_feature "SAFE_STOP_DEV"`, creates null devices, invokes `${UBLK_PROG} stop -n <id> --safe`, opens a device with background `dd`, and deletes devices through `_ublk_del_dev()`.

## Control Flow
First it creates an idle null device and expects `stop --safe` to succeed, then deletes it. Second it creates another null device, starts a background direct read to keep it open, expects `stop --safe` to fail, kills `dd`, and deletes the device.

## State and Persistence
Temporary null ublk devices and a background `dd` process are cleaned up.

## Dependencies and Integration Points
It depends on kernel `UBLK_F_SAFE_STOP_DEV`, `kublk` try-stop command, and block device opener tracking.

## Risks
The busy test uses a short sleep for `dd` startup; slow systems could race if the opener is not established. Cleanup kills the background process best-effort.

## Test Signals
Pass means safe stop succeeds when idle and fails when the block device has an active opener.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_16.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_17.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_17.sh

## Purpose
This fault-injection recovery test verifies that a device can be deleted after a recovery daemon dies while only part of a queue's I/O has been fetched.

## Important APIs, Types, and Functions
It uses `_add_ublk_dev -t fault_inject -r 1`, `__ublk_kill_daemon()`, foreground `${UBLK_PROG} recover ... --die_during_fetch 1`, and `_ublk_del_dev()`.

## Control Flow
The script creates a recoverable fault-inject device, kills the daemon and expects the device to become `QUIESCED`, then starts recovery in foreground with `die_during_fetch` enabled. It expects exit code 137 from SIGKILL and then deletes the device, relying on delete to complete only after teardown finishes.

## State and Persistence
It creates a ublk device in recovery mode and intentionally kills daemon processes. Cleanup deletes the device and temp directory.

## Dependencies and Integration Points
It depends on `fault_inject` pre-fetch kill behavior, ublk recovery/quiesce state handling, and daemon teardown paths in kernel and `kublk`.

## Risks
If teardown hangs, `_ublk_del_dev()` may hang until external timeout. The script references `$action` in one error message without defining it, but that does not affect control flow.

## Test Signals
Pass means recovery death produces SIGKILL exit status and device deletion succeeds afterward, proving incomplete recovery teardown completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_17.sh -->
