## sources/distributed-fs/ceph-client/arch/arm/mm/copypage-v6.c

### Purpose
Implements ARMv6 user page copy/clear functions, switching at boot between simple non-aliasing helpers and VIPT alias-aware fixed-color mappings.

### Important APIs, Types, And Functions
Exports initial `v6_user_fns`, later patched by `v6_userpage_init` when `cache_is_vipt_aliasing()`. Helpers include `v6_copy_user_highpage_nonaliasing`, `v6_clear_user_highpage_nonaliasing`, `discard_old_kernel_data`, `v6_copy_user_highpage_aliasing`, and `v6_clear_user_highpage_aliasing`.

### Control Flow
Non-aliasing paths use `kmap_atomic`, `copy_page`, and `clear_page`. Aliasing paths compute `CACHE_COLOUR(vaddr)`, flush source folio data if needed, discard old kernel data, lock `v6_lock`, install color-matched fixed PTEs at `COPYPAGE_V6_FROM/TO`, run copy/clear, and unlock.

### State, Dependencies, And Integration
State is the raw spinlock and the runtime mutation of `cpu_user` function pointers. It depends on `mm.h` fixed aliases, cache type helpers, TLB flush via `set_top_pte`, highmem, and folio `PG_dcache_clean`. It integrates with core ARM page fault/COW machinery.

### Risks And Test Signals
Risks include fixed alias races, highmem unsafety noted in comments for `page_address`, wrong cache-color computation, and stale executable aliases. Test ARMv6 VIPT aliasing and non-aliasing systems, highmem configurations, COW/page-cache sharing, and executable mmap coherency.
