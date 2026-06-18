# sources/distributed-fs/ceph-client/arch/arm64/mm/copypage.c

Purpose: implements high-level page copy routines that combine raw page copying with KASAN tag reset, MTE tag propagation, and user-page cache flush handling.

Important APIs/types/functions: `copy_highpage`, `copy_user_highpage`, `copy_page`, `page_kasan_tag_reset`, `mte_copy_page_tags`, `try_page_mte_tagging`, hugetlb MTE tag helpers, and `flush_dcache_page`.

Control flow: `copy_highpage` copies page data, resets KASAN HW tags if enabled, then if MTE is supported copies allocation tags. Hugetlb tagged folios copy tags for all subpages when the source folio is tagged and the copy starts at the first folio page; normal pages copy tags only when the source page is MTE-tagged. `copy_user_highpage` calls `copy_highpage` and marks the destination D-cache dirty for later executable-user synchronization.

State and persistence: writes destination page data and MTE tag state, updates page/folio MTE tagged flags, and marks D-cache clean state dirty. No disk persistence.

Dependencies/integration: core COW/migration page copy, MTE, KASAN HW tags, hugetlb, cache flush code, and exported page-copy symbols.

Risks: huge page tag copy must account for subpage starts and avoid duplicating partial tag state. Reused pages during migration may already be tagged. Missing cache dirty marking can expose stale I-cache for executable mappings.

Test signals: COW and migration with MTE-tagged pages, hugetlb tagged folio copy, KASAN HW tag reset, user executable page copy followed by execution, and no-MTE fallback behavior.
