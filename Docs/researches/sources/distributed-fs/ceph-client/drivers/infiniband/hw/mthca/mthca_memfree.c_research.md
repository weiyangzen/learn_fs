# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_memfree.c

Purpose: implements "mem-free" Arbel/Sinai context-memory management for mthca, including ICM allocation/mapping, lazy ICM tables, user/kernel doorbell record mapping, and kernel doorbell page allocation.

Important APIs/functions: exports `mthca_alloc_icm`, `mthca_free_icm`, `mthca_alloc_icm_table`, `mthca_free_icm_table`, `mthca_table_get/put/find/get_range/put_range`, `mthca_map_user_db`, `mthca_unmap_user_db`, `mthca_init_user_db_tab`, `mthca_cleanup_user_db_tab`, `mthca_alloc_db`, `mthca_free_db`, `mthca_init_db_tab`, and `mthca_cleanup_db_tab`.

Control flow: ICM allocation builds chunk lists from the largest available orders up to 256 KiB, maps noncoherent chunks with `dma_map_sg`, and zeroes pages because firmware expects cleared context memory. Table get lazily allocates a 256 KiB ICM chunk, maps it with `mthca_MAP_ICM`, increments a refcount, and table put unmaps/free when the refcount reaches zero. User doorbell mapping pins a user page, DMA maps it, maps one ICM page at the UARC virtual address, and defers unmapping until context cleanup. Kernel doorbells allocate coherent pages from two allocation groups so SQ/CQ-arm and RQ/SRQ/CQ-set-CI records grow from opposite ends.

State and persistence: all state is runtime kernel/HCA state: `mthca_icm_table.icm[]` refcounts, pinned user DB pages, coherent kernel DB pages, and firmware ICM mappings. No disk persistence exists.

Dependencies and integration: used by QP, CQ, SRQ, MR, EQ, and UAR paths on mem-free devices; depends on DMA mapping APIs, user page pinning, `mthca_MAP_ICM`, `mthca_UNMAP_ICM`, `mthca_MAP_ICM_page`, and `dev->uar_table`.

Risks: refcount mismatches can leak or prematurely unmap firmware context pages; long-term user page pins must be released on all context paths; `mthca_unmap_user_db` intentionally delays actual unmapping, so cleanup is critical. Doorbell group boundary logic is subtle and can leak pages until table cleanup.

Test signals: probe/unload mem-free HCAs, create/destroy user and kernel QPs/CQs/SRQs, stress doorbell allocation exhaustion, exercise failed `mthca_MAP_ICM*` paths, and run with DMA/debug page-pin diagnostics.
