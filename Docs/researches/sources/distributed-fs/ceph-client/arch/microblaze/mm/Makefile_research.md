# sources/distributed-fs/ceph-client/arch/microblaze/mm/Makefile

Purpose: selects the MicroBlaze MMU/memory-management objects.

Important build rules and state: `obj-y := consistent.o init.o pgtable.o mmu_context.o fault.o` unconditionally links coherent DMA prep, boot memory/MMU init, page-table/ioremap helpers, context allocator, and page-fault handling.

Control flow: build-time only.

State and persistence: determines which memory-management implementation is present in every MicroBlaze kernel build represented by this tree.

Dependencies and integration: linked with low-level assembly TLB handlers and setup/head code.

Risks and test signals: no config gating means these files must build across MMU-related options present in this architecture. Test all MicroBlaze defconfigs and highmem/CMA/initrd variants.
