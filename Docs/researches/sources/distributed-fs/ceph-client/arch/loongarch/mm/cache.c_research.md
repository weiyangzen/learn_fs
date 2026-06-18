<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/cache.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/cache.c

### Purpose
`cache.c` initializes LoongArch cache metadata, installs the cache-error exception vector, provides a full-cache flush path, and defines the architecture VM protection map used by generic `mmap` and fault code. It is architecture support for the imported Ceph client kernel tree; Ceph depends on it indirectly through page cache, networking, DMA, and executable mapping correctness.

### Important APIs, Types, And Functions
Key functions are `cache_error_setup()`, `flush_cache_leaf()`, `__flush_cache_all()`, and `cpu_cache_init()`. The `populate_cache_properties()` macro decodes `LOONGARCH_CPUCFG16/17+leaf` into `struct cache_desc` fields: level, type, flags, ways, sets, and line size. `protection_map[16]` and `DECLARE_VM_GET_PAGE_PROT` provide page protections for `VM_READ`, `VM_WRITE`, `VM_EXEC`, and `VM_SHARED` combinations.

### Control Flow
Boot calls `cpu_cache_init()`, reads CPU configuration, enumerates L1 instruction/unified and data caches, then shifts through higher-level cache fields. It sets `CACHE_PRIVATE`, `CACHE_INCLUSIVE`, `CACHE_PRESENT`, and `LOONGARCH_CPU_PREFETCH`. `__flush_cache_all()` either flushes the last inclusive cache leaf or all present leaves. `flush_cache_leaf()` walks sets and ways over DMW0 addresses, repeating for all NUMA nodes unless the leaf is private.

### State, Persistence, And Dependencies
Persistent state is CPU-local kernel metadata in `current_cpu_data.cache_leaves`, `cache_leaves_present`, and `options`; there is no filesystem persistence. Dependencies include `asm/cpu.h`, `asm/cpu-features.h`, `asm/cacheflush.h`, LoongArch CPU config registers, NUMA node count, DMW address layout, and generic `cacheinfo`/MM protection machinery.

### Integration Points
`__flush_cache_all()` is used by suspend/resume assembly and other low-level maintenance paths. `cpu_cache_init()` feeds cacheinfo and PCI cache-line sizing. `protection_map` integrates with generic VM code so user mappings receive LoongArch PTE bits such as `_CACHE_CC`, `_PAGE_VALID`, `_PAGE_WRITE`, `_PAGE_NO_EXEC`, and `_PAGE_NO_READ`.

### Risks
Wrong CPUCFG bit decoding can report invalid cache topology or flush too little memory. Inclusive-cache assumptions are performance and correctness sensitive. The protection map is security-critical: incorrect read/write/execute or present/protnone bits can cause privilege, fault, or W^X regressions.

### Test Signals
Cross-build LoongArch configs, boot with cacheinfo enabled, compare reported cache topology with hardware, run cache alias/DMA stress, suspend/resume cache-coherency tests, and MM tests covering executable, writable, shared, and protnone mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/cache.c -->
