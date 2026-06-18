<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm.c

Purpose: Implements PowerVR device virtual-memory contexts, GPUVA bookkeeping, MMU map/unmap operations, heap/static-data UAPI queries, and firmware memory-context objects.

Important APIs/types/functions: Key public functions include `pvr_vm_create_context()`, `pvr_vm_map()`, `pvr_vm_unmap_obj()`, `pvr_vm_unmap()`, `pvr_vm_unmap_all()`, `pvr_vm_context_lookup/get/put()`, `pvr_destroy_vm_contexts_for_file()`, `pvr_static_data_areas_get()`, `pvr_heap_info_get()`, `pvr_find_heap_containing()`, `pvr_vm_find_gem_object()`, `pvr_vm_get_page_table_root_addr()`, `pvr_vm_get_dma_resv()`, and `pvr_vm_get_fw_mem_context()`. Important internal types are `struct pvr_vm_context`, `struct pvr_vm_gpuva`, and `struct pvr_vm_bind_op`.

Control flow: Context creation checks virtual-address-space feature width, creates an MMU context, optionally creates a firmware memory-context BO, initializes a private GEM object for VM reservation, and initializes DRM GPUVM. Mapping validates user heaps, address/size alignment, object bounds, obtains a `drm_gpuvm_bo`, pins pages, creates an MMU op context, locks GPUVM/GEM reservations, and lets `drm_gpuvm_sm_map()` drive map/remap callbacks. Unmap mirrors that via `drm_gpuvm_sm_unmap()`. Context release destroys firmware object, unmaps all GPUVAs, destroys MMU state, and releases GPUVM.

State and persistence behavior: Persistent per-context state includes MMU page tables, DRM GPUVA mappings, firmware memory-context object, kref, mutex, and dummy GEM reservation. Static data area and heap arrays are immutable UAPI-visible descriptions, with the region-header heap hidden unless quirk 63142 is present.

Dependencies: Uses DRM GPUVM, DRM exec locking, GEM, dma-resv, PowerVR GEM/MMU/FW helpers, Rogue heap config, UAPI object copy helpers, feature/quirk detection, and Linux kref/mutex/error helpers.

Integration points: File handles store VM contexts in `pvr_file->vm_ctx_handles`. GEM mapping, job submission, firmware context setup, and dev queries all consume this API. The MMU layer performs actual page-table writes and flushes.

Risks: Address validation and heap containment protect userspace from mapping outside allowed GPU heaps; mistakes here expose device address space. GPUVA remap splitting must keep GEM references and MMU unmaps consistent. Error paths must release pinned pages, GPUVM BOs, preallocated VA nodes, and MMU op contexts without leaks.

Test signals: VM create/destroy, map/unmap/remap overlap, unmap-all cleanup, heap info query, static data query, invalid alignment/range/object-size tests, quirk 63142 heap behavior, and GPU job execution using mapped BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm.c -->
