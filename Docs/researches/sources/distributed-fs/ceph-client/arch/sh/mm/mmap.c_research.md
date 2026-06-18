# sources/distributed-fs/ceph-client/arch/sh/mm/mmap.c

Purpose: implements SH mmap address selection and physical address validation.

Important APIs and state: exported `shm_align_mask`, `protection_map` via `DECLARE_VM_GET_PAGE_PROT`, `arch_get_unmapped_area`, `arch_get_unmapped_area_topdown`, `valid_phys_addr_range`, and `valid_mmap_phys_addr_range`.

Control flow: mmap placement honors fixed mappings, rejects shared fixed mappings that violate cache coloring, optionally color-aligns file/shared mappings by `pgoff`, searches bottom-up or top-down, and falls back from failed top-down to bottom-up. Physical address validation restricts `/dev/mem` read/write ranges to system RAM.

State and persistence: no owned state beyond `shm_align_mask`; returns selected virtual addresses.

Dependencies and integration: generic mmap, VMA gap search, cache aliasing policy, and `/dev/mem` validation.

Risks: color alignment must match cache alias geometry or shared mappings can become incoherent. `valid_mmap_phys_addr_range` currently permits all PFNs.

Test signals: mmap layout tests, MAP_FIXED shared alias rejection, SysV shared memory alignment, and `/dev/mem` access policy tests.
