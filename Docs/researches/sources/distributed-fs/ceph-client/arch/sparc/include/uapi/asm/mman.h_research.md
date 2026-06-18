<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/mman.h

Purpose: SPARC memory-mapping constants layered on common generic mmap definitions.

Important APIs and control flow: adds `PROT_ADI`, SunOS compatibility names such as `MAP_RENAME`, SPARC-specific `MAP_NORESERVE`, `MAP_INHERIT`, `MAP_LOCKED`, `_MAP_NEW`, stack/executable flags, and mlockall flags. These constants feed mmap/mprotect/mlock syscall decoding.

State, dependencies, and risks: state is VMA protection and mapping policy. Dependencies include generic mman common definitions and ADI-capable MM code. Risks include flag collisions, exposing `PROT_ADI` on unsupported platforms, and legacy `_MAP_NEW` compatibility. Test signals are mmap/mprotect flag tests, ADI protected mappings, mlockall behavior, and SunOS-compat application probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/mman.h -->
