<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/uctx.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/uctx.h

Purpose: SPARC64 `getcontext`/`setcontext` machine-context register and FPU layout definitions.

Important APIs and control flow: defines general-register indexes for tstate, pc/npc, y, globals, outs, frame pointer, return pc, and count. `mc_fpu` contains single/double/quad views of FPU registers, FSR/FPRS/GSR, FQ pointer, queue count/entry size, and enable state. `mcontext_t` and `ucontext_t` combine registers, stack-link flags, signal mask, and context link.

State, dependencies, and risks: state is userspace context saved/restored by libc or signal/context APIs. Dependencies include `sigset_t` from signal headers and exact SPARC64 register semantics. Risks include pointer-size ABI, FPU queue handling, and mismatches with signal frame construction. Test signals are `getcontext`/`setcontext`/`swapcontext`, signal context inspection, FPU state preservation, and 64-bit userspace ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/uctx.h -->
