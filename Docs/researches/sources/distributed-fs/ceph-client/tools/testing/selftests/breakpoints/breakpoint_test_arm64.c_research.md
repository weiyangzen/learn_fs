# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test_arm64.c

## Purpose

This arm64 kselftest validates hardware watchpoint byte-selection behavior across write sizes and offsets. It checks that a watchpoint triggers only when the watched byte range overlaps the child write and that negative-offset boundary cases work.

## Important APIs, Types, and Functions

Important state is aligned volatile `var[96]`. Key functions are `child`, `set_watchpoint`, `run_test`, `sigalrm`, and `main`. It uses `PTRACE_TRACEME`, `PTRACE_SETREGSET` with `NT_ARM_HW_WATCH`, `PTRACE_CONT`, `PTRACE_GETSIGINFO`, `TRAP_HWBKPT`, `struct user_hwdebug_state`, `iovec`, and kselftest.

## Control Flow

For each write size from 1 to 32 bytes and nearby watchpoint offsets, `main` forks a child. The child stops under ptrace, writes using scalar stores or arm64 pair stores for 16/32-byte cases, and exits. The parent sets one hardware watchpoint with a byte mask derived from size and address offset, resumes the child with an alarm timeout, waits for SIGTRAP, validates `si_code == TRAP_HWBKPT`, kills the child, and compares the result to expected overlap.

## State and Persistence Behavior

State is limited to child watchpoint registers and the static `var` buffer. No persistent system state is modified.

## Dependencies and Integration Points

It depends on arm64 hardware watchpoint support, ptrace regset availability, and kselftest. The Makefile selects it only for arm64/aarch64.

## Risks and Test Signals

Risks include hardware lacking watchpoint support (`EIO`), incorrect byte-mask calculation for larger-than-8-byte writes, timeouts, and ptrace restrictions. Signals are 213 planned kselftest results, pass when `wr == wp` for overlap cases, pass for negative boundary checks, and final pass/fail aggregation.
