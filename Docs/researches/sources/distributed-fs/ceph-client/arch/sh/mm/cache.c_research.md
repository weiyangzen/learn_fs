# sources/distributed-fs/ceph-client/arch/sh/mm/cache.c

Purpose: central SH cache abstraction layer that exports generic cacheflush APIs and dispatches to CPU-family-specific implementations.

Important APIs and state: function pointers `local_flush_*`, exported region hooks `__flush_wback_region`, `__flush_purge_region`, `__flush_invalidate_region`, page helpers `copy_to_user_page`, `copy_from_user_page`, `copy_user_highpage`, `clear_user_highpage`, `__update_cache`, `__flush_anon_page`, exported `flush_cache_all/range`, `flush_dcache_folio`, `flush_icache_range`, and `cpu_cache_init`.

Control flow: generic flush APIs run hooks on each relevant CPU through `cacheop_on_each_cpu`. User page copy paths use coherent kmap when alias-clean folios are mapped. Boot computes alias masks and selects CPU-specific hook implementations before logging cache parameters.

State and persistence: hook pointers and `boot_cpu_data.cache_info` derived fields persist for runtime. Folio `PG_dcache_clean` flags track alias cleanliness.

Dependencies and integration: integrates generic MM, highmem, folios, SMP, CPU probe data, and CPU-specific cache files.

Risks: no-op defaults are safe only for disabled/uninitialized cache paths. Alias tracking errors can expose stale data or instructions. Cross-CPU flushing is conditional and SHX3-specific.

Test signals: cache debugfs/boot logs, user page copy tests, executable mapping modifications, SMP flush tests, and DMA coherency workloads.
