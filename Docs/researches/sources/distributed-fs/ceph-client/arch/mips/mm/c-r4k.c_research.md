# sources/distributed-fs/ceph-client/arch/mips/mm/c-r4k.c

Purpose: primary R4K-style cache subsystem for many MIPS CPUs. It probes cache geometry, selects optimized blast functions, implements cache/TLB coherency hooks, DMA cache operations, CPU errata workarounds, coherency attributes, and power-management restoration.

Important APIs/functions: `r4k_cache_init()` is the main entry. It calls `probe_pcache()`, `probe_vcache()`, `setup_scache()`, selects line-size-specific flush functions, sets global cache flush pointers, builds page routines, flushes caches, configures CCA, and installs cache error handlers. Public globals include exported `r4k_blast_dcache` and `r4k_blast_icache`.

Control flow: flush paths use `r4k_on_each_cpu()` to decide whether cache ops must run on foreign cores. Page/range flushes check ASID/MMID validity, executable mappings, dcache aliasing, icache fill behavior, and whether a temporary coherent mapping is required. DMA paths choose scache or dcache operations by cache inclusivity, size, and IPI constraints.

State and persistence: cache sizes and function pointers are static/global boot state. `_page_cachable_default`, `shm_align_mask`, and CPU option flags are configured once and restored after CPU PM exit.

Dependencies and integration: central implementation behind `cache.c` globals for R4K, SB1, and many MIPS32/MIPS64 CPUs; depends on CP0 config registers, SMP masks, board secondary cache ops, uasm page generation, and exception vectors.

Risks and test signals: high risk due to CPU-specific errata and aliases. Test boot on each CPU family, executable mmap/JIT coherency, DMA map/unmap, SMP flush scope, Loongson/BMIPS overrides, `cca=` early param, CPU suspend/resume, and cache error vector installation. The file contains duplicated CPU cases and workaround branches that deserve build-matrix coverage.
