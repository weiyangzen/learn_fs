# sources/distributed-fs/ceph-client/tools/testing/selftests/syscall_user_dispatch/sud_test.c

## Purpose
Provides kselftest harness coverage for syscall user dispatch API behavior, signal delivery, emulated syscall return, dispatcher enable/disable, and inclusive/exclusive dispatch ranges.

## Important APIs, Types, And Functions
Uses `kselftest_harness.h` tests: `dispatch_trigger_sigsys`, `bad_prctl_param`, `dispatch_and_return`, `bad_selector`, `disable_dispatch`, `direct_dispatch_range`, and `dispatch_range`. Helpers include `prctl_valid()`, `prctl_invalid()`, `handle_sigsys()`, `setup_sigsys_handler()`, and `test_range()`. Globals `glob_sel`, `nr_syscalls_emulated`, `si_code`, `si_errno`, and `syscall_addr` capture handler state.

## Control Flow
Signal tests enable dispatch, block selector state, and expect SIGSYS termination or catchable handler paths. Parameter tests exercise invalid op codes, invalid off/size/selector combinations, overflow ranges, valid off mode, and inclusive mode validation. `dispatch_and_return()` verifies a magic syscall is a normal `-1` when dispatch is allowed, then becomes an emulated return value when dispatch is blocked and SIGSYS handling adjusts state. Range tests first learn the syscall instruction address from the handler and then verify exclusive and inclusive allowed ranges dispatch or bypass as expected.

## State And Persistence
State is process-global across individual test bodies but reset by tests before use. The selector byte is the kernel-observed switch. Handler-captured `syscall_addr` persists for later range tests.

## Dependencies And Integration Points
Depends on `PR_SET_SYSCALL_USER_DISPATCH` constants, `SYS_USER_DISPATCH` signal code, architecture-specific `ucontext_t` register adjustment for RISC-V, and kselftest harness signal-test support. The Makefile builds it as `sud_test`.

## Risks
Some behavior is architecture-specific: the comment notes syscall return emulation assumes `syscall(x) == x` except where adjusted for RISC-V. Test ordering matters because `dispatch_range()` relies on `syscall_addr` having been populated. Unsupported kernels are reported through failed `ASSERT_EQ(0, prctl(...))` blocks with explanatory logs rather than explicit skip in every path.

## Test Signals
Passing signals are SIGSYS raised when expected, invalid prctl parameters returning `EINVAL` or `EFAULT`, magic syscall emulation incrementing `nr_syscalls_emulated`, dispatch disable allowing `sysinfo`, direct allowed ranges bypassing dispatch, and JSON-free kselftest harness pass/fail output.
