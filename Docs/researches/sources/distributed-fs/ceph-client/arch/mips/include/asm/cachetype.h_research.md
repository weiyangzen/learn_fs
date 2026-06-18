<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cachetype.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cachetype.h

**Purpose:** Exposes MIPS cache aliasing information through the generic cachetype interface.

**Important APIs/types/functions:** `cpu_dcache_is_aliasing()` maps to `cpu_has_dc_aliases`.

**Control flow:** Inline macro only.

**State, dependencies, integration:** Depends on CPU feature detection and is consumed by generic cache/MM code.

**Risks and test signals:** Incorrect alias reporting leads to missing flushes or unnecessary overhead. Test on aliasing and non-aliasing D-cache CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cachetype.h -->
