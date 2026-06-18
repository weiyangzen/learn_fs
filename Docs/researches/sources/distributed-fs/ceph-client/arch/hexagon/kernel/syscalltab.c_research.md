# sources/distributed-fs/ceph-client/arch/hexagon/kernel/syscalltab.c

## Purpose

`syscalltab.c` builds the Hexagon syscall dispatch table from generated syscall metadata. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The main object is `sys_call_table[__NR_syscalls]`; macros map generic syscall names and Hexagon-specific aliases such as `sys_sync_file_range`. Concrete declarations observed in the file: Includes: `linux/syscalls.h`, `linux/signal.h`, `linux/unistd.h`, `asm/syscall.h`, `asm/syscall_table_32.h`. Macros: `__SYSCALL`, `__SYSCALL_WITH_COMPAT`, `sys_mmap2`, `sys_fadvise64_64`, `sys_sync_file_range`. Functions/syscalls: `hexagon_fadvise64_64`.

## Control Flow, State, And Persistence

No active control flow exists here; `traps.c` indexes the table after validating the syscall number.

## Dependencies And Integration Points

It integrates with generated `asm/syscall_table_32.h`, `unistd.h`, syscall wrappers, and ptrace/seccomp paths.

## Risks And Test Signals

Risks are table size drift or wrong aliasing. Test signals are syscall smoke tests, strace syscall names, and generated-table build checks.
 A local static signal for this file is that it has 31 lines and 785 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
