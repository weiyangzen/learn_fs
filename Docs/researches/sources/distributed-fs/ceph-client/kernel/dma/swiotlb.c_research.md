# sources/distributed-fs/ceph-client/kernel/dma/swiotlb.c

## Purpose

`swiotlb.c` implements the software I/O TLB bounce-buffer allocator used when devices cannot directly DMA to a target physical address or when policy requires forced bouncing. It initializes default and optional dynamic pools, allocates aligned IO_TLB slots under segment-boundary constraints, copies data between original buffers and bounce buffers, supports encrypted-memory handling, exports status and debugfs counters, and supports restricted DMA pools from reserved memory.

## Important APIs, Types, And Functions

- `struct io_tlb_slot` records per-slot `orig_addr`, `alloc_size`, free-list `list`, and leading `pad_slots`.
- `struct io_tlb_area` records per-area `used`, next search `index`, and lock. Pools divide slots across areas for parallel allocation.
- Global boot policy includes `swiotlb_force_bounce`, `swiotlb_force_disable`, `default_nslabs`, `default_nareas`, and `io_tlb_default_mem`.
- Boot sizing and parameters: `setup_io_tlb_npages()`, `swiotlb_size_or_default()`, `swiotlb_adjust_size()`, `swiotlb_adjust_nareas()`, `limit_nareas()`, and `round_up_default_nslabs()`.
- Pool initialization: `swiotlb_init_remap()`, `swiotlb_init()`, `swiotlb_init_late()`, `swiotlb_init_io_tlb_pool()`, `add_mem_pool()`, `swiotlb_update_mem_attributes()`, `swiotlb_exit()`, and `swiotlb_print_info()`.
- Dynamic pool support under `CONFIG_SWIOTLB_DYNAMIC`: `alloc_dma_pages()`, `swiotlb_alloc_tlb()`, `swiotlb_free_tlb()`, `swiotlb_alloc_pool()`, `swiotlb_dyn_alloc()`, `swiotlb_dyn_free()`, `__swiotlb_find_pool()`, and `swiotlb_del_pool()`.
- Device initialization and lookup: `swiotlb_dev_init()`, `is_swiotlb_allocated()`, `is_swiotlb_active()`, `default_swiotlb_base()`, and `default_swiotlb_limit()`.
- Mapping core: `swiotlb_align_offset()`, `swiotlb_bounce()`, `swiotlb_search_pool_area()`, `swiotlb_find_slots()`, `swiotlb_tbl_map_single()`, `__swiotlb_tbl_unmap_single()`, `__swiotlb_sync_single_for_device()`, `__swiotlb_sync_single_for_cpu()`, `swiotlb_map()`, and `swiotlb_max_mapping_size()`.
- Restricted pool support under `CONFIG_DMA_RESTRICTED_POOL`: `swiotlb_alloc()`, `swiotlb_free()`, `rmem_swiotlb_device_init()`, `rmem_swiotlb_device_release()`, `rmem_swiotlb_setup()`, and `RESERVEDMEM_OF_DECLARE()`.

## Control Flow

Early setup parses `swiotlb=` as optional slab count, area count, and `force` or `noforce`. Initialization only proceeds when an addressing limit exists or force-bounce is requested, unless force-disable is set. `swiotlb_init_remap()` configures dynamic growth metadata, computes areas from possible CPUs when not provided, allocates low or unrestricted memblock memory, allocates slot and area descriptors, initializes every slot's free-list run length and invalid original address, and registers the pool. Late initialization follows a similar path through page allocator memory, retrying smaller orders and marking memory decrypted.

Slot allocation starts in `swiotlb_tbl_map_single()`. It computes padding from the device minimum alignment mask and requested allocation alignment, rounds the total allocation, and calls `swiotlb_find_slots()`. The search walks per-CPU-starting areas and, with dynamic support, all RCU-visible pools. `swiotlb_search_pool_area()` locks one area, enforces segment boundary and alignment constraints, checks contiguous free-list length, marks slots allocated, updates predecessor free-list lengths, advances the search index, increments usage counters, and returns the slot index.

After a slot sequence is allocated, `swiotlb_tbl_map_single()` resets `dma_skip_sync` for the device, records `pad_slots` and original addresses for the usable slots, computes the returned TLB address, and copies original data into the bounce buffer. That copy happens even for `DMA_FROM_DEVICE` to preserve bytes that a device might not overwrite during a partial write.

Unmapping with `__swiotlb_tbl_unmap_single()` first copies data back to the original buffer for `DMA_FROM_DEVICE` and bidirectional mappings unless `DMA_ATTR_SKIP_CPU_SYNC` is set. It then frees a transient dynamic pool wholesale if the mapping came from one; otherwise `swiotlb_release_slots()` reconstructs the allocation start from padding, rebuilds free-list run lengths forward and backward within the IO_TLB segment, clears original-address metadata, and decrements area/global counters.

`swiotlb_map()` wraps this for direct DMA: it traces a bounced mapping, allocates the bounce buffer, converts it to an unencrypted DMA address, verifies `dma_capable()`, and performs noncoherent device syncs. Sync helpers copy into or out of bounce buffers without releasing slots.

Dynamic growth has two lanes. A background work item can allocate a full default-sized pool and add it to the global pool list. If a mapping cannot find space and the allocator can grow, a one-mapping transient pool may be allocated immediately with `GFP_NOWAIT`, attached to the device pool list, and freed on unmap via RCU.

Restricted DMA pools are initialized from reserved-memory nodes with compatible `restricted-dma-pool`. A pool is rejected if it is reusable, default CMA/DMA memory, no-map, or highmem. The first attached device initializes `rmem->priv`, decrypts the reserved memory, creates one area, forces bounce, and points the device at that private `io_tlb_mem`.

## State And Persistence Behavior

SWIOTLB maintains long-lived in-kernel allocator state: `io_tlb_default_mem`, pool lists, slot arrays, area arrays, per-device `dma_io_tlb_mem`, dynamic per-device pool lists, usage counters, high-water counters, and debugfs directories. Slot metadata persists from map until unmap. Dynamic pools persist until explicitly removed through RCU; transient pools are tied to a single mapping. Memory encryption state is changed for bounce-buffer pages and restored on teardown/free when possible. Boot parameters persist as runtime policy flags.

## Dependencies And Integration Points

The code integrates with the direct DMA layer, DMA masks and bus limits, `dma_get_min_align_mask()`, DMA segment boundaries, memblock, page allocator, CMA/atomic DMA pools, memory encryption APIs (`set_memory_decrypted()`/`set_memory_encrypted()`), confidential-computing attributes, KMSAN, highmem copy helpers, trace events in `trace/events/swiotlb.h`, debugfs, RCU lists, device tree reserved memory, and `struct device` DMA fields initialized by `swiotlb_dev_init()`.

## Risks And Edge Cases

- Alignment and boundary calculations are subtle. Incorrect `pad_slots`, min-align masking, or free-list merging can cause data corruption or allocator leaks.
- Bounce copy direction matters: partial `DMA_FROM_DEVICE` writes require pre-copying original data into the bounce buffer, while unmap/sync must copy back only when ownership returns to CPU.
- `alloc_size` overflow and mapping-size checks guard against copying beyond the allocated bounce buffer; warnings indicate possible caller misuse or allocator metadata corruption.
- Dynamic pool publication uses RCU and memory barriers so other CPUs do not see a returned DMA address before `dev->dma_uses_io_tlb` and pool-list updates are visible.
- Encrypted-memory systems can leak pages intentionally if re-encryption fails, trading memory loss for security.
- `default_swiotlb_base()` disables dynamic growth before returning the base, which can affect later allocation capacity.
- Restricted pools are shared through `reserved_mem->priv`; initialization must be race-safe in practice and must reject memory not linearly mapped.

## Test Signals

Important signals include boot logs for pool sizing, `swiotlb=force/noforce` behavior, debugfs `io_tlb_nslabs`, used, high-water, and transient counters, tracepoint `swiotlb_bounced`, DMA API tests on devices with small masks, memory-encryption guests, highmem buffers, noncoherent devices, alignment-sensitive devices, segment-boundary cases, dynamic pool growth, transient pool allocation/free, restricted-DMA device tree pools, and exhaustion warnings when the bounce buffer is full.
