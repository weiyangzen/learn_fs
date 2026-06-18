# sources/distributed-fs/ceph-client/arch/parisc/include/asm/sparsemem.h

Purpose: defines PA-RISC sparsemem geometry.

Important APIs/types/functions: exports `MAX_PHYSMEM_BITS` and `SECTION_SIZE_BITS`.

Control flow: memory initialization divides physical memory into sparse sections using these constants.

State and persistence: section metadata persists in the sparsemem memory model. Dependencies and integration: mm initialization, memory hotplug, and page-to-section translations.

Risks and test signals: too-small limits hide RAM; wrong section size wastes memory or breaks pfn translation. Test boot with large memory maps and sparsemem debug checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
