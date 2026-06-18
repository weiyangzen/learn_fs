# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/vmm.c

## Purpose
This file wraps NVIF virtual memory manager objects and provides classic and raw get/put/map/unmap/sparse operations.

## Important APIs, Types, and Functions
Public APIs include `nvif_vmm_ctor`, `nvif_vmm_dtor`, `nvif_vmm_get`, `nvif_vmm_put`, `nvif_vmm_map`, `nvif_vmm_unmap`, `nvif_vmm_raw_get`, `nvif_vmm_raw_put`, `nvif_vmm_raw_map`, `nvif_vmm_raw_unmap`, and `nvif_vmm_raw_sparse`.

## Control Flow
Constructor builds a VMM object with type UNMANAGED, MANAGED, or RAW, records start/limit/page count, allocates page capability descriptors, and queries each page type. Classic get/put/map/unmap use versioned VMM methods and `struct nvif_vma`. Raw helpers issue `NVIF_VMM_V0_RAW` with explicit address, size, shift, memory handle, sparse, and argument pointers.

## State and Persistence Behavior
State persists in the VMM object, start/limit, page capability array, and allocated VMAs returned to callers. Destructor frees page metadata and destroys the object.

## Dependencies and Integration Points
It depends on NVIF MMU object construction, memory object handles, VMM class ABI, and callers in classic VMM, SVM, UVMM, and TTM paths.

## Risks
Raw map passes a kernel pointer value in the ioctl arguments, so backend expectations must match in-kernel NVIF usage. Constructor failure must tear down partially allocated objects. Page capability selection affects UVMM page-shift decisions.

## Test Signals
Signals include VMM construction for all types, page capability enumeration, get/put/map/unmap success and failure, raw sparse refs, and UVMM/SVM raw mapping flows.
