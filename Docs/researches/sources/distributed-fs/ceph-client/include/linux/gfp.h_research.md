<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp.h -->
# sources/distributed-fs/ceph-client/include/linux/gfp.h

Purpose: Declares core page/folio allocation helpers and GFP flag interpretation utilities for the page allocator.

Important APIs/types/functions: Helpers include `default_gfp()`, `gfp_migratetype()`, `gfpflags_allow_blocking()`, `gfpflags_allow_spinning()`, `gfp_zone()`, `gfp_zonelist()`, `gfp_nested_mask()`, `node_zonelist()`, node warning helpers, `gfp_has_flags()`, `gfp_has_io_fs()`, and `gfp_compaction_allowed()`. Allocation APIs wrap no-profile functions through `alloc_hooks()`: `__alloc_pages`, `__folio_alloc`, bulk allocators, node allocators, NUMA/mempolicy folio allocators, `alloc_pages`, `folio_alloc`, `alloc_page`, `alloc_pages_nolock`, `__get_free_pages`, `get_zeroed_page`, exact-page allocators, and contiguous allocation APIs under `CONFIG_CONTIG_ALLOC`. Freeing APIs include `__free_pages`, `free_pages_nolock`, `free_pages`, `__free_page`, and `free_page`.

Control flow: Callers provide GFP flags; helpers derive migratetype, zone, zonelist fallback behavior, reclaim/spinning permissions, and nested-allocation masks. Allocation wrappers choose NUMA node/default node, call underlying allocator implementations, and pass through allocation hooks for profiling/tagging.

State and persistence behavior: Runtime state comes from NUMA node data, zonelists, per-CPU pages, `gfp_allowed_mask`, page grouping flags, and architecture allocation/free hooks. This header declares behavior but does not store pages itself.

Dependencies and integration points: Depends on `gfp_types.h`, memory zones, topology, allocation tags, cleanup helpers, scheduler, mempolicy, and VMA declarations. It is central to MM, filesystems, drivers, and any kernel subsystem allocating pages.

Risks: Invalid zone flag combinations trigger `VM_BUG_ON`; misuse of `__GFP_NOFAIL`, reclaim flags, or nested masks can deadlock or stall. `GFP_NOFS/NOIO` contexts are especially important for filesystem recursion. Node-specific allocation from offline nodes warns.

Test signals: MM page allocator tests, NUMA fallback tests, invalid GFP flag debug builds, allocation failure injection, nofs/noio lockdep scenarios, contiguous allocation tests, allocation hook/profiling builds, and hibernation `gfp_allowed_mask` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gfp.h -->
