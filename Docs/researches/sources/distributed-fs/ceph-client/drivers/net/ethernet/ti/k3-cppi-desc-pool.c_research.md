# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.c

## Purpose
This file implements a small exported API for allocating fixed-size TI K3 CPPI5 descriptors from a coherent DMA block. It wraps `dma_alloc_coherent()` and a `gen_pool` so clients can allocate/free descriptors by CPU address, translate CPU/DMA addresses, and attach per-descriptor software metadata.

## Important APIs, types, and functions
- `struct k3_cppi_desc_pool` stores the owning device, DMA base, CPU base, rounded descriptor size, memory size, descriptor count, gen_pool, and sideband `desc_infos`.
- `k3_cppi_desc_pool_create_name()` allocates the pool object, rounds descriptor size to a power of two, creates a named gen_pool, allocates sideband metadata array, allocates coherent DMA memory, and adds it to the gen_pool.
- `k3_cppi_desc_pool_destroy()` warns if descriptors are still allocated, frees coherent memory, metadata, gen_pool, and the pool.
- `k3_cppi_desc_pool_virt2dma()` and `_dma2virt()` translate by base-offset arithmetic.
- `k3_cppi_desc_pool_alloc()` and `_free()` allocate and free one descriptor-sized block.
- `k3_cppi_desc_pool_avail()`, `_desc_size()`, `_cpuaddr()`, `_desc_info_set()`, and `_desc_info()` expose pool metadata and sideband storage.

## Control flow
Creation is fail-unwind structured: allocate pool, duplicate name, create gen_pool, allocate metadata array, allocate coherent memory, add memory to gen_pool, return pool. Failure paths free in reverse order. Allocation/free are direct gen_pool calls. Destroy checks for leaked descriptors by comparing gen_pool total and available bytes before freeing resources.

## State and persistence behavior
State is entirely in kernel memory and coherent DMA memory. Descriptors persist until freed or until the pool is destroyed. The `desc_infos` array persists sideband pointers per descriptor index but bounds are not checked by this API.

## Dependencies and integration points
The file exports GPL symbols for other kernel drivers. It depends on Linux device, DMA mapping, genalloc, err, and kernel helpers. The paired header exposes the opaque pool type and API. It is meant for K3 Ethernet/UDMA-style clients that need CPPI5 descriptors.

## Risks and edge cases
- Descriptor size is rounded up to a power of two; clients must use the returned size when computing indices.
- Address translation assumes the passed address/DMA belongs to the pool and performs no range checking.
- `desc_info_set()` and `desc_info()` do not validate `desc_idx`.
- Destroy warns but still frees if descriptors are outstanding.

## Test signals
Create/destroy with normal and named pools, allocation until exhaustion, free/reallocate cycles, descriptor size rounding, virt-to-DMA and DMA-to-virt round trips, outstanding allocation warning on destroy, and metadata set/get for valid indices.
