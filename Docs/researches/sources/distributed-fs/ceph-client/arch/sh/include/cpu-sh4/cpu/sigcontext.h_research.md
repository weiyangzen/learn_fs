<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sigcontext.h

Purpose: declares the SH-4 CPU-local `struct sigcontext` layout used by signal delivery and restore code.

Important APIs/types/functions: `struct sigcontext` with oldmask, regs[16], pc, pr, sr, gbr, mach, macl, fpregs[16], xfpregs[16], fpscr, fpul, ownedfp.

Control flow: the file is a pure ABI type declaration; signal setup copies register/FPU state into this shape and sigreturn consumes the same offsets.

State and persistence: no persistence; the state is user-visible process signal-frame data and must stay layout-compatible.

Dependencies/integration: included by architecture signal code and mirrors the UAPI signal context expectations for SH-4 FPU state.

Risks: any field reorder or type-width change breaks signal ABI and user-space unwind/sigreturn.

Test signals: build asm offsets and run signal/FPU context save-restore tests on SH-4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sigcontext.h -->
