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
