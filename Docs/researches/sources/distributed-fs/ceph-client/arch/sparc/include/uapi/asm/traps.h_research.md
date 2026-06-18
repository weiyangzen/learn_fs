<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/traps.h

Purpose: SPARC trap-table constants, instruction encoders, and trap classification macros.

Important APIs and control flow: defines `NUM_SPARC_TRAPS`, instruction-forming helpers for trap-table patching, hardware trap numbers, software trap numbers for SunOS/Solaris/NetBSD/Linux syscalls, PROM breakpoint traps, compatibility aliases, and macros to classify bad, hardware, software, and syscall traps.

State, dependencies, and risks: state is trap table contents and trap-level classification in low-level code. Dependencies include SPARC instruction encoding and architecture trap assignments. Risks are branch helper assumptions that destination follows instruction, wrong syscall trap classification, and debugger/PROM breakpoint incompatibility. Test signals are trap-table patching during boot, syscall entry for supported personalities, illegal/fault trap delivery, and BAD_TRAP_P coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/traps.h -->
