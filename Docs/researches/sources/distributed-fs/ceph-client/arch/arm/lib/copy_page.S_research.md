# sources/distributed-fs/ceph-client/arch/arm/lib/copy_page.S

Purpose: optimized `copy_page` routine for copying one kernel page using cacheline-sized blocks and prefetch hints.

Control flow saves minimal registers, prefetches source cachelines, loops over `PAGE_SZ / (2 * L1_CACHE_BYTES)` chunks, and copies four registers at a time with `ldmia/stmia`. There is no fault handling because both addresses are kernel page mappings. Dependencies include page/cache constants and PLD assembler macros. Risks are cacheline-size assumptions, register clobber mistakes, and use on overlapping ranges, which this API does not support. Test signals are page-copy correctness, highmem/page allocator users, and architecture build coverage with and without PLD.
