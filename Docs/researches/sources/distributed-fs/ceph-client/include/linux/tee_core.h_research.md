<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_core.h -->
# sources/distributed-fs/ceph-client/include/linux/tee_core.h

## Purpose
declares the internal API that the generic TEE core provides to concrete TEE drivers, including device allocation/registration, driver operation vectors, shared-memory pools, protected-memory pools, DMA-heap registration, and context/shared-memory reference helpers.

## Important APIs, Types, and Functions
The file is 439 lines and exports these visible symbol families: types/enums `tee_dma_heap_id`, `tee_device`, `tee_driver_ops`, `tee_desc`, `tee_protmem_pool`, `tee_protmem_pool_ops`, `tee_shm_pool`, `tee_shm_pool_ops`, `tee_shm`, `tee_context`; macros/constants `TEE_SHM_DYNAMIC`, `TEE_SHM_USER_MAPPED`, `TEE_SHM_POOL`, `TEE_SHM_PRIV`, `TEE_SHM_DMA_BUF`, `TEE_SHM_DMA_MEM`, `TEE_DEVICE_FLAG_REGISTERED`, `TEE_MAX_DEV_NAME_LEN`, `TEE_REVISION_STR_SIZE`, `TEE_DESC_PRIVILEGED`; function-like macros none; inline helpers `tee_shm_pool_free`, `tee_shm_is_dynamic`, `tee_shm_get_id`, `tee_param_is_memref`; external prototypes `tee_device_alloc`, `tee_device_register`, `tee_device_unregister`, `tee_device_register_dma_heap`, `tee_device_put_all_dma_heaps`, `tee_device_get`, `tee_device_put`, `tee_device_set_dev_groups`, `tee_session_calc_client_uuid`, `tee_shm_pool_alloc_res_mem`, `tee_protmem_static_pool_alloc`, `tee_get_drvdata`, `tee_shm_alloc_priv_buf`, `tee_dyn_shm_alloc_helper`, and 7 more.

## Control Flow
A TEE driver fills `tee_desc` and `tee_driver_ops`, allocates a `tee_device`, optionally attaches sysfs groups and shared-memory pools, registers it, and serves open/session/invoke/cancel/supplicant and shared-memory callbacks through the core. Shared memory is allocated from pools, registered dynamically, referenced by ID, and released through refcount helpers.

## State and Persistence Behavior
`tee_device` owns the device/cdev, user count, completion used during unregister, IDR of user-visible shared memory, mutex, and pool pointer. `tee_shm` objects have flags, IDs, physical/kernel/user backing, secure-world IDs, and references. Protected-memory pools encapsulate implementation-owned state through ops.

## Dependencies and Integration Points
It depends on cdev/device/dma-buf/idr/kref/list/scatterlist/TEE UAPI/UUID APIs and integrates with OP-TEE or other TEE drivers, tee-supplicant, DMA heaps, reserved memory, and client-driver contexts. Direct includes are `linux/cdev.h`, `linux/device.h`, `linux/dma-buf.h`, `linux/idr.h`, `linux/kref.h`, `linux/list.h`, `linux/scatterlist.h`, `linux/tee.h`, `linux/tee_drv.h`, `linux/types.h`, `linux/uuid.h`.

## Risks and Edge Cases
Device unregister must block new users while existing contexts and shared memory drain. Dynamic shared-memory registration requires page lifetime, DMA visibility, secure-world unregister, and IDR cleanup to match. Protected-memory update hooks can expose wrong parent buffers or physical addresses.

## Test Signals
Run TEE core and OP-TEE tests for device register/unregister, concurrent opens, session open/invoke/cancel, supplicant absence, shared-memory alloc/register/free by ID, DMA-heap protected memory, and error unwinding under refcount debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tee_core.h -->
