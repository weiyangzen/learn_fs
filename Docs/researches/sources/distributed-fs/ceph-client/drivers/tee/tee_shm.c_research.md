<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm.c -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_shm.c

## Purpose

`tee_shm.c` implements generic TEE shared-memory allocation, registration, lookup, file-descriptor export, mmap, refcounting, and dynamic helper routines. It supports pool-backed allocations, registered user/kernel buffers, DMA-BUF heap backed protected memory, and private driver buffers.

## Important APIs, Types, and Functions

Allocation APIs include `tee_shm_alloc_user_buf()`, `tee_shm_alloc_kernel_buf()`, `tee_shm_alloc_priv_buf()`, and optional `tee_shm_alloc_dma_mem()`. Registration APIs include `tee_shm_register_user_buf()`, `tee_shm_register_kernel_buf()`, and `tee_shm_register_fd()`. Dynamic pool helpers are `tee_dyn_shm_alloc_helper()` and `tee_dyn_shm_free_helper()`. Access/lifetime APIs are `tee_shm_get_fd()`, `tee_shm_free()`, `tee_shm_get_va()`, `tee_shm_get_pa()`, `tee_shm_get_from_id()`, and `tee_shm_put()`.

Internal helpers include `shm_alloc_helper()`, `register_shm_helper()`, `release_registered_pages()`, and `tee_shm_release()`. `struct tee_shm_dma_mem` wraps DMA pages when DMA heap support is enabled.

## Control Flow

User allocation reserves an IDR slot, allocates from the device pool, then replaces the IDR placeholder with the `tee_shm` and returns an fd. User registration pins/extracts pages from a user iterator, calls driver `.shm_register()`, installs the SHM in the IDR, and returns an fd. Private/kernel allocations are not normally IDR-visible. Registering an fd gets a DMA-BUF, verifies it through `tee_heap_update_from_dma_buf()`, installs a wrapper SHM in the IDR, and returns it.

All refs converge through `tee_shm_put()`: the last ref removes the IDR entry while holding the device mutex so future lookups cannot increment from zero, then `tee_shm_release()` frees according to flags: DMA pages, DMA-BUF wrapper, pool allocation, or dynamic registered memory with unregister and page unpin.

## State and Persistence Behavior

Shared-memory state is runtime-only. Each `tee_shm` tracks refcount, flags, ID, context, virtual/physical address, size, offset, pages, page count, and secure-world ID if assigned by a driver. User-visible allocated/registered SHM persists until all file descriptors, parameter references, and driver references are released.

## Dependencies and Integration Points

This file depends on generic TEE device/context state from `tee_core.c`, per-driver shared-memory pool ops from `tee_shm_pool.c` and qcomtee/tstee pools, optional DMA-BUF heap logic from `tee_heap.c`, Linux page pinning/extraction, anon inode fd creation, and DMA APIs. Concrete drivers use `tee_shm_alloc_priv_buf()` for transport buffers and `.shm_register()`/`.shm_unregister()` callbacks for secure-world registration.

## Risks and Edge Cases

Bounds checks reject offsets `>= shm->size`, so zero-size shared-memory objects would be unusable for VA/PA access. `tee_shm_get_va()` requires `kaddr`; registered user buffers and DMA-BUF wrappers may not have one. `register_shm_helper()` page-count handling after partial extraction is delicate and must unpin exactly what was pinned. `tee_shm_fop_mmap()` refuses user-mapped and DMA-BUF SHM but remaps physical pages for pool-backed memory; cacheability and memory attributes depend on the original allocation. `tee_dyn_shm_free_helper()` calls unregister but ignores its return. IDR removal before release prevents refcount resurrection and is critical to preserve.

## Test Signals

Tests should cover SHM alloc/register/free by fd close and explicit put, lookup by valid/invalid ID and wrong context, memref offset/size boundary checks through `tee_core.c`, mmap allowed and denied cases, dynamic helper allocation/register failure unwind, user page pin/unpin accounting, DMA-BUF registration paths, private buffer VA/PA retrieval, concurrent lookup and final put, and unregister failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_shm.c -->
