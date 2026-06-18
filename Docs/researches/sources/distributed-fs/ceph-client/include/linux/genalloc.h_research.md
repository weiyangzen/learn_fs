<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genalloc.h -->
# sources/distributed-fs/ceph-client/include/linux/genalloc.h

Purpose: Declares the generic special-purpose memory pool allocator for memory outside normal `kmalloc` management, such as device SRAM, uncached memory, and reserved regions.

Important APIs/types/functions: `gen_pool` owns chunk list, minimum allocation order, allocation algorithm, private algorithm data, and name. `gen_pool_chunk` tracks physical/virtual bounds, owner, availability counter, and allocation bitmap. Allocation callbacks use `genpool_algo_t`; data structs support aligned and fixed allocations. APIs include pool create/destroy, add chunks, virt-to-phys, alloc/free with optional algorithms and owners, DMA alloc/zalloc variants, chunk iteration, availability/size queries, algorithm setters, first/best/fixed-fit algorithms, devm creation, lookup, address containment, and optional OF lookup.

Control flow: A client creates a pool, adds one or more chunks, optionally sets an allocation algorithm, then allocates/free regions. Allocation scans chunk bitmaps with an algorithm and updates bits atomically so prepopulated pools can be used in NMI-like contexts on architectures with NMI-safe cmpxchg.

State and persistence behavior: Pool/chunk state is runtime-only. Chunks persist until removed by pool destruction; owner pointers provide caller metadata on allocation/free.

Dependencies and integration points: Depends on spinlock types, atomics, device and OF declarations. Integrates with platform/device memory providers and managed device lifetime.

Risks: NMI safety only applies when enough memory is already in the pool and architecture cmpxchg is NMI-safe. Extreme contention can livelock. Physical address `-1` sentinel in `gen_pool_add_virt()` users must be interpreted carefully.

Test signals: Allocation/free fragmentation tests, alignment/fixed/best-fit algorithms, owner round-trip, DMA variants, concurrent stress, NMI-safe architecture build checks, OF pool lookup, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genalloc.h -->
