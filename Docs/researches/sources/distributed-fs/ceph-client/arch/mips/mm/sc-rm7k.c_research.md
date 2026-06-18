<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-rm7k.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-rm7k.c

### Purpose
`sc-rm7k.c` manages RM7000 secondary and optional tertiary caches. It handles cache geometry reporting, cache enable/disable, tertiary-cache probing, and DMA cache maintenance.

### Important APIs, Types, And Functions
`rm7k_sc_wback_inv()` and `rm7k_sc_inv()` maintain secondary and tertiary caches for DMA. `__rm7k_sc_enable()` and `__rm7k_tc_enable()` initialize tags while running uncached. `__probe_tcache()` detects tertiary-cache wraparound size. `rm7k_sc_init()` populates cache descriptors and installs `rm7k_sc_ops`.

### Control Flow
Initialization checks for secondary-cache presence, fills `current_cpu_data.scache`, enables secondary cache if needed, registers bcache ops, then probes tertiary cache when Config says it is present. The tertiary probe enables TC, writes known tags across increasing powers of two, detects wraparound by reading tags, disables TC, and later enables it for use.

### State, Persistence, And Dependencies
Persistent state includes `rm7k_tcache_init`, `tcache_size`, CP0 config bits, and CPU cache descriptors. The file depends on `run_uncached()`, CP0 tag registers, cache op encodings, and primary cache geometry globals.

### Integration Points
DMA cache operations use these callbacks through `bcops`. CPU cache information is visible to generic MIPS cache management and diagnostics.

### Risks
The tertiary-cache size probe depends on tag behavior and address aliasing; mistakes can corrupt cache state. Enable routines must run uncached to avoid executing through cache being reinitialized. Secondary and tertiary page granularities differ, so range math must stay exact.

### Test Signals
Boot RM7000 with and without tertiary cache, verify reported cache sizes, run DMA coherency tests across ranges crossing tertiary-cache page boundaries, and exercise enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-rm7k.c -->
