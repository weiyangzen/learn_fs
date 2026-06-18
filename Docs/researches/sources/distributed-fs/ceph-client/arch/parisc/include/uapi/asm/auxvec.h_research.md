<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/auxvec.h

Source read size: 8 lines, 213 bytes.

Purpose: defines PA-RISC auxiliary vector keys visible to userspace. Important API: `AT_SYSINFO_EHDR` value 33 identifies the vDSO ELF header base. Control flow: exec setup places this auxv entry when a vDSO is mapped; userspace dynamic linkers read it. State and persistence: per-process auxv persists from exec until process exit. Dependencies and integration points: paired with vDSO mapping and libc/dynamic linker startup. Risks: changing the numeric value breaks userspace ABI. Test signals: inspect `/proc/self/auxv`, libc vdso detection, and signal/vdso startup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/auxvec.h -->
