<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_table.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_table.h

Purpose: Declares the RISC-V syscall table symbol consumed by entry/syscall dispatch code.

Important APIs/types/functions: Exports `sys_call_table[]` as an array of syscall handler pointers.

Control flow: No runtime flow in the header; assembly/C syscall entry indexes this table by syscall number.

State and persistence: Table contents are generated/linked elsewhere and persist for kernel lifetime.

Dependencies and integration points: Integrates with syscall table generation, unistd numbers, compat table support, and entry.S.

Risks: Table type or number mismatch dispatches the wrong syscall.

Test signals: Syscall ABI selftests, generated table build checks, seccomp/audit, and compat syscall matrix.

Source read size: 7 lines, 137 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_table.h -->
