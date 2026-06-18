<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psr.h

Purpose: Defines SPARC V8 Processor Status Register bit masks and field shifts.

Important APIs and control flow: constants cover CWP, trap enable, privilege bits, interrupt priority level, FPU/coprocessor enable, syscall marker, SuperSPARC little-endian bit, integer condition codes, implementation/version fields, and known implementation IDs for TI and LEON. Assembly and ptrace-style code use these to interpret or synthesize PSR state.

State, dependencies, and risks: state is hardware PSR and trap-frame PSR images. Dependencies include V8 CPU semantics and `ptrace.h` consumers. Risks are wrong privilege/interrupt/FPU interpretation and incompatibility with register dump tools. Test signals are trap-frame decode, ptrace get/set registers, FPU enable paths, and LEON CPU identification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psr.h -->
