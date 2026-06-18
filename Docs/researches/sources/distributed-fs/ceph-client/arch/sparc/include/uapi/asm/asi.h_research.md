<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/asi.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/asi.h

Purpose: Enumerates SPARC Address Space Identifier constants for sun4c/sun4m, LEON, V9, UltraSPARC, CMT, sun4v, and later SPARC cores.

Important APIs and control flow: the header is a constant map for alternate address-space load/store instructions. It includes legacy MMU/cache flush ASIs, LEON cache/MMU ASIs, V9 primary/secondary/no-fault/little-endian ASIs, physical bypass and block-load/store ASIs, diagnostic cache/tag ASIs, interrupt queue ASIs, MMU register spaces, ADI/MCD ASIs, and Niagara/T4+ PIC/crypto-era definitions.

State, dependencies, and risks: the state is CPU hardware addressing behavior selected by assembly and inline asm consumers. Dependencies include exact processor manuals and code using `ldxa/stxa/lduwa/lduha`. Risks are catastrophic if constants are altered, because wrong ASIs can access diagnostics, MMU, cache tags, physical memory, or hypervisor-related spaces. Test signals are architecture boot, cache/MMU flush tests, byte-swap inline asm, ADI tag operations, and trap handlers that read/write diagnostic registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/asi.h -->
