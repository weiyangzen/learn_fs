# sources/distributed-fs/ceph-client/arch/mips/include/asm/r4kcache.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/r4kcache.h

### Purpose
`r4kcache.h` implements inline MIPS R4K-style cache operations and generated blast helpers for I-cache, D-cache, S-cache, user pages, address ranges, and Loongson node-aware secondary-cache flushing.

### Important APIs, Types, And Functions
Important declarations are `r5k_sc_init`, `rm7k_sc_init`, `mips_sc_init`, `r4k_blast_dcache`, and `r4k_blast_icache`. Important macros/functions include `INDEX_BASE`, `_cache_op`, `cache_op`, line flush/invalidate helpers, `protected_cache_op`, `protected_flush_icache_line`, `protected_writeback_dcache_line`, `protected_writeback_scache_line`, `invalidate_tcache_page`, `cache_unroll`, and generated `blast_*cache*`, `blast_*cache*_page`, `blast_*cache*_page_indexed`, `blast_*cache*_range`, protected range helpers, user-page helpers, and Loongson node helpers.

### Control Flow
Callers invoke inline helpers that emit `cache` or EVA `cachee` instructions. Protected variants wrap the instruction with exception-table fixups and return `-EFAULT` on invalid user addresses. Blast helpers iterate over ways/indices or line ranges, unrolling 32 cache operations per inner chunk.

### State, Persistence, Dependencies, And Integration
State is CPU cache contents/tags, current CPU cache geometry, exception-table fixups, and optional node address bases. Dependencies include cache op encodings, CPU feature/type detection, MIPS assembly helpers, EVA support, MM zones, and unroll macros. Integration is with cache flush implementations, DMA/I-cache coherency, signal trampolines, user copy, secondary cache initialization, and Loongson NUMA cache handling.

### Risks
Inline assembly constraints and ISA level must match target CPU. Wrong line size or way geometry can leave stale cachelines. Protected variants rely on exact exception-table relocation. Some CPUs need special operations, such as Loongson2 I-cache invalidation and R10000 writeback/invalidate behavior.

### Test Signals
Cross-build EVA/non-EVA, Loongson, R5K/RM7K, secondary-cache, and NUMA configs. Run I-cache coherency tests after code modification, DMA cache maintenance tests, user-address protected flush fault tests, and boot cache init diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/r4kcache.h -->
