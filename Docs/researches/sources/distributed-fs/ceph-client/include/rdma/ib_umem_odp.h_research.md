# sources/distributed-fs/ceph-client/include/rdma/ib_umem_odp.h

Purpose: defines On-Demand Paging user-memory registration objects for RDMA and config-gated APIs to allocate, map DMA pages under page fault, unmap, and release ODP memory ranges.

Important APIs and types: `struct ib_umem_odp` embeds `ib_umem`, an `mmu_interval_notifier`, owning thread-group PID, `hmm_dma_map`, `umem_mutex`, provider-private pointer, page count, implicit-ODP flag, and page shift. Inline helpers convert from `ib_umem`, return start/end addresses from the notifier interval, and compute page count. With `CONFIG_INFINIBAND_ON_DEMAND_PAGING`, APIs include `ib_umem_odp_get()`, `ib_umem_odp_alloc_implicit()`, `ib_umem_odp_alloc_child()`, `ib_umem_odp_release()`, `ib_umem_odp_map_dma_and_lock()`, and `ib_umem_odp_unmap_dma_pages()`. Without the config, get returns `-EINVAL` and release is a no-op.

Control flow: providers create explicit or implicit ODP umems, register MMU interval notification over the range, and map DMA pages on demand during faults or access. Mapping/unmapping is serialized by `umem_mutex` and coordinates with HMM DMA maps and invalidation counters. Child umems can represent subranges of an implicit root.

State and persistence: ODP state is runtime memory-registration state coupled to an mm interval and DMA mappings. Implicit ODP objects have zero length and serve as anchors. The page map can be invalidated by MMU notifications and is not persistent.

Dependencies and integration points: depends on `ib_umem.h`, verbs access flags, HMM DMA mapping, MMU interval notifier APIs, PID lifetime, mutexes, and provider page-fault handlers. It integrates RDMA memory registration with Linux MM invalidation and hardware page-fault support.

Risks and test signals: risks include notifier lifetime bugs, mapping while invalidation is active, missing mutex coverage, incorrect start/end/page_shift math, implicit ODP misuse as DMA-mappable memory, stale DMA mappings after unmap, and config-disabled behavior mismatches. Test ODP MR creation/release, page fault map/unmap, mmu_notifier invalidation during DMA, implicit and child ODP flows, access-mask enforcement, process exit while ODP exists, and config matrices with ODP disabled.
