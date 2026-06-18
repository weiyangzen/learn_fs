<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sparsemem.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/sparsemem.h

**Purpose:** Defines sparsemem section sizing and maximum physical address width for Alpha.

**Important APIs/types/functions:** `SECTION_SIZE_BITS` as 27 and `MAX_PHYSMEM_BITS` as 48 under `CONFIG_SPARSEMEM`.

**Control flow:** Memory initialization uses these constants to divide physical memory into sparse sections and bound PFNs.

**State and persistence behavior:** No mutable state; constants shape memmap allocation and section lookup.

**Dependencies and integration points:** Depends on `CONFIG_SPARSEMEM` and Alpha architecture maximum physical-address limits.

**Risks:** Wrong section size wastes memory or breaks section indexing; wrong max bits can reject valid memory or overrun arrays.

**Test signals:** Sparsemem boot tests across low/high memory layouts and memory hotplug compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sparsemem.h -->
