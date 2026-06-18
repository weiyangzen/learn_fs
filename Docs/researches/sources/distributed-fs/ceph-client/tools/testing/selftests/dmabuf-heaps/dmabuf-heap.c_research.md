# sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/dmabuf-heap.c

## Purpose

`dmabuf-heap.c` tests dma-buf heap allocation, mmap/write/sync behavior, optional VGEM import, zeroed allocation reuse, ioctl structure size compatibility, and invalid argument rejection for every heap under `/dev/dma_heap`.

## Important APIs, Types, and Functions

It uses `DMA_HEAP_IOCTL_ALLOC`, `DMA_BUF_IOCTL_SYNC`, `DRM_IOCTL_VERSION`, `DRM_IOCTL_PRIME_FD_TO_HANDLE`, `DRM_IOCTL_GEM_CLOSE`, `mmap()`, `munmap()`, and kselftest result helpers. Key functions are `open_vgem()`, `dmabuf_heap_open()`, `dmabuf_heap_alloc_fdflags()`, `dmabuf_sync()`, `test_alloc_and_import()`, `test_alloc_zeroed()`, `dmabuf_heap_alloc_older()`, `dmabuf_heap_alloc_newer()`, `test_alloc_compat()`, `test_alloc_errors()`, and `numer_of_heaps()`.

## Control Flow

`main()` opens `/dev/dma_heap`, sets a plan of 11 tests per heap, and for each heap runs allocation/import/sync, two zeroing tests at 4 KiB and 1 MiB, older/newer ioctl compatibility, and invalid fd/flag cases. The import path maps a 1 MiB buffer, writes patterns under sync start/end, imports to VGEM if available, writes again, and closes handles.

## State and Persistence Behavior

It allocates dma-buf fds from heaps, maps them shared, writes data patterns, imports to DRM handles, and closes fds/handles. No files are persisted.

## Dependencies and Integration Points

It depends on dma-buf heap device nodes, exported dma-heap/dma-buf headers, optional VGEM DRM device, and kselftest. It exercises heap allocator, dma-buf synchronization, and PRIME import integration.

## Risks and Edge Cases

Some error cleanup paths return before closing all resources in failure cases. Zeroing tests allocate 32 buffers and assume freed heap memory must be zeroed on reallocation. `numer_of_heaps()` assumes `opendir()` succeeded because `main()` checked once earlier.

## Test Signals

Passes include allocation/import, sync success, buffer zeroing at two sizes, old/new ioctl compatibility, and expected errors for invalid fd/heap flags/fd flags. Skips occur when VGEM is absent.
