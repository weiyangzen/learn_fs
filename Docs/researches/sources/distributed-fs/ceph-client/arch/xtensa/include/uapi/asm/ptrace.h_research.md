<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ptrace.h

Purpose: defines UAPI ptrace register numbers, ptrace request numbers, FDPIC selector constants, and `struct user_pt_regs`. Important constants include `REG_A_BASE`, `REG_AR_BASE`, `REG_PC`, `REG_PS`, `REG_WB`, `REG_WS`, `REG_LBEG`, `REG_LEND`, `REG_LCOUNT`, `REG_SAR`, `SYSCALL_NR`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETXTREGS`, `PTRACE_SETXTREGS`, `PTRACE_GETHBPREGS`, `PTRACE_SETHBPREGS`, and `PTRACE_GETFDPIC`.

Control flow is implemented in `kernel/ptrace.c`, which maps this ABI to internal `pt_regs` and TIE/coprocessor state. Persistent state is debugger-visible task register state. Dependencies include `linux/types.h` and Xtensa register-window architecture. Integration points are strace, gdb, core dump regsets, hardware breakpoints, syscall tracing, and FDPIC loaders. Risks include ABI structure size/offset regressions, windowbase/windowstart rotation mistakes, and reserved field misuse. Test signals include ptrace GET/SETREGS/GETXTREGS, gdb single-step, hardware breakpoint ptrace operations, strace syscall number reads, and core dump register notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ptrace.h -->
