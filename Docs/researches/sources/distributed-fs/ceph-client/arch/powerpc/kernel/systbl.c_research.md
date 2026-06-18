# sources/distributed-fs/ceph-client/arch/powerpc/kernel/systbl.c

## Purpose
Defines PowerPC native and compat syscall function tables from generated syscall table headers.

## Important APIs, Types, and Functions
- `sys_call_table[]` includes either `syscall_table_64.h` or `syscall_table_32.h`.
- `compat_sys_call_table[]` includes 32-bit table entries with compat handlers when `CONFIG_COMPAT` is enabled.
- `__SYSCALL` macro casts handlers to common `syscall_fn` when syscall wrappers are not used.

## Control Flow and State
This is static table initialization at build time; runtime syscall dispatch indexes these arrays in `system_call_exception()`.

## State and Persistence Behavior
Exports read-only syscall dispatch tables in kernel memory.

## Dependencies and Integration Points
Depends on generated headers from `kernel/syscalls/Makefile`, `asm/syscalls.h`, and `CONFIG_ARCH_HAS_SYSCALL_WRAPPER` calling convention.

## Risks
Mismatched generated headers or wrong compat macro expansion can dispatch to native handlers with compat arguments or vice versa. Casts are intentional but hide type mismatches when wrappers are disabled.

## Test Signals
Build native 32-bit, native 64-bit, and compat configs; run syscall ABI tests; verify unknown syscall bounds in `system_call_exception()` and table size match `NR_syscalls`.
