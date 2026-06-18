<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sigcontext.h

Purpose: defines the user-visible SH signal context layout.

Important APIs/types/functions: `struct sigcontext` with GPRs, PC/PR/SR/GBR/MAC, FPU, xFPU, FPSCR/FPUL, and ownedfp.

Control flow: signal delivery writes this frame and sigreturn restores it.

State and persistence: state is user-stack signal-frame CPU context.

Dependencies/integration: integrates signal_32, ptrace register layouts, and libc signal trampolines.

Risks: any field movement or type change breaks old binaries.

Test signals: run signal frame ABI and FPU preservation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sigcontext.h -->
