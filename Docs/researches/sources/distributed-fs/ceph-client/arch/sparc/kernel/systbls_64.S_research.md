# sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls_64.S

Purpose: materializes sparc64 native and optional compat syscall tables from generated include files.

Important APIs/symbols: defines `sys_call_table32` under `CONFIG_COMPAT`, and aliases `sys_call_table64` and `sys_call_table` for native 64-bit syscalls. Entries are emitted with `.word`. `__SYSCALL_WITH_COMPAT()` resolves to compat handlers for the 32-bit table and native handlers for the 64-bit table.

Control flow: no executable flow; assembly syscall dispatch loads table entries indexed by syscall number.

State and persistence: creates read-only/text-section syscall address tables used at runtime.

Dependencies and integration points: depends on generated `syscall_table_32.h` and `syscall_table_64.h`, `CONFIG_COMPAT`, and `syscalls.S` dispatch code.

Risks: entry size and symbol alignment must match dispatch's `lduw` table loads. Compat/native macro definitions must be reset correctly around includes.

Test signals: native and compat syscall table lookup, builds with and without `CONFIG_COMPAT`, generated table content inspection, and syscall ABI smoke tests.
