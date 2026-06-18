<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cache.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cache.h

**Purpose:** Defines MIPS cache line constants and cache initialization/probing function declarations.

**Important APIs/types/functions:** `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `__read_mostly`, and declarations for R3K/R4K/Octeon cache init plus cache size/line helpers.

**Control flow:** Header-only constants and externs.

**State, dependencies, integration:** Used by memory allocators, alignment, CPU cache setup, and architecture data placement.

**Risks and test signals:** Wrong L1 cache shift affects alignment and performance. Test cache init on supported CPU families and cache line constants in build configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cache.h -->
