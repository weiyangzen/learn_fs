# sources/distributed-fs/ceph-client/drivers/tee/optee/protmem.c

## Purpose
`protmem.c` implements dynamic OP-TEE protected-memory pools used for secure data path DMA heaps. It queries secure-world protected-memory requirements, allocates physical memory, lends it to OP-TEE, suballocates it through a gen_pool, and reclaims it when no allocations remain.

## Important APIs, Types, And Functions
`struct optee_protmem_dyn_pool` wraps `tee_protmem_pool` with an OP-TEE pointer, backing `tee_shm`, gen_pool, page count, memory attributes, use case, refcount, and mutex. `init_dyn_protmem()` allocates DMA memory via `tee_shm_alloc_dma_mem()`, lends it with `optee->ops->lend_protmem()`, marks it dynamic, creates a gen_pool, and adds the protected physical range. `get_dyn_protmem()` lazily initializes or refcounts the pool; `put_dyn_protmem()` releases it when the last allocation returns.

Pool ops allocate by page-aligning requested size, taking a physical subrange from gen_pool, creating a one-entry SG table, and returning an offset relative to the backing protected SHM. Free returns SG entries to the gen_pool and drops the dynamic pool reference. `protmem_pool_op_dyn_update_shm()` reports the parent protected SHM to the TEE core.

`get_protmem_config()` sends `OPTEE_MSG_CMD_GET_PROTMEM_CONFIG` to secure world, optionally using a private SHM output buffer for memory attributes. `optee_protmem_alloc_dyn_pool()` queries size/attributes, sets DMA mask from returned PA width, initializes the pool object, and returns the generic `tee_protmem_pool`.

## Control Flow And State
Dynamic protected memory is lazily lent on the first allocation and reclaimed after the last allocation. `refcount` guards active users; `mutex` serializes init and teardown. The gen_pool tracks suballocations inside the protected physical range. Memory attributes and use case persist for the pool lifetime.

## Dependencies And Integration Points
This file depends on Linux genalloc, TEE protected-memory pool APIs, TEE DMA memory allocation, common OP-TEE message calls from `call.c`, and backend-specific `lend_protmem()`/`reclaim_protmem()` ops from SMC or FF-A. It is called by backend protected-memory initialization.

## Risks
`protmem_pool_op_dyn_alloc()` aligns allocation size to pages but calls `gen_pool_free()` with `size` instead of the aligned `sz` in the SG allocation failure path, which can leave part of the allocation unreleased. The TODO notes memory should be unmapped before lending because it becomes inaccessible; relying on EL2 to handle this is platform-dependent. `get_protmem_config()` computes `*ma_count = params[1].u.memref.size / sizeof(*mem_attrs)` even when `mem_attrs` is NULL; this relies on `sizeof(*mem_attrs)` being valid on the pointed-to type and is syntactically okay but easy to misread.

## Test Signals
Query configs with no attributes, short-buffer attributes, and invalid returns. Allocate/free multiple protected buffers and ensure the dynamic pool initializes once and reclaims on last free. Fault-inject gen_pool add/alloc, lend, and reclaim failures. Use memory-debugging to catch the aligned-size free mismatch.
