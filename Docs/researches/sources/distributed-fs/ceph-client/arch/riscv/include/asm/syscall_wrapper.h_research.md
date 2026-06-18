<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_wrapper.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_wrapper.h

Purpose: Provides RISC-V syscall wrapper macros that adapt generic syscall declarations to pt_regs-based entry calling conventions.

Important APIs/types/functions: Defines `SC_RISCV_REGS_TO_ARGS`, `__SYSCALL_DEFINEx`, `__ARCH_WANT_SYS_*` wrapper behavior, and compat wrapper variants.

Control flow: Macros generate wrapper functions that extract arguments from `pt_regs` registers and call the typed syscall implementation.

State and persistence: No persistent state; wrappers operate on each syscall frame.

Dependencies and integration points: Used by syscall definition expansion, trace metadata, compat syscalls, and generated syscall tables.

Risks: Argument extraction errors produce ABI-visible syscall corruption, especially for 64-bit arguments and compat calls.

Test signals: Syscall selftests, compat syscall tests, tracing metadata builds, and generated wrapper compile checks.

Source read size: 108 lines, 4052 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_wrapper.h -->
