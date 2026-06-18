# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/udmabuf.c

Purpose: C kselftest for `/dev/udmabuf`, covering invalid `UDMABUF_CREATE` arguments, normal udmabuf creation from sealed memfds, and migration/list creation behavior for base pages and huge pages.

Important APIs/types/functions: `memfd_create`, `F_ADD_SEALS`, `F_SEAL_SHRINK`, `ftruncate`, `mmap`, `ioctl(UDMABUF_CREATE)`, `ioctl(UDMABUF_CREATE_LIST)`, `struct udmabuf_create`, `struct udmabuf_create_list`, `create_memfd_with_seals()`, `create_udmabuf_list()`, `write_to_memfd()`, `mmap_fd()`, `compare_chunks()`, and kselftest helpers from `kselftest.h`.

Control flow: `main()` opens `/dev/udmabuf`, creates a sealed memfd, executes three negative tests for unaligned offset, unaligned size, and non-memfd input, then creates a valid udmabuf. It then exercises list creation with four chunks from a large memfd, writes after pinning, maps both memfd and udmabuf, and compares page-granular data. Later tests repeat this with 2 MiB huge pages, including a case where the udmabuf is pinned before writing the memfd.

State and persistence: State is process-local file descriptors and mappings. The test mutates memfd contents, maps DMA buffers shared, and unmaps/closes between cases. No persistent repository state is written.

Dependencies and integration points: Requires `/dev/udmabuf`, memfd sealing, hugetlb availability for huge-page cases, Linux UAPI headers, and kselftest result conventions. It directly tests dma-buf/udmabuf kernel ABI validation.

Risks and test signals: Failures indicate broken input validation, fd type checks, page alignment handling, list/chunk migration, huge-page migration, or DMA buffer data coherency. Huge-page allocation may skip/fail depending on host configuration.
