<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall.h

Purpose: Defines RISC-V syscall inspection and mutation helpers for tracing, seccomp, audit, and syscall restart.

Important APIs/types/functions: Includes `syscall_get_nr()`, `syscall_rollback()`, `syscall_get_error()`, `syscall_get_return_value()`, `syscall_set_return_value()`, `syscall_get_arguments()`, `syscall_set_arguments()`, and syscall work hooks.

Control flow: Helpers interpret `pt_regs.a7` as syscall number, `a0-a5` as arguments, and `orig_a0` for restart/rollback behavior.

State and persistence: State is the live `pt_regs` syscall frame.

Dependencies and integration points: Used by entry syscall path, ptrace, seccomp, audit, tracepoints, and restart logic.

Risks: Wrong argument ordering or error detection breaks tracing and seccomp decisions.

Test signals: strace/ptrace tests, seccomp selftests, syscall restart tests, audit, and compat syscall tests.

Source read size: 124 lines, 2924 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall.h -->
