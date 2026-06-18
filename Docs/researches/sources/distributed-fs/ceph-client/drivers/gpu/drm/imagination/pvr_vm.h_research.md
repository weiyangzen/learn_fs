<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm.h

Purpose: Declares the PowerVR VM context API and makes Rogue MMU definitions available to VM/MMU users.

Important APIs/types/functions: Forward-declares `struct pvr_vm_context` and public APIs for address validation, context lifecycle, map/unmap, page-table root retrieval, shared reservation retrieval, static-data/heap queries, heap lookup, mapped GEM lookup, firmware memory-context lookup, and per-file context destruction.

Control flow: No implementation flow; documents the externally visible VM operations.

State and persistence behavior: The API exposes opaque context lifetime through get/put and returns shared kernel objects such as dma-resv, GEM object references, and firmware object pointers with caller-managed lifetime.

Dependencies: Includes `pvr_rogue_mmu_defs.h`, UAPI `pvr_drm.h`, and Linux types. Forward declarations keep include pressure low.

Integration points: Used by GEM, firmware, ioctl, job, and context-management code across the PowerVR driver.

Risks: Callers must respect object reference semantics, especially for `pvr_vm_find_gem_object()` and context get/put. Address validation must be used before direct MMU operations.

Test signals: Build coverage of all API users and runtime coverage through VM ioctls, GEM mappings, and firmware memory-context creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm.h -->
