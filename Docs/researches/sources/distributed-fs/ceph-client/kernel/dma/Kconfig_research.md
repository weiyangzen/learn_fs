# sources/distributed-fs/ceph-client/kernel/dma/Kconfig

## Purpose
This Kconfig file defines the kernel DMA mapping framework feature switches. It controls whether DMA exists, which helper implementations build, architecture capability flags, SWIOTLB behavior, restricted pools, coherent pools, CMA, DMA API debugging, and the DMA map benchmark debugfs driver.

## Important APIs, Types, And Functions
Key symbols are `HAS_DMA`, `DMA_OPS_HELPERS`, `DMA_OPS_BYPASS`, `ARCH_HAS_DMA_MAP_DIRECT`, `NEED_*` scatterlist/map-state flags, `ARCH_DMA_ADDR_T_64BIT`, sync/prep/unencrypted/batched architecture flags, `ARCH_DMA_DEFAULT_COHERENT`, `SWIOTLB`, `SWIOTLB_DYNAMIC`, `DMA_NEED_SYNC`, `DMA_RESTRICTED_POOL`, `DMA_NONCOHERENT_MMAP`, `DMA_COHERENT_POOL`, `DMA_GLOBAL_POOL`, `DMA_DIRECT_REMAP`, `ARCH_HAS_DMA_ALLOC`, `DMA_CMA`, `DMA_NUMA_CMA`, CMA sizing choices, `DMA_API_DEBUG`, and `DMA_MAP_BENCHMARK`.

## Control Flow
The file is declarative. Symbol selections and dependencies drive compilation in `kernel/dma/Makefile` and conditional code in the DMA implementation files. CMA size choice selects megabytes, percentage, minimum, or maximum. Debug and benchmark options expose runtime instrumentation when selected.

## State, Persistence, And Dependencies
Configuration state is persisted in the kernel build `.config`. Several symbols select helper requirements, such as `DMA_API_DEBUG` and `SWIOTLB` selecting map state. Device-tree restricted pools depend on OF reserved memory and SWIOTLB. CMA depends on `HAVE_DMA_CONTIGUOUS` and `CMA`; benchmark depends on `DEBUG_FS`.

## Integration Points
These symbols gate `coherent.c`, `contiguous.c`, `debug.c`, `direct.c`, `dummy.c`, `map_benchmark.c`, and other DMA files not in this work item. Architecture Kconfigs select capability symbols to choose direct mapping, arch allocation hooks, cache sync hooks, and coherent defaults.

## Risks
Incorrect selects can compile incompatible paths, for example non-coherent mmap without page-table support or global coherent pools on architectures that require uncached setup. Enabling `DMA_API_DEBUG` is intentionally expensive. CMA sizing can reserve too much or too little early memory. Restricted pools require careful device-tree descriptions.

## Test Signals
Build matrix coverage should include no-DMA, direct-DMA, SWIOTLB, non-coherent, CMA, NUMA CMA, DMA API debug, and benchmark configurations. Runtime signals include successful boot, expected debugfs nodes, CMA reservation logs, and DMA mapping selftests.
