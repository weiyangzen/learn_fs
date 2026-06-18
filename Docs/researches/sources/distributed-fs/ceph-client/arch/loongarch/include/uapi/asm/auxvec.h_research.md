<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/auxvec.h

Purpose: defines LoongArch ELF auxiliary-vector architecture entries.
Important APIs and types: defines `AT_SYSINFO_EHDR` for vDSO discovery and `AT_VECTOR_SIZE_ARCH` sizing.
Control flow: ELF loader populates auxvec for new processes; libc reads it to locate the vDSO.
State and persistence: auxvec entries are per-process ABI data visible to userspace.
Dependencies and integration: integrates with ELF exec, vDSO mapping, dynamic loaders, and libc clock/signal fast paths.
Risks and test signals: wrong constants break vDSO discovery. Signals include auxvec inspection, libc startup, and vDSO tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/auxvec.h -->
