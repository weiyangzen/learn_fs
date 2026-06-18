# sources/distributed-fs/ceph-client/arch/arm64/mm/cache.S

Purpose: implements ARM64 cache maintenance primitives for I/D coherency, user executable mappings, DMA/cache invalidation and cleaning to PoU, PoC, and PoP.

Important APIs/types/functions: `caches_clean_inval_pou`, `caches_clean_inval_user_pou`, `icache_inval_pou`, `dcache_clean_inval_poc`, `dcache_clean_pou`, `dcache_inval_poc`, `dcache_inval_poc_nosync`, `dcache_clean_poc`, `dcache_clean_poc_nosync`, and `dcache_clean_pop`.

Control flow: PoU clean/invalidate skips D-cache work when IDC is present and skips I-cache invalidation when DIC is present. User PoU maintenance enables TTBR0 and returns `-EFAULT` through a fixup if user access fails. PoC/PoP routines walk cache lines with the appropriate `dc` operation, using clean+invalidate for partial invalidation endpoints to avoid data loss. PoP falls back to PoC when DC CVAP is unsupported.

State and persistence: no software state. It issues architectural cache maintenance and barriers affecting memory visibility and persistence.

Dependencies/integration: called by MM flush code, DMA mapping, uaccess flushcache, module/text patching, and PMEM support. Depends on assembler cache macros, CPU feature alternatives IDC/DIC/DCPOP, and uaccess helpers.

Risks: missing barriers can leave stale instructions or dirty data. Invalidation must clean partial lines to prevent losing unrelated bytes. User range faults must be reported without leaving TTBR0 access enabled. PoP fallback changes persistence guarantees on unsupported CPUs.

Test signals: self-modifying code/module load tests, DMA cache sync tests, user executable mapping flush faults, PMEM persistence tests, IDC/DIC/DCPOP feature matrix, and cache-line unaligned ranges.
