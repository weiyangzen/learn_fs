# sources/distributed-fs/ceph-client/kernel/dma/debug.c

## Purpose
This file implements DMA API misuse detection. It tracks live DMA mappings and coherent/noncoherent allocations, verifies unmap/sync/free parameters, detects mapping of illegal memory, tracks unchecked `dma_mapping_error()` results, reports leaks on driver unbind, and exposes debugfs controls and dumps.

## Important APIs, Types, And Functions
`struct dma_debug_entry` records device, DMA address, size, type, direction, scatterlist counts, physical address, map-error state, cacheline-clean state, and optional stack trace. Core helpers include hash bucket lookup/add/delete, `active_cacheline_insert()`/`remove()`, `dma_entry_alloc()`/`free()`, `add_dma_entry()`, `check_unmap()`, `check_sync()`, `check_sg_segment()`, `check_for_stack()`, and `check_for_illegal_area()`. Public hooks include `debug_dma_map_single()`, `debug_dma_map_phys()`, `debug_dma_mapping_error()`, `debug_dma_unmap_phys()`, `debug_dma_map_sg()`, `debug_dma_unmap_sg()`, coherent alloc/free hooks, sync hooks, noncoherent page alloc/free hooks, `debug_dma_dump_mappings()`, and `dma_debug_add_bus()`.

## Control Flow
`dma_debug_init()` initializes hash buckets and preallocates entries at core init unless disabled by `dma_debug=off`. Mapping hooks allocate entries, validate stack/text/rodata/SG segment rules, then add entries to a DMA-address hash and active-cacheline radix tree. Unmap/free hooks build a reference entry, locate a best-fit match, verify size/type/direction/SG count/CPU address and map-error checks, then remove and free the entry. Sync hooks locate a containing mapping and verify range and direction. Debugfs exposes error counts, free-entry counters, driver filtering, and a mapping dump. Bus notifiers report live mappings when drivers unbind.

## State, Persistence, And Dependencies
Global state includes `dma_entry_hash[16384]`, `free_entries`, `global_disable`, `dma_debug_initialized`, error display counters, preallocation counts, driver filter state, and the active-cacheline radix tree. It persists only for the boot. Dependencies include DMA mapping APIs, scatterlists, stacktrace, debugfs, bus notifiers, SWIOTLB, sections bounds, vmalloc/usercopy helpers, radix tree, and spinlocks.

## Integration Points
Generic DMA mapping wrappers call these hooks when `CONFIG_DMA_API_DEBUG` is enabled; `debug.h` provides no-op stubs otherwise. Debugfs creates `/sys/kernel/debug/dma-api/*`. Bus types call `dma_debug_add_bus()` to get unbind leak checks.

## Risks
Instrumentation is expensive and can disable itself on allocation failure or cacheline tracking ENOMEM. Error counters are intentionally racy because debugfs exposes them directly. Hashing by DMA address can have ambiguous matches when the same physical address maps multiple times, so best-fit logic may still avoid reporting in ambiguous cases. Cacheline overlap tracking can warn on legitimate advanced use unless attributes mark the mapping clean or skip CPU sync.

## Test Signals
Trigger double unmap, wrong unmap size/type/direction, missing `dma_mapping_error()`, stack/vmalloc/text/rodata mapping, SG segment too large or crossing boundary, sync outside allocation, unbind with leaked mappings, driver filter debugfs writes, dynamic pool growth, and cacheline overlap warnings.
