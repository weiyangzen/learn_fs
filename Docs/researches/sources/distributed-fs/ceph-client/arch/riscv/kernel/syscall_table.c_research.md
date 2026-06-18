<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/syscall_table.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/syscall_table.c

Purpose: Builds the RISC-V syscall dispatch table from generated syscall number headers.

Important APIs/types/functions: Defines syscall prototypes through `__SYSCALL` and initializes `sys_call_table[__NR_syscalls]`.

Control flow: No dynamic control flow; compile-time inclusion of `asm/unistd.h` expands native and compat syscall entries into table slots.

State and persistence: Produces the read-only syscall table used by trap/syscall entry.

Dependencies and integration points: Consumed by `do_trap_ecall_u()` in `traps.c` and generated syscall ABI headers.

Risks: Missing or wrong macro expansion breaks syscall numbering or dispatch. Compat/native wrapper naming must match architecture wrappers.

Test signals: Syscall ABI smoke tests, strace table validation, unimplemented syscall behavior, and allmodconfig build coverage.

Source read size: 24 lines, 687 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/syscall_table.c -->
