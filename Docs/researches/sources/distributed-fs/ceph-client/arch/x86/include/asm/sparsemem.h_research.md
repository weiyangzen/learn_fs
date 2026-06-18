<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sparsemem.h

Purpose: defines x86 sparsemem section sizing, physical address limits, and memory-model constants. Important macros include section size bits and maximum physical memory bits for 32/64-bit and configuration-specific variants.

Control flow: memory initialization uses these constants to size sparsemem sections and validate PFN ranges. State is memory model metadata owned by generic mm. Dependencies include page size, physical address width, NUMA, memory hotplug, and Kconfig memory model.

Risks: wrong limits can hide RAM, overrun mem_section arrays, or break hotplug. Test signals include large-memory boot, NUMA, memory hotplug, sparsemem/vmemmap initialization, and 32-bit PAE/non-PAE builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sparsemem.h -->
