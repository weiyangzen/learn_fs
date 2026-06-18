<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace_32.h

Purpose: defines the 32-bit SH userspace register frame layout.

Important APIs/types/functions: `struct pt_regs`, `struct pt_dspregs`, register index macros for GPR, PC/PR/SR/GBR/MAC/FPU/FPSCR/FPUL.

Control flow: exception and ptrace code save/restore registers according to this layout and expose it to userspace.

State and persistence: per-task register state is copied into these structs on traps and ptrace calls.

Dependencies/integration: must match assembly offsets and signal context handling.

Risks: layout/index changes break debuggers, core dumps, signal frames, and syscall tracing.

Test signals: validate asm offsets, core dump notes, gdb register access, and signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace_32.h -->
