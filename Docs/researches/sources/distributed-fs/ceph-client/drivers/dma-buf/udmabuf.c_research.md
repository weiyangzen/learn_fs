## sources/distributed-fs/ceph-client/drivers/dma-buf/udmabuf.c

### Purpose
`udmabuf.c` implements `/dev/udmabuf`, a misc device that exports sealed memfd/shmem/hugetlb-backed pages as dma-buf objects. It lets userspace build DMA-shareable buffers from one or more memfd ranges while preserving page pinning and dma-buf mapping semantics.

### Important APIs, Types, And Functions
The central type is `struct udmabuf`, holding page count, folio and offset arrays, pinned-folio tracking, a cached CPU-access sg table, and the miscdevice. Important operations are `mmap_udmabuf()`, `vmap_udmabuf()`, `get_sg_table()`, `begin_cpu_udmabuf()`, `end_cpu_udmabuf()`, `check_memfd_seals()`, `udmabuf_pin_folios()`, `udmabuf_create()`, `udmabuf_ioctl_create()`, and `udmabuf_ioctl_create_list()`. Module parameters `list_limit` and `size_limit_mb` bound list count and exported buffer size.

### Control Flow, State, And Persistence
An ioctl copies either a single create request or a list, validates page alignment and size limit, allocates arrays, then for each memfd range obtains the file, locks the inode in shared mode, validates seals, pins folios with `memfd_pin_folios()`, and expands large folios into page/offset entries. `dma_buf_export()` transfers ownership of the `udmabuf` to dma-buf release. Mapping for devices builds a fresh scatterlist and maps it with `dma_map_sgtable()`. CPU access lazily creates and caches a bidirectional sg table, then syncs it for CPU/device. `mmap` inserts PFNs fault-by-fault and prefaults the VMA range.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include dma-buf, dma-resv locking for vmap/vunmap, memfd sealing, shmem/hugetlb, folio pinning, scatterlists, DMA mapping API, misc devices, and uapi `linux/udmabuf.h`. Risks include long-term pin accounting, huge-folio subpage offsets, seal races with `memfd_add_seals()`, off-by-one range end computation, cached sg table direction reuse, PFNMAP mmap semantics, and user-controlled list size/total size. Test signals include single and multi-range creates, missing/incorrect seals, unaligned offset/size rejection, hugepage ranges, mmap faults beyond `pagecount` returning SIGBUS, device attach/detach map/unmap, CPU begin/end access, and close-time unpin count matching duplicate pinned folios.
