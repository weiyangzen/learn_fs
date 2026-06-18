# sources/distributed-fs/ceph-client/arch/mips/mm/mmap.c

Purpose: MIPS-specific mmap address selection and virtual-address validation, including cache-color alignment for shared mappings on aliasing caches.

Important APIs/functions: `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, internal `arch_get_unmapped_area_common()`, exported `shm_align_mask`, and `__virt_addr_valid()`.

Control flow: common mmap search rejects oversized mappings, validates `MAP_FIXED` against `TASK_SIZE` and cache-color constraints, aligns requested addresses for file/shared mappings, probes VMA gaps, then uses `vm_unmapped_area()` bottom-up or top-down with fallback. `__virt_addr_valid()` checks kernel virtual range and PFN validity.

State and persistence: `shm_align_mask` is global and updated by cache initialization based on aliasing constraints.

Dependencies and integration: used by Linux mmap core and cache alias handling. Depends on `current->mm`, VMA gap helpers, randomization/topdown policy from generic mm, and MIPS address translation.

Risks and test signals: test shared mappings with pgoff color alignment, MAP_FIXED rejection, topdown fallback, huge lengths, ASLR interactions, and `virt_addr_valid` around PAGE_OFFSET/MAP_BASE boundaries.
