<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-r5k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-r5k.c

### Purpose
`sc-r5k.c` implements R5000 secondary-cache support. It detects cache presence/size, enables or disables the secondary cache, and provides page-granular invalidation for DMA.

### Important APIs, Types, And Functions
`blast_r5000_scache()` invalidates all secondary-cache pages. `r5k_dma_cache_inv_sc()` invalidates an affected range or the whole cache when the request covers at least `scache_size`. `r5k_sc_enable()`, `r5k_sc_disable()`, `r5k_sc_probe()`, and `r5k_sc_init()` manage lifecycle and `bcops`.

### Control Flow
Probe checks `CONF_SC`; if cache exists, it derives size from `R5K_CONF_SS`. Enabling sets `R5K_CONF_SE`, blasts the cache, and restores interrupts. DMA invalidation rounds the range to 128-line secondary-cache page boundaries because smaller invalidation is not supported.

### State, Persistence, And Dependencies
`scache_size` is the file-local persistent cache geometry. Hardware state lives in CP0 Config secondary-cache enable bits. Dependencies include `cache_op(R5K_Page_Invalidate_S)`, CP0 config helpers, and bcache operations.

### Integration Points
The registered bcache operations are used by DMA mapping and cache maintenance code on R5000 systems.

### Risks
The secondary cache is physically indexed and write-through, with invalidation granularity larger than normal cache lines. Wrong size calculation or boundary rounding can leave stale data. `BUG_ON(size == 0)` makes bad DMA caller inputs fatal.

### Test Signals
Boot R5000 systems with and without secondary cache, test DMA on small and whole-cache-sized buffers, and verify enable/disable paths preserve interrupt state and CP0 configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-r5k.c -->
