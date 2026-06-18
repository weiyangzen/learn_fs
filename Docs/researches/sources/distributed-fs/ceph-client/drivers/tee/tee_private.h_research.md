<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_private.h -->
# sources/distributed-fs/ceph-client/drivers/tee/tee_private.h

## Purpose

`tee_private.h` declares private interfaces shared by the generic TEE core, shared-memory implementation, and DMA-BUF heap support. It is not a public driver ABI; it coordinates internal shared-memory allocation, registration, file-descriptor export, and DMA-BUF backed TEE shared memory.

## Important APIs, Types, and Functions

`struct tee_shm_dmabuf_ref` extends `struct tee_shm` with DMA-BUF registration metadata: offset, `struct dma_buf *`, and optional parent `tee_shm`. Declared helpers include `tee_shm_get_fd()`, `tee_shm_alloc_user_buf()`, `tee_shm_register_user_buf()`, and `tee_heap_update_from_dma_buf()`.

## Control Flow

`tee_core.c` calls the user-buffer allocation/registration helpers from SHM ioctls and calls `tee_shm_get_fd()` before returning a file descriptor. `tee_shm.c` allocates `tee_shm_dmabuf_ref` for `TEE_IOC_SHM_REGISTER_FD` and calls `tee_heap_update_from_dma_buf()` to resolve protected DMA-BUFs. `tee_heap.c` implements that update hook when heap support is enabled.

## State and Persistence Behavior

The header defines only in-memory structures. DMA-BUF references persist while the corresponding `tee_shm` refcount is nonzero; parent `tee_shm` references can outlive the wrapper when protected-memory heaps require indirection. No persistent storage exists.

## Dependencies and Integration Points

The header depends on Linux cdev, completion, device, DMA-BUF, kref, mutex, and TEE types. It bridges `tee_core.c`, `tee_shm.c`, and `tee_heap.c`, and is intentionally local to the TEE subsystem.

## Risks and Edge Cases

Because this header exposes private helpers, adding users outside the TEE core can create layering problems. `tee_shm_dmabuf_ref` embeds `struct tee_shm`, so code must use the correct `container_of()` path based on `TEE_SHM_DMA_BUF`. Parent shared-memory lifetime must be handled carefully to avoid leaking or prematurely freeing protected-memory mappings.

## Test Signals

Build tests should catch mismatches between declarations and implementations under both enabled and disabled DMA-BUF heap configs. Runtime checks should cover SHM fd export, user SHM registration, DMA-BUF registration with and without parent SHM, and refcount cleanup for wrapper and parent objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tee_private.h -->
