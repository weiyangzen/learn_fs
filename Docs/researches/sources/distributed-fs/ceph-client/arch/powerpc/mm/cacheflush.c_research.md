# sources/distributed-fs/ceph-client/arch/powerpc/mm/cacheflush.c

Purpose: implements PowerPC instruction/data cache maintenance required after code modification, user page copy/clear, and folio cache synchronization.

Important APIs and control flow: `flush_icache_range()` first handles coherent-I-cache CPUs with a dummy `icbi`, otherwise cleans D-cache and invalidates I-cache lines or uses 44x `iccci`. `flush_dcache_icache_folio()` covers normal, highmem, BookE, and physical-address fallback paths. `clear_user_page()`, `copy_user_page()`, and `flush_icache_user_page()` integrate cache maintenance with generic user page helpers.

State and dependencies: no durable state; behavior depends on CPU feature bits, cache-line geometry, highmem configuration, MMU type, and local kmap APIs. The highmem physical flush temporarily disables data translation with carefully constrained assembly. Risks are stale executable instructions, over-invalidation on virtually tagged 44x I-caches, unsafe memory accesses while MSR_DR is disabled, and highmem alias mistakes. Test signals include module/kprobe/BPF text patch execution, self-modifying code tests, highmem user executable pages, and 44x/BookE boot tests.
