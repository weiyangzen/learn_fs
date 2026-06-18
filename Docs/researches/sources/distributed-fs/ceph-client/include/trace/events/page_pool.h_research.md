# sources/distributed-fs/ceph-client/include/trace/events/page_pool.h

Purpose: Provides tracepoints for network page-pool lifecycle and page reference handoff. It helps debug recycling, release, hold, and NUMA-node updates in high-speed RX paths.

Important APIs/types/functions: Events are `page_pool_release`, `page_pool_state_release`, `page_pool_state_hold`, and `page_pool_update_nid`. Fields include page-pool pointer, netdev info when available, inflight count, hold/release deltas, page pointer, page refcount, DMA address, page flags, and NUMA node.

Control flow: Page-pool code emits release events when pools are destroyed or drained, state events when pages are held or released from the pool, and nid updates when allocation locality changes. Trace records tie a page and DMA address back to a pool.

State and persistence: No state is owned by the header. Runtime state resides in `struct page_pool`, pages, DMA mappings, and driver RX queues; records are transient.

Dependencies and integration points: Depends on `net/page_pool/types.h`, MM flag printing, tracepoints, and network drivers using page_pool for RX recycling.

Risks and test signals: Risks include refcount imbalance, DMA unmap ordering, pool destruction with inflight pages, NUMA drift, and driver misuse of recycled pages. Test high-rate RX, XDP page recycling, pool teardown under traffic, NUMA node updates, and page leak detection with tracing.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/page_pool.h` completely for this pass (119 lines, 2831 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/page_pool.h_research.md`.
