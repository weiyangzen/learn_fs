# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.c

## Purpose
`qcom_tzmem.c` provides a TrustZone-safe memory allocator for Qualcomm firmware drivers. It creates genalloc-backed pools over coherent DMA memory and optionally wraps each area in a Qualcomm SHM Bridge so TrustZone accepts the buffers.

## Important APIs, Types, And Functions
- Internal types: `struct qcom_tzmem_area`, `struct qcom_tzmem_pool`, and `struct qcom_tzmem_chunk`.
- Global state: `qcom_tzmem_dev`, radix tree `qcom_tzmem_chunks`, and `qcom_tzmem_chunks_lock`.
- Mode hooks: `qcom_tzmem_init()`, `qcom_tzmem_init_area()`, and `qcom_tzmem_cleanup_area()` differ between generic and SHM Bridge configurations.
- SHM Bridge exports: `qcom_tzmem_shm_bridge_create()` and `qcom_tzmem_shm_bridge_delete()`.
- Pool APIs: `qcom_tzmem_pool_new()`, `qcom_tzmem_pool_free()`, and `devm_qcom_tzmem_pool_new()`.
- Allocation APIs: `qcom_tzmem_alloc()`, `qcom_tzmem_free()`, and `qcom_tzmem_to_phys()`.
- Enable API: `qcom_tzmem_enable()`.

## Control Flow
`qcom_tzmem_enable()` records the SCM device and initializes mode-specific behavior. In SHM Bridge mode it skips blacklisted SoCs, calls `qcom_scm_shm_bridge_enable()`, and records whether bridge creation should be active. Pools are created with static, multiplier, or on-demand growth policies and optionally prefilled with coherent DMA areas. Each area is added to a `gen_pool`, tracked in the pool's area list, and optionally assigned a SHM Bridge handle.

Allocations round up to page size, allocate a chunk record, try `gen_pool_alloc()`, grow the pool if allowed, and insert a chunk record into a global radix tree keyed by virtual address. Free looks up the chunk, returns memory to the owning pool, and frees the record. Physical address translation scans owned chunks and delegates to `gen_pool_virt_to_phys()`.

## State And Persistence
The allocator maintains boot/module-lifetime global device state, per-pool area lists and gen_pools, per-allocation chunk metadata, and optional SHM Bridge handles. Memory is coherent DMA memory and is not persisted, but SHM Bridge creation/deletion changes secure firmware's view of shared memory.

## Dependencies And Integration Points
It depends on DMA coherent allocation, generic allocator, radix tree, spinlocks, device tree machine matching, and SCM SHM Bridge calls. SCM and QSEECOM/UEFI clients use it for buffers passed to TrustZone.

## Risks
`qcom_tzmem_enable()` is singleton and returns `-EBUSY` on repeated enable. Freeing a pool with outstanding chunks triggers a warning and risks leaks or use-after-free. `qcom_tzmem_to_phys()` scans all chunks and returns zero on failure; callers must treat zero as invalid. SHM Bridge mode is blacklisted for known-broken machines, but unsupported firmware or non-TZMem buffers can still fail secure calls.

## Test Signals
Pool creation should succeed in static, multiplier, and on-demand policies. Allocation/free should leave no non-empty pool warnings. SHM Bridge mode should log unsupported on blacklisted/unsupported platforms and create/delete handles on supported platforms. SCM extended-argument, QSEECOM, and EFI variable operations validate allocator integration.
