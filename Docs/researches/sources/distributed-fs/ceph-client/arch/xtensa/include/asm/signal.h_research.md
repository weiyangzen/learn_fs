<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/signal.h

Purpose: connects kernel Xtensa signal handling to UAPI signal definitions and advertises `__ARCH_HAS_SA_RESTORER`. It includes `uapi/asm/signal.h` and, for C kernel code, `asm/sigcontext.h`.

Control flow is delegated to `kernel/signal.c`; this header defines compile-time contracts for signal frames and restorer support. State is user-visible signal masks, action layout, and sigcontext data. Dependencies include UAPI signal ABI and sigcontext layout. Integration points are signal delivery/return, libc signal trampolines, ptrace signal stops, and `rt_sigreturn`. Risks are ABI breakage if restorer or sigcontext expectations change. Test signals include signal handler execution, alternate signal stack, rt_sigreturn, strace signal decoding, and libc compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/signal.h -->
