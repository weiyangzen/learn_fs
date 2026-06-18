# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_vm.h

Purpose: declares Lima VM layout constants, VM page structures, VM object state, and public VM management helpers.

Important APIs/types/functions: page constants (`LIMA_PAGE_SIZE`, `LIMA_PAGE_ENT_NUM`), bundle table sizing (`LIMA_VM_NUM_PT_PER_BT`, `LIMA_VM_NUM_BT`), reserved VA range for DLBU, `struct lima_vm_page`, `struct lima_vm`, and helpers `lima_vm_get/put`.

Control flow: callers create a VM, add BOs before submission, query BO VA for command streams or error dumps, optionally map additional BO pages, and release refs through `lima_vm_put`.

State and persistence: `struct lima_vm` owns a mutex, kref, `drm_mm`, Lima device pointer, one page directory, and bundle table pages. Its lifetime is explicit through `kref`.

Dependencies and integration points: depends on DRM MM and Linux kref. It is included by scheduler, submit, GEM, MMU, and device code.

Risks and test signals: VA reserve constants must align with device VA configuration; table sizing must match `lima_vm.c` index macros. Test compile coverage plus runtime submits that switch VMs and free contexts under job pressure.
