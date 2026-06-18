<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/auxvec.h

Purpose: Defines SPARC-specific ELF auxiliary-vector entries.

Important APIs and control flow: `AT_SYSINFO_EHDR` advertises the vDSO ELF header to userspace, and `AT_ADI_BLKSZ`, `AT_ADI_NBITS`, and `AT_ADI_UEONADI` advertise Application Data Integrity capability details.

State, dependencies, and risks: state is per-process auxv content produced at exec time. Dependencies include ELF loader setup, vDSO mapping, and ADI platform detection. Risks are ABI breakage if values change and incorrect ADI capability exposure causing applications to issue unsupported tagged-memory operations. Test signals are `/proc/self/auxv`, libc/vDSO startup, ADI-aware application probes, and exec tests on non-ADI systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/auxvec.h -->
