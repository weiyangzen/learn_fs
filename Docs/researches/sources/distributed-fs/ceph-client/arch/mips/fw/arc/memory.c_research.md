<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/memory.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/memory.c

**Purpose:** Converts ARC/ARCS firmware memory descriptors into Linux `memblock` regions and later frees temporary PROM memory when safe.

**Important APIs/types/functions:** `prom_meminit()` walks `ArcGetMemoryDescriptor()`. `prom_memtype_classify()` selects ARC versus ARCS memory type rules using `prom_flags`. `prom_free_prom_memory()` frees recorded firmware temporary regions unless `PROM_FLAG_DONT_FREE_TEMP` is set. `prom_cleanup()` is a weak platform hook.

**Control flow:** Descriptor pages are shifted by `ARC_PAGE_SHIFT` to bytes, mirrored RAM below `PHYS_OFFSET` is ignored, all regions are added to memblock, reserved and firmware-temporary regions are reserved, and up to five temporary regions are remembered for later freeing.

**State, dependencies, integration:** Maintains `prom_mem_base[]`, `prom_mem_size[]`, and `nr_prom_mem` in initdata. It integrates ARC firmware descriptors with Linux memblock and init-memory freeing.

**Risks and test signals:** More than five temporary regions logs errors and leaks them reserved. Misclassified ARC versus ARCS type values can either reserve usable RAM or free firmware-owned pages. Test descriptor permutations, mirrored IP28/IP30 RAM, `DONT_FREE_TEMP`, and weak platform overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/memory.c -->
