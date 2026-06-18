# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_benchmark.c

## Purpose
Benchmarks syscall user dispatch overhead while also smoke-testing SIGSYS trapping and selector behavior. It compares repeated native `sysinfo()` syscall timing before and after enabling dispatch.

## Important APIs, Types, And Functions
Important globals are `selector`, `trapped_call_count`, `native_call_count`, `factor`, and architecture-specific dispatcher symbols. Functions include `one_sysinfo_step()`, `calibrate_set()`, `perf_syscall()`, `handle_sigsys()`, and `main()`. It uses `prctl(PR_SET_SYSCALL_USER_DISPATCH, ...)`, `sigaction(SIGSYS, ...)`, `syscall(MAGIC_SYSCALL_1)`, `clock_gettime()`, and `sysinfo()`.

## Control Flow
`main()` calibrates a loop to roughly five seconds, measures baseline syscall time, installs a SIGSYS handler, enables syscall user dispatch with an allowed dispatcher range, blocks dispatch through `selector`, and performs a deliberately invalid syscall to verify trapping. The handler unblocks dispatch, records whether the trapped syscall was the magic one, and on x86_64 emits inline assembly to test returning through a dispatcher-area syscall with the selector blocked. The program then unblocks dispatch, measures syscall time again, and reports overhead.

## State And Persistence
State is process-global and volatile during the benchmark: selector byte controls dispatch, counters record trapped/native unexpected syscalls, and `factor` controls iteration count. No state persists beyond process exit.

## Dependencies And Integration Points
Depends on syscall user dispatch prctl support, SIGSYS signal ABI fields, architecture-specific syscall argument/return behavior, and x86 dispatcher labels for `TEST_BLOCKED_RETURN`. It integrates with kselftest as a generated benchmark binary rather than the main pass/fail harness.

## Risks
The benchmark is architecture-sensitive and uses inline assembly on x86_64. `printf` is avoided in the signal handler except via `snprintf` plus `write`, but `snprintf` itself is not async-signal-safe. Timing is noisy and calibration scales `factor` in coarse steps. The fallback syscall number must remain invalid on the target architecture.

## Test Signals
Signals include a successful prctl enable, at least one trapped magic syscall, selector still blocked after the blocked-return test on supported architectures, zero unexpected native dispatches, and a printed overhead percentage.
