<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xlate_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xlate_mmu.c

## Purpose
`xlate_mmu.c` provides MMU helpers for Xen guests with auto-translated physmaps. It maps foreign GFNs into userspace VMAs, unmaps them, maps ballooned pages for grant tables, and remaps VMA ranges from preallocated pages.

## Important APIs, types, and functions
Exports are `xen_xlate_remap_gfn_array`, `xen_xlate_unmap_gfn_range`, `xen_xlate_map_ballooned_pages`, and `xen_remap_vma_range`. Internal helpers include `xen_for_each_gfn`, `remap_pte_fn`, `setup_hparams`, `unmap_gfn`, `setup_balloon_gfn`, and `remap_pfn_fn`.

## Control flow
Remap validates a PFNMAP/IO VMA, batches up to `XEN_PFN_PER_PAGE` foreign GFNs, calls `XENMEM_add_to_physmap_range`, records per-GFN errors, counts successful mappings, and installs special PTEs when the hypercall itself succeeds. Unmap walks GFNs and calls `XENMEM_remove_from_physmap`. Balloon mapping allocates unpopulated pages, collects GFNs, and vmaps them.

## State and persistence
State is transient: page arrays, per-batch hypercall arrays, mapped counts, and VMA page tables. Mappings persist only as VMA/PTE state until unmapped or process teardown.

## Dependencies and integration points
The file depends on Xen memory hypercalls, balloon allocation, page/PFN/GFN translation, `apply_to_page_range`, and `vmap`. It is used by privcmd/grant-related paths on ARM and other auto-translated guests.

## Risks and test signals
Risks include partial hypercall success, mismatch between Xen PFN and Linux page size, installing PTEs despite per-entry errors, invalid VMA flags, and cleanup after vmap or balloon allocation failures. Test signals include mixed-success GFN arrays, non-page-aligned ranges, unmap idempotence, balloon allocation failure, and privcmd mmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xlate_mmu.c -->
