# sources/distributed-fs/ceph-client/arch/sh/mm/nommu.c

Purpose: provides NOMMU stubs and simple memory primitives for SH builds without an MMU.

Important functions: `copy_page`, `__copy_user`, `__clear_user`, TLB flush no-ops (`local_flush_tlb_*`, `__flush_tlb_global`), `kunmap_coherent`, and `page_table_range_init`.

Control flow: memory operations use plain memcpy/memset-style behavior; TLB and page-table functions are empty because no MMU translation exists.

State and persistence: mutates copied/cleared memory only; no page-table/TLB state.

Dependencies and integration: selected by `CONFIG_NOMMU` through `mm/Makefile` and satisfies generic symbols expected by shared code.

Risks: stubs must still preserve generic API contracts enough for common code. User-copy behavior lacks MMU fault recovery semantics.

Test signals: NOMMU build/boot, user-copy tests under flat memory, and absence of unresolved MMU symbols.
