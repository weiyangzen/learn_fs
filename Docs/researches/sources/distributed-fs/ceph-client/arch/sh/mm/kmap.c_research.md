# sources/distributed-fs/ceph-client/arch/sh/mm/kmap.c

Purpose: implements coherent highmem-style mappings used to avoid D-cache aliases on SH.

Important functions: `kmap_coherent_init` and `kunmap_coherent`.

Control flow: initialization prepares per-CPU or fixed coherent mapping space. `kunmap_coherent` tears down a coherent mapping and performs required cache/TLB cleanup.

State and persistence: manages transient coherent mappings and supporting page-table/TLB state.

Dependencies and integration: used by `cache.c` user-page copy and anonymous-page flush paths, depends on highmem, MMU context, cacheflush, and exported module support.

Risks: stale coherent mappings or missing cache purge can leave aliasing data visible. Must be safe in atomic/highmem contexts.

Test signals: highmem user-page copy tests, aliasing-cache workloads, and kmap/kunmap stress.
