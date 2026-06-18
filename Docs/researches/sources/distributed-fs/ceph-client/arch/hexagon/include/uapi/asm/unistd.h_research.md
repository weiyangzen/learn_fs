# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/unistd.h

## Purpose

`unistd.h` provides Hexagon syscall-number UAPI glue. It includes generated `asm/unistd_32.h` and aliases `__NR_sync_file_range2` to syscall number 84 for the architecture-specific syscall table. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public API is the syscall number namespace consumed by libc, seccomp, ptrace, and kernel syscall dispatch. Concrete declarations observed in the file: Includes: `asm/unistd_32.h`. Macros: `__NR_sync_file_range2`.

## Control Flow, State, And Persistence

No executable flow exists in the header; at runtime the numbers are consumed by `do_trap0` and `sys_call_table` dispatch.

## Dependencies And Integration Points

It integrates with generated syscall headers, `kernel/syscalltab.c`, `kernel/signal.c` restart handling, and userspace syscall wrappers.

## Risks And Test Signals

Risks are syscall-number ABI drift and mismatch between UAPI numbers and `sys_call_table`. Test signals are syscall table generation, strace/seccomp syscall-number checks, and runtime syscall smoke tests.
 A local static signal for this file is that it has 34 lines and 1231 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
