<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/auxvec.h

Purpose: defines SH architecture-specific ELF auxiliary vector tags.

Important APIs/types/functions: `AT_FPUCW`, `AT_SYSINFO_EHDR`, cache-shape auxv tags, and `AT_VECTOR_SIZE_ARCH`.

Control flow: ELF loader fills these auxv entries for userspace startup.

State and persistence: state is process startup metadata copied to user stack.

Dependencies/integration: depends on CPU cache-shape globals set during CPU init and generic ELF binfmt.

Risks: tag renumbering breaks dynamic loaders and runtime cache probes.

Test signals: inspect auxv in SH userspace and verify cache shape values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/auxvec.h -->
