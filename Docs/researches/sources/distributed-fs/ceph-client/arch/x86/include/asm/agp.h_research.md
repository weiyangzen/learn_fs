## `sources/distributed-fs/ceph-client/arch/x86/include/asm/agp.h`

Purpose: x86 AGP/GART cache-coherency helpers for pages mapped into the AGP aperture.

Important APIs and macros: `map_page_into_agp(page)` sets the page uncacheable with `set_pages_uc()`, `unmap_page_from_agp(page)` restores write-back with `set_pages_wb()`, and `flush_agp_cache()` uses `wbinvd()`.

Control flow: no function bodies beyond macro expansion; AGP users call these at mapping/unmapping or flush points.

State and persistence: mutates page cacheability attributes in the kernel page tables and CPU cache state. No private state.

Dependencies and integration points: agpgart/GART drivers, x86 cacheflush/page attribute APIs, and memory aliasing rules.

Risks: conflicting cacheability aliases can corrupt data on some CPUs. `wbinvd()` is heavy and global, so misuse has performance impact. Forgetting to restore write-back affects later page use.

Test signals: AGP/GART driver tests on supported hardware, PAT/cache attribute debug warnings, graphics stability, and page attribute restore checks.
