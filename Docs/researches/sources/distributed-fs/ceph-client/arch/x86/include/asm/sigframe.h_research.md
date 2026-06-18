<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigframe.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sigframe.h

Purpose: declares internal x86 signal-frame layouts and helpers for native and compat signal delivery. Important types include signal frame structures for rt and legacy frames, embedded `ucontext`, siginfo, FPU frame placement, and optional compat variants.

Control flow: signal setup code builds these frames on the user stack, stores saved `pt_regs`, signal mask, siginfo/ucontext, and FPU/xstate frame, then arranges user return through sigreturn trampolines. Sigreturn reads the same layout to restore state.

State and persistence: frames are transient user-stack ABI data but persist until user signal handlers return. Dependencies include UAPI signal context, FPU/xstate, compat ABI, ptrace-visible regs, and altstack handling. Risks include stack alignment, frame-size miscalculation, user memory faults, and ABI drift. Test signals include signal delivery/return, altstack, SA_SIGINFO, 32-bit compat signals, xstate preservation, and malformed sigreturn tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigframe.h -->
