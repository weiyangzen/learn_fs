# sources/distributed-fs/ceph-client/drivers/tee/amdtee/shm_pool.c

## Purpose
`shm_pool.c` implements AMD-TEE’s page-backed `tee_shm_pool`. It allocates zeroed kernel pages, translates their physical address for the PSP, maps them into AMD TEE firmware, and unmaps/frees them when the TEE core releases shared memory.

## Important APIs, Types, And Functions
`pool_op_alloc()` computes an allocation order from the requested size, allocates zeroed pages with `__get_free_pages()`, fills `tee_shm.kaddr`, `paddr`, and page-rounded `size`, then calls `amdtee_map_shmem()`. If mapping fails, it frees the pages and clears `kaddr`. `pool_op_free()` calls `amdtee_unmap_shmem()` and frees the pages using the stored size. `pool_op_destroy_pool()` frees the pool object. `amdtee_config_shm()` allocates a `tee_shm_pool` and assigns the AMD pool ops.

## Control Flow And State
The pool itself has no independent allocation list. State is stored in each `tee_shm` plus the per-context mapping list maintained by `core.c`. Allocation order determines the final shared-memory size, which may be larger than requested. The firmware buffer id is acquired as part of allocation and retired before physical pages are returned.

## Dependencies And Integration Points
This file depends on Linux TEE core pool callbacks, page allocator APIs, AMD PSP physical address translation (`__psp_pa()`), and `amdtee_map_shmem()`/`amdtee_unmap_shmem()` from `core.c` and `call.c`. It is consumed by `amdtee_driver_init()`.

## Risks
The `align` argument is intentionally ignored because page allocation is assumed sufficient; future callers requiring larger alignment would not get it. `get_order(size)` rounds up, so callers must respect `shm->size` rather than the requested size. Unmap failure is not represented because `amdtee_unmap_shmem()` returns void.

## Test Signals
Allocate sizes below, equal to, and above one page and verify `shm->size` and PSP map size. Inject map failure and ensure pages are freed. Confirm unmap is called exactly once on free and that repeated allocations do not leave stale `shm_list` entries.
