<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sigcontext.h

Purpose: exposes x86 signal-context UAPI definitions to kernel users. It primarily includes `uapi/asm/sigcontext.h`.

Control flow and state: signal delivery and return code use the UAPI structures to save/restore user-visible register and xstate context; this wrapper owns no state. Dependencies include the stable UAPI signal ABI and FPU/xstate layout. Risks are ABI breakage if the included definitions are changed incompatibly. Test signals include signal frame selftests, rt_sigreturn, FPU/xstate signal preservation, and compat signal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sigcontext.h -->
