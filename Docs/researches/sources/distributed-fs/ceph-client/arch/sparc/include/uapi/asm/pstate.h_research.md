<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/pstate.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/pstate.h

Purpose: Defines SPARC V9 PSTATE, TSTATE, FPRS, version-register, and compatibility-feature bit masks.

Important APIs and control flow: PSTATE constants describe interrupt/MMU globals, endian controls, memory model, RED, FPU enable, address mask, privilege, interrupts, and alternate globals; `PSTATE_MCDE` shares the IG bit on ADI-capable processors. TSTATE constants map global level, condition codes, ASI, PIL, embedded PSTATE, syscall marker, and CWP. FPRS constants expose FPU enable and dirty bits. Version and CFR masks expose CPU implementation and crypto/hash capability features.

State, dependencies, and risks: state is trap-frame and CPU privileged register content. Dependencies include assembly trap code, VIS/FPU helpers, ADI handling, signal/ptrace, and CPU feature reporting. Risks are overlapping IG/MCDE semantics, incorrect memory-model or privilege-bit manipulation, and ABI-visible debugger breakage. Test signals are trap entry/return, ptrace register views, VIS/FPU save/restore, ADI enablement, and CPU capability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/pstate.h -->
