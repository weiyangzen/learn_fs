<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ptrace.h

Source read size: 96 lines, 2820 bytes.

Purpose: defines PA-RISC ptrace-visible register layouts and ptrace request numbers. Important APIs/types: legacy `struct pt_regs`, `struct user_regs_struct`, `struct user_fp_struct`, `PTRACE_SINGLEBLOCK`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, and `PTRACE_SETFPREGS`. Control flow: ptrace and regset code copy these structures for debuggers, strace, core dumps, and signal inspection. State and persistence: register snapshots are per-task transient but core-file and debugger ABI is stable. Dependencies and integration points: `entry.S`, signal frames, ELF gregset/fpregset, perf register enum, gdb/strace. Risks: comments note gdb/strace depend on size and offsets; changing layouts breaks object compatibility. Test signals: gdb single-step/block-step, ptrace GET/SETREGS/FPREGS, core dump register notes, and strace syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ptrace.h -->
