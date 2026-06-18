<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sparsemem.h

Purpose: Defines sparsemem geometry for RISC-V memory sections.

Important APIs/types/functions: Sets `MAX_PHYSMEM_BITS`/`SECTION_SIZE_BITS`-related constants through generic sparsemem expectations.

Control flow: No runtime flow; constants drive memory model sizing at build time.

State and persistence: Shapes persistent PFN-to-section and vmemmap layout.

Dependencies and integration points: Used by memory hotplug, vmemmap, page allocator, and sparsemem core.

Risks: Bad sizing loses addressable memory or bloats metadata.

Test signals: Sparsemem/vmemmap builds, high-memory boot, memory hotplug, and pfn_to_page/page_to_pfn tests.

Source read size: 15 lines, 331 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sparsemem.h -->
