<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm_pool.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_shm_pool.c

## Purpose

`tee_shm_pool.c` implements a generic reserved-memory TEE shared-memory pool backed by `gen_pool`. It is used by TEE drivers that have a statically reserved shared-memory region rather than dynamic per-buffer registration.

## Important APIs, Types, and Functions

`pool_op_gen_alloc()` allocates aligned zeroed chunks from a `gen_pool`, fills `tee_shm->kaddr`, `paddr`, `size`, and clears `TEE_SHM_DYNAMIC`. `pool_op_gen_free()` frees a chunk and clears `kaddr`. `pool_op_gen_destroy_pool()` destroys the gen_pool and frees the wrapper. `tee_shm_pool_alloc_res_mem()` validates page-aligned virtual address, physical address, and size, creates a gen_pool, adds the virtual/physical range, and returns a `tee_shm_pool`.

## Control Flow

A driver calls `tee_shm_pool_alloc_res_mem()` during probe with a pre-mapped reserved memory range. Generic TEE allocation paths call the pool's `.alloc` op, which rounds allocation size up to the selected alignment, gets a chunk from the gen_pool, zeroes it, and returns physical/virtual fields to the `tee_shm`. Free returns the exact allocated size to the pool. Destroy tears down the gen_pool when the driver is removed.

## State and Persistence Behavior

State is in the gen_pool allocation bitmap and the pool's private_data pointer. Shared-memory chunks persist until the corresponding `tee_shm` is released. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on Linux genalloc, device/DMA headers, and generic TEE pool interfaces. It is exported for drivers using reserved shared-memory carveouts; qcomtee and tstee in this work item use dynamic pools instead.

## Risks and Edge Cases

All inputs must be page aligned; non-page-aligned reserved ranges are rejected. Allocation alignment is the max of requested alignment and the gen_pool minimum order, and the size is rounded to that alignment, so callers may receive larger SHM than requested. Clearing `TEE_SHM_DYNAMIC` means no per-buffer secure registration/unregistration will occur; this is correct only when the reserved pool is already shared or globally known to secure world. Destroying a pool with outstanding allocations would be unsafe and must be prevented by device teardown ordering.

## Test Signals

Tests should cover page-alignment rejection, gen_pool create/add failure, allocation/free with different alignments, zeroing, physical address translation, pool exhaustion, destroy after all allocations are freed, and integration with `tee_shm_alloc_user_buf()` and mmap for reserved memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm_pool.c -->
