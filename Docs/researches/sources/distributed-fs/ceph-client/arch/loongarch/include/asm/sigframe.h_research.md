<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sigframe.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sigframe.h

Purpose: defines the LoongArch runtime signal frame layout used by signal delivery and `rt_sigreturn`.
Important APIs and types: declares `struct rt_sigframe` containing siginfo, ucontext, and trampoline space.
Control flow: signal setup writes this frame on the user stack; `rt_sigreturn` reads it to restore user register and extended context state.
State and persistence: the frame is user-visible ABI state during signal handlers and must remain layout-compatible.
Dependencies and integration: integrates with `kernel/signal.c`, UAPI `sigcontext.h`, `ucontext.h`, vdso signal return, FPU/LSX/LASX/LBT extended context handling, and user stacks.
Risks and test signals: layout drift breaks signal handlers, debuggers, and libcs. Signals include signal ABI tests, sigaltstack, vector-state signal restore, and ptrace over signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sigframe.h -->
