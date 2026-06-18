# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.c

Purpose: implements Lima GPU virtual address spaces, BO-to-VA tracking, page-table allocation, mapping, unmapping, and VM lifetime management.

Important APIs/types/functions: internal `struct lima_bo_va` binds a BO to a VM with a `drm_mm_node` and refcount. Public functions include `lima_vm_bo_add`, `lima_vm_bo_del`, `lima_vm_get_va`, `lima_vm_create`, `lima_vm_release`, `lima_vm_print`, and `lima_vm_map_bo`.

Control flow: `lima_vm_create` allocates a write-combined page directory, optionally maps the reserved DLBU page, and initializes a `drm_mm` VA allocator. `lima_vm_bo_add` finds or creates a per-BO VA record, allocates VA space, lazily allocates page-table bundles, and maps every DMA page with cacheable permissions. Delete decrements the BO-VA refcount, clears PTEs, removes the `drm_mm_node`, and frees the VA record. `lima_vm_map_bo` remaps later BO pages from a page offset, used for heap growth.

State and persistence: VM state is in-memory and refcounted with `kref`. Page directory and page-table bundles are DMA-coherent/write-combined allocations visible to hardware until VM release. BO VA records live on each BO's `va` list and are protected by `bo->lock`; `vm->lock` protects `drm_mm` and PTE mutation.

Dependencies and integration points: consumes Lima BO/GEM scatter-gather tables, device VA bounds, reserved DLBU DMA address, `drm_mm`, DMA mapping, and VM flag macros from `lima_regs.h`. Scheduler switches MMUs to these VMs before running jobs.

Risks and test signals: `lima_vm_bo_del` assumes a mapping exists; missing add/del pairing can underflow or crash. Partial mapping failure must unmap already written PTEs. Test BO submission, heap remapping, VA reuse, VM refcount release, DLBU reservation, and MMU fault diagnostics.
