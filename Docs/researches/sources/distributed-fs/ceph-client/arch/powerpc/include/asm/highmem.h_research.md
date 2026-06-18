# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/highmem.h

Purpose: Provides PowerPC highmem declarations and kmap support glue for 32-bit systems with memory beyond the permanent kernel mapping.

Important APIs, types, and functions: Defines `PKMAP_BASE`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR()`, `PKMAP_ADDR()`, declares `kmap_prot`, `kmap_pte`, and includes generic highmem helpers. It also declares `flush_cache_kmaps()` behavior.

Control flow: Highmem pages are temporarily mapped through pkmap slots. Generic kmap code uses the architecture constants and page-table pointer to establish mappings and flush caches as needed.

State and persistence: pkmap page tables and mapping counters are runtime-only kernel state.

Dependencies and integration points: Depends on page-table, cache flush, and generic highmem infrastructure. It is relevant mainly for 32-bit PowerPC highmem builds.

Risks: Incorrect slot arithmetic or cache flushing can corrupt highmem data. Highmem code is config-sensitive and must not leak into PPC64 assumptions.

Test signals: 32-bit highmem boot, kmap/kunmap stress, pkmap wraparound, cache-coherency tests, and build coverage with and without `CONFIG_HIGHMEM`.
