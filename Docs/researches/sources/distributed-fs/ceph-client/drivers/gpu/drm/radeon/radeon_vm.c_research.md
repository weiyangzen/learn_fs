<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vm.c

## Purpose
`radeon_vm.c` implements Radeon GPU virtual memory for Cayman and newer hardware. It manages VM manager enablement, VMID allocation/reuse, page-directory and page-table BOs, BO virtual-address mappings, PTE/PDE updates through the DMA ring, invalidation/freed lists, and VM teardown.

## Important APIs, types, and functions
Manager functions are `radeon_vm_manager_init` and `radeon_vm_manager_fini`. Per-VM lifecycle uses `radeon_vm_init` and `radeon_vm_fini`. Submission integration uses `radeon_vm_get_bos`, `radeon_vm_grab_id`, `radeon_vm_flush`, and `radeon_vm_fence`. BO mapping uses `radeon_vm_bo_find`, `radeon_vm_bo_add`, `radeon_vm_bo_set_addr`, `radeon_vm_bo_update`, `radeon_vm_bo_rmv`, `radeon_vm_bo_invalidate`, `radeon_vm_clear_freed`, and `radeon_vm_clear_invalids`. Internal update helpers include `radeon_vm_set_pages`, `radeon_vm_clear_bo`, `radeon_vm_update_page_directory`, `radeon_vm_frag_ptes`, `radeon_vm_update_ptes`, and `radeon_vm_fence_pts`.

## Control flow
VM init allocates a page-table pointer array and a cleared VRAM page directory. Mapping a BO validates address bounds and interval-tree overlap, clones old mappings to the freed list when remapping, inserts new ranges into the VM interval tree, grows `max_pde_used`, and lazily allocates/clears required page-table BOs. Page-directory updates coalesce contiguous PDE writes into one DMA IB. BO updates choose valid/system/snooped/writeable flags from TTM placement and userptr read-only state, sync against page-table reservations, emit PTE writes/copies/sets, pad and schedule the DMA IB, mark the fence as a VM update, and fence touched page tables. VMID allocation skips VMID 0, prefers free IDs, otherwise chooses the earliest active fence with preference for the same ring.

## State, dependencies, and integration points
Persistent state is split among `rdev->vm_manager`, per-VM page directory/tables, per-ring VM IDs, interval trees, invalidated/freed/cleared status lists, fences, and BO `va` lists. Dependencies include Radeon BO/TTM, DMA reservations, fences, IB scheduling, GART, ASIC VM callbacks, interval trees, mutexes/spinlocks, and tracepoints. Command submission uses this file to validate VM BOs and flush page directories before executing IBs.

## Risks and test signals
Risks include address-overlap bugs, stale PTEs after unmap/invalidate, missing sync to VMID last use when clearing invalid mappings, page-table BO allocation races, DMA IB size underestimation, and fragment PTE flags on non-contiguous system pages. Signals include VM tracepoints, GPU page-fault absence, command submission under remap/unmap stress, userptr readonly mapping behavior, VMID reuse ordering, and clean VM teardown with no active BO warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_vm.c -->
