<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sparsemem.h

Purpose: provides LoongArch sparsemem/vmemmap sizing and section layout constants.
Important APIs and types: defines `SECTION_SIZE_BITS`, `MAX_PHYSMEM_BITS`, and related memory-model constants with 32-bit/64-bit and NUMA considerations.
Control flow: no runtime flow; generic memory-model code uses these constants to size sections and vmemmap.
State and persistence: constants shape physical memory section indexing and vmemmap placement for the life of the kernel.
Dependencies and integration: consumed by `pgtable.h`, memblock, sparsemem, NUMA, memory hotplug, and vmemmap initialization.
Risks and test signals: too-small limits lose memory; too-large section geometry wastes metadata or breaks PFN math. Signals include high-memory boot, NUMA boot, memory hotplug, and sparsemem build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/sparsemem.h -->
