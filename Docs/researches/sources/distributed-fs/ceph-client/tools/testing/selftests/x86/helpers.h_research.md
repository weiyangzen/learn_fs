# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/helpers.h

## Purpose

`helpers.h` provides small shared helpers for x86 selftests: reading/writing EFLAGS and installing/removing SA_SIGINFO signal handlers with kselftest failure semantics.

## Important APIs, Types, and Functions

`get_eflags()` uses `__builtin_ia32_readeflags_u64()` or `_u32()`. `set_eflags()` uses `__builtin_ia32_writeeflags_u64()` or `_u32()`. `sethandler()` wraps `sigaction()` with `SA_SIGINFO | flags`, and `clearhandler()` restores `SIG_DFL`. Both fail with `ksft_exit_fail_msg()` on `sigaction` errors.

## Control Flow

Consumers include this header and call inline helpers directly. Signal helper setup zeroes `struct sigaction`, sets the callback/mask/flags, and installs it.

## State and Persistence Behavior

It mutates only the current process flags register or signal dispositions. There is no persistence.

## Dependencies and Integration Points

It depends on x86 compiler builtins, `<asm/processor-flags.h>`, POSIX signals, and `kselftest.h`.

## Risks and Edge Cases

Signal handlers installed through `sethandler()` always use `SA_SIGINFO`; callers needing a simple handler must adapt. Failure exits the test immediately, which is appropriate for setup helpers but not for optional signal paths.

## Test Signals

The helpers are validated indirectly by tests that depend on correct EFLAGS and signal-handler behavior.
