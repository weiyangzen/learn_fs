# subset-b-006027 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/mapping.c -->
# sources/distributed-fs/ceph-client/kernel/dma/mapping.c

## Purpose

`mapping.c` is the architecture-independent front door for the Linux DMA mapping API. It normalizes driver-facing calls such as streaming map/unmap, coherent allocation, scatter-gather mapping, sync, mmap, mask setup, and noncontiguous allocation, then dispatches to the right backend: direct DMA, IOMMU DMA, or architecture/device-specific `struct dma_map_ops`. It also wraps those operations with DMA API debug tracking, tracepoints, KMSAN handling, and devres-managed allocation helpers.

## Important APIs, Types, And Functions

- `struct dma_devres`, `dmam_alloc_attrs()`, and `dmam_free_coherent()` provide devres-managed coherent DMA allocations. The release path calls `dma_free_attrs()`, and the matcher validates that the caller frees the same virtual address, size, and DMA handle.
- `dma_go_direct()`, `dma_alloc_direct()`, and `dma_map_direct()` decide whether an operation can bypass `dma_map_ops`. They reject the direct path when `use_dma_iommu(dev)` is active and optionally honor `CONFIG_DMA_OPS_BYPASS` via `dev->dma_ops_bypass`.
- `dma_map_phys()`, `dma_map_page_attrs()`, `dma_unmap_phys()`, and `dma_unmap_page_attrs()` implement single-buffer streaming mapping. They validate directions, masks, `DMA_ATTR_REQUIRE_COHERENT`, MMIO, confidential-computing shared attributes, and zone-device pages.
- `__dma_map_sg_attrs()`, `dma_map_sg_attrs()`, `dma_map_sgtable()`, and `dma_unmap_sg_attrs()` handle scatterlists and sg_tables. The internal helper preserves negative errno details for `dma_map_sgtable()`, while the legacy scatterlist API collapses errors to zero.
- `dma_map_resource()` and `dma_unmap_resource()` map MMIO/resource ranges by forcing `DMA_ATTR_MMIO` and rejecting normal RAM PFNs under DMA API debug.
- Under `CONFIG_DMA_NEED_SYNC`, `__dma_sync_single_for_cpu()`, `__dma_sync_single_for_device()`, `__dma_sync_sg_for_cpu()`, `__dma_sync_sg_for_device()`, `__dma_need_sync()`, `dma_need_unmap()`, and `dma_setup_need_sync()` centralize cache/ownership synchronization policy.
- `dma_get_sgtable_attrs()`, `dma_can_mmap()`, `dma_mmap_attrs()`, and `dma_pgprot()` expose coherent allocation export/mmap support and choose page protections for coherent or write-combined memory.
- `dma_alloc_attrs()`, `dma_free_attrs()`, `dma_alloc_pages()`, `dma_free_pages()`, `dma_mmap_pages()`, `dma_alloc_noncontiguous()`, `dma_free_noncontiguous()`, `dma_vmap_noncontiguous()`, `dma_vunmap_noncontiguous()`, and `dma_mmap_noncontiguous()` provide allocation variants.
- `dma_set_mask()`, `dma_set_coherent_mask()`, `dma_get_required_mask()`, `dma_addressing_limited()`, `dma_max_mapping_size()`, `dma_opt_mapping_size()`, `dma_get_merge_boundary()`, and `dma_pci_p2pdma_supported()` expose device capability and sizing queries.

## Control Flow

The common control pattern is: validate API inputs, choose direct/IOMMU/ops backend, call the backend, then emit trace/debug/KMSAN side effects. For streaming physical mappings, `dma_map_phys()` first rejects invalid directions or missing masks, rejects required-coherent mappings on noncoherent devices, then uses direct mapping if `dma_map_direct()` or `arch_dma_map_phys_direct()` says it is allowed. Otherwise it rejects `DMA_ATTR_CC_SHARED`, then tries `iommu_dma_map_phys()` or `ops->map_phys()`. Unmap mirrors that path.

Scatter-gather mapping follows the same backend selection but has more error normalization. `__dma_map_sg_attrs()` accepts only expected negative errors (`-EINVAL`, `-ENOMEM`, `-EIO`, `-EREMOTEIO`); unexpected negative returns are warned, traced as errors, and converted to `-EIO`. The public `dma_map_sg_attrs()` returns zero on any negative error to preserve the older API contract, while `dma_map_sgtable()` propagates the errno and records `sgt->nents` on success.

Allocation flow first checks device coherent mask and rejects `__GFP_COMP`, then tries per-device coherent memory with `dma_alloc_from_dev_coherent()`. If that does not satisfy the request, it strips caller-provided DMA zone flags and dispatches to direct, IOMMU, or `ops->alloc`. Freeing reverses this order: release device coherent memory first, warn if called with IRQs disabled, trace/debug the free, then dispatch to direct, IOMMU, or `ops->free`.

Noncontiguous allocation uses the IOMMU allocator when available; otherwise it falls back to a single page-backed sg_table from `alloc_single_sgt()`. Vmap, vunmap, and mmap for noncontiguous allocations similarly defer to IOMMU helpers or operate on the single fallback page.

## State And Persistence Behavior

This file does not persist state to disk. It mutates runtime device state: DMA masks (`*dev->dma_mask`, `dev->coherent_dma_mask`), `dev->dma_skip_sync`, and devres allocation records. It also emits tracepoints and DMA debug records, updates KMSAN state for DMA ownership transfers, and relies on per-device coherent pools managed elsewhere. Managed allocations persist until explicit free or device detach through devres.

## Dependencies And Integration Points

The file is tightly integrated with `linux/dma-map-ops.h`, `direct.h`, `iommu-dma.h`, `debug.h`, KMSAN, trace events in `trace/events/dma.h`, scatterlist APIs, vm/mmap APIs, and arch hooks such as `arch_dma_map_phys_direct()`, `arch_dma_alloc_direct()`, `arch_dma_set_mask()`, and cache-sync operations. It is exported heavily (`EXPORT_SYMBOL`, `EXPORT_SYMBOL_GPL`) and is therefore a shared kernel subsystem surface used by drivers, IOMMU backends, architecture DMA implementations, and DMA API debugging.

## Risks And Edge Cases

- Backend selection must stay symmetric between map/unmap and alloc/free; mismatches can leak IOVA space, bounce buffers, or coherent memory.
- `DMA_ATTR_REQUIRE_COHERENT`, `DMA_ATTR_MMIO`, and `DMA_ATTR_CC_SHARED` are policy-sensitive. Incorrect handling can break noncoherent devices, resource mappings, or confidential-computing sharing assumptions.
- The direct path depends on masks, `bus_dma_limit`, and optional bypass state. Incorrect mask updates can silently expose devices to unreachable DMA addresses.
- `dma_free_attrs()` warns in IRQ-disabled context because some noncoherent implementations may sleep through `vunmap()`.
- `dma_get_sgtable_attrs()` is explicitly documented as fundamentally unsafe for some coherent allocations because not all coherent memory has ordinary `struct page` backing and streaming APIs must not be mixed with coherent aliases.
- `dma_need_unmap()` can return false only after mappings have been established, because SWIOTLB use can reset `dev->dma_skip_sync`.

## Test Signals

Useful test signals include DMA API debug warnings, tracepoints (`dma_map_phys`, `dma_map_sg`, allocation/free and sync traces), KMSAN reports around DMA buffers, boot/device tests across direct DMA and IOMMU configurations, noncoherent architecture tests, SWIOTLB/bounce-buffer tests, P2PDMA capability checks, mmap tests for coherent allocations, and sg_table error-path tests verifying errno versus zero-return API behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/ops_helpers.c -->
# sources/distributed-fs/ceph-client/kernel/dma/ops_helpers.c

## Purpose

`ops_helpers.c` contains common helper implementations for DMA operation backends that allocate ordinary pages visible in the direct kernel mapping or vmalloc space. It builds single-entry scatter-gather tables, maps coherent memory into user VMAs, and supplies generic page allocation/free helpers for non-direct DMA paths.

## Important APIs, Types, And Functions

- `dma_common_vaddr_to_page()` converts a CPU virtual address to a `struct page` using `vmalloc_to_page()` for vmalloc addresses and `virt_to_page()` otherwise.
- `dma_common_get_sgtable()` allocates a one-entry `sg_table` and points it at the page backing an already allocated DMA buffer.
- `dma_common_mmap()` handles userspace mapping for coherent DMA memory under `CONFIG_MMU`. It applies `dma_pgprot()`, gives device-specific coherent areas first chance through `dma_mmap_from_dev_coherent()`, validates VMA offsets and sizes, and remaps with `remap_pfn_range()`.
- `dma_common_alloc_pages()` allocates contiguous or buddy pages, maps their physical address through IOMMU or `ops->map_phys()` with `DMA_ATTR_SKIP_CPU_SYNC`, zeroes the CPU mapping, and returns the page.
- `dma_common_free_pages()` unmaps through IOMMU or `ops->unmap_phys()` and releases the allocation with `dma_free_contiguous()`.

## Control Flow

The sg_table helper is intentionally minimal: find the backing page, allocate one table entry, and install a page-aligned length. The mmap helper first chooses DMA page protections, delegates to per-device coherent mmap if present, rejects out-of-range offsets, then remaps the underlying PFN range into the VMA.

Page allocation first prefers `dma_alloc_contiguous()`, falls back to `alloc_pages_node()`, maps the resulting physical range for DMA through the active IOMMU or map ops, and unwinds on `DMA_MAPPING_ERROR`. Freeing performs the inverse unmap before releasing the contiguous allocation.

## State And Persistence Behavior

No durable state is stored. The file creates transient sg_table state supplied by the caller, VMA mappings in a process address space, DMA mappings in the IOMMU or backend map_ops, and page allocations that persist until `dma_common_free_pages()`.

## Dependencies And Integration Points

This helper layer depends on `dma-map-ops.h`, `iommu-dma.h`, vmalloc detection, scatterlist allocation, mmap/remap functions, contiguous memory allocation, and backend `struct dma_map_ops`. It is used by DMA backends that need a common implementation without duplicating the page-to-sgtable and mmap mechanics.

## Risks And Edge Cases

- `dma_common_vaddr_to_page()` assumes the virtual address is either vmalloc-backed or a direct kernel mapping; special coherent mappings without ordinary page backing are outside its safe model.
- `dma_common_mmap()` must validate `vm_pgoff` and `vma_pages()` to prevent mapping beyond the original allocation.
- `dma_common_alloc_pages()` uses `DMA_ATTR_SKIP_CPU_SYNC`; callers must ensure the chosen ownership/sync semantics are valid.
- If `ops->map_phys()` fails, the allocated pages must be freed immediately to avoid leaks.

## Test Signals

Test with coherent mmap users, IOMMU-backed page allocations, forced map failure injection, vmalloc-backed coherent memory, VMA offset boundary cases, and non-MMU builds where mmap returns `-ENXIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/ops_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/pool.c -->
# sources/distributed-fs/ceph-client/kernel/dma/pool.c

## Purpose

`pool.c` implements atomic coherent DMA pools used when callers need DMA-coherent memory from contexts that cannot sleep or cannot perform the normal allocation/remap path. It creates separate genalloc pools for DMA, DMA32, and kernel-addressable zones, supports an early `coherent_pool=` boot parameter, exposes pool sizes via debugfs, and grows pools asynchronously when they become low.

## Important APIs, Types, And Functions

- Global pools: `atomic_pool_dma`, `atomic_pool_dma32`, and `atomic_pool_kernel`, with size counters `pool_size_dma`, `pool_size_dma32`, and `pool_size_kernel`.
- `early_coherent_pool()` parses the `coherent_pool` early boot parameter into `atomic_pool_size`.
- `dma_atomic_pool_debugfs_init()` creates `/sys/kernel/debug/dma_pools` size files.
- `cma_in_zone()` checks whether the default CMA area is usable for a requested DMA zone.
- `atomic_pool_expand()` allocates pages, prepares them coherent, optionally remaps them with `dma_common_contiguous_remap()`, decrypts memory, and adds the range to a `gen_pool`.
- `atomic_pool_resize()` and `atomic_pool_work_fn()` grow pools in background work when free space falls below the configured initial pool size.
- `dma_atomic_pool_init()` sizes and initializes pools at `postcore_initcall`.
- `dma_guess_pool()` orders fallback pool selection based on GFP zone flags.
- `dma_alloc_from_pool()` allocates zeroed memory from the best available pool and returns the backing page plus CPU address.
- `dma_free_from_pool()` finds the owning gen_pool and frees the address range.

## Control Flow

At boot, `dma_atomic_pool_init()` computes a default pool size of 128 KiB per GiB of RAM, bounded by a 128 KiB minimum and `MAX_ORDER_NR_PAGES`, unless `coherent_pool=` provided an override. It initializes workqueue state, creates a kernel pool if normal memory exists, then optional DMA and DMA32 pools when their managed zones exist. Each pool is a `gen_pool` configured for first-fit order alignment and seeded by `atomic_pool_expand()`.

Expansion chooses the largest feasible order no larger than `MAX_PAGE_ORDER`, preferring CMA if the CMA area belongs to the requested zone, then falling back to `alloc_pages()`. It prepares coherent memory, remaps for `CONFIG_DMA_DIRECT_REMAP`, decrypts pages because DMA pools must be unencrypted, and adds the virtual-to-physical range to the gen_pool. Error paths re-encrypt when possible, remove remaps, and free pages; if re-encryption fails after successful decryption, the code intentionally leaks the pages rather than returning insecure memory to the allocator.

Allocation tries pools in a zone-sensitive fallback order from `dma_guess_pool()`. `__dma_alloc_from_pool()` allocates from gen_pool, validates the physical address through the caller-supplied `phys_addr_ok` callback, schedules background growth if available space drops below the baseline size, zeroes the CPU address, and returns the page. Freeing scans possible pools and releases the range if it belongs to one.

## State And Persistence Behavior

The pools are long-lived kernel runtime state initialized after core boot and not designed to shrink. Pool pages remain decrypted for the lifetime of the pools. Debugfs size counters persist while the kernel runs. Dynamic expansion is asynchronous through `atomic_pool_work`; allocations can schedule this work when pool availability drops.

## Dependencies And Integration Points

The implementation depends on CMA, genalloc, debugfs, DMA direct remapping, set_memory encryption/decryption, coherent preparation hooks, workqueues, zone management, and the generic DMA pool APIs declared in `dma-map-ops.h`. SWIOTLB dynamic allocation also uses `dma_alloc_from_pool()` for atomic encrypted-memory cases.

## Risks And Edge Cases

- Pool sizing affects atomic DMA reliability; too-small pools trigger allocation failures and warnings.
- Decryption/re-encryption failures are security-sensitive. The intentional leak path avoids returning memory with uncertain encryption state.
- `atomic_pool_expand()` does not shrink pools, so repeated low-water growth can permanently consume memory.
- Zone fallback order must preserve device addressing constraints; using a wider pool for a narrow device is gated by `phys_addr_ok`.
- Remapped coherent memory cannot be used in contexts that sleep incorrectly, and expansion itself may sleep, which is why allocation from existing pools is separated from background growth.

## Test Signals

Check boot logs for preallocated pool messages, debugfs pool size files, atomic DMA allocation under `GFP_ATOMIC`, exhaustion warnings, background expansion behavior, CMA-zone selection, encrypted-memory systems, `CONFIG_DMA_DIRECT_REMAP` mappings, and free-path recognition through `dma_free_from_pool()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/remap.c -->
# sources/distributed-fs/ceph-client/kernel/dma/remap.c

## Purpose

`remap.c` provides generic remapping helpers for coherent DMA allocations. It can create vmalloc-style coherent mappings from an array of pages or a contiguous page range, find the page array backing a coherent mapping, and free such remaps.

## Important APIs, Types, And Functions

- `dma_common_find_pages()` looks up a `vm_struct` with `find_vm_area()`, verifies `VM_DMA_COHERENT`, warns on unexpected flags, and returns the stored page array.
- `dma_common_pages_remap()` calls `vmap()` with `VM_DMA_COHERENT` and stores the caller-provided `pages` array in the resulting vm_area for later discovery.
- `dma_common_contiguous_remap()` builds a temporary array of consecutive `struct page *` entries with `kvmalloc_objs()`, maps them with `vmap()`, and frees the temporary array.
- `dma_common_free_remap()` validates that the address refers to a coherent vm_area and releases it with `vunmap()`.

## Control Flow

Remapping an arbitrary page array is direct: call `vmap()` with the requested protection and coherent flag, then attach the page list to the vm_area. Remapping a contiguous allocation first materializes a page pointer array from the starting page and page count. Freeing performs defensive validation before calling `vunmap()`.

## State And Persistence Behavior

The persistent runtime state is the `vm_struct` created by `vmap()`, including the `VM_DMA_COHERENT` flag and page-array pointer. That state exists until `dma_common_free_remap()` unmaps it. The file does not maintain global state.

## Dependencies And Integration Points

The helpers depend on `vmap()`, `vunmap()`, `find_vm_area()`, vmalloc flags, `pgprot_t`, and kernel allocation helpers. They are used by coherent DMA implementations and the atomic pool code when direct remapping is enabled.

## Risks And Edge Cases

- `dma_common_pages_remap()` stores the caller's `pages` pointer in the vm_area; the caller must keep that page array valid if later discovery is expected.
- `dma_common_contiguous_remap()` frees its temporary page array after `vmap()`, so `dma_common_find_pages()` is not useful for that path unless the vmalloc internals retain their own page list.
- Freeing an address that is not a coherent remap triggers a warning and returns without unmapping.
- These helpers cannot be used from non-sleeping contexts.

## Test Signals

Exercise coherent remap allocation/free, invalid free warnings, `VM_DMA_COHERENT` flag checks, page-array discovery for page-array remaps, and `CONFIG_DMA_DIRECT_REMAP` users such as atomic pool expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/remap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/swiotlb.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/dma/swiotlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/elfcorehdr.c -->
# sources/distributed-fs/ceph-client/kernel/elfcorehdr.c

## Purpose

`elfcorehdr.c` stores and parses the physical location and optional size of the ELF core header supplied to a kdump capture kernel. The values are used for vmcore handling and also by crash-dump detection paths such as `is_kdump_kernel()`.

## Important APIs, Types, And Functions

- `elfcorehdr_addr` is a globally exported `unsigned long long` initialized to `ELFCORE_ADDR_MAX`, meaning no core header is configured.
- `elfcorehdr_size` stores an optional parsed size.
- `setup_elfcorehdr()` parses the early boot parameter `elfcorehdr=[size[KMG]@]offset[KMG]` using `memparse()`.
- `early_param("elfcorehdr", setup_elfcorehdr)` registers the parser during early boot.

## Control Flow

When the kernel receives `elfcorehdr=`, `setup_elfcorehdr()` rejects a null argument, parses the first number into `elfcorehdr_addr`, and then checks for `@`. If present, the first number is reinterpreted as `elfcorehdr_size` and the value after `@` becomes the header physical address. The function succeeds when parsing advanced the input pointer and otherwise returns `-EINVAL`.

## State And Persistence Behavior

The parsed address and size are global kernel runtime state. They are set once during early boot and exported for other crash-dump code. There is no disk persistence.

## Dependencies And Integration Points

This file depends on `crash_dump.h`, `memparse()`, early boot parameter handling, and the kdump/vmcore subsystem. `elfcorehdr_addr` is exported with `EXPORT_SYMBOL_GPL` because other kernel code needs to detect and locate crash-dump metadata.

## Risks And Edge Cases

- An omitted argument returns `-EINVAL`.
- The parser accepts size plus address only when separated by `@`; otherwise the single parsed value is treated as the address.
- Incorrect bootloader-provided addresses or sizes can prevent vmcore discovery or mislead kdump detection.

## Test Signals

Test by booting capture kernels with `elfcorehdr=offset` and `elfcorehdr=size@offset`, checking `/proc/vmcore` availability where configured, validating `is_kdump_kernel()` behavior, and verifying invalid parameter handling in early boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/elfcorehdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/Makefile -->
# sources/distributed-fs/ceph-client/kernel/entry/Makefile

## Purpose

This Makefile builds the generic kernel entry subsystem objects while disabling instrumentation that is unsafe for `noinstr` entry code. It controls sanitizer, coverage, branch profiling, and stack protector settings for files that run at interrupt, syscall, and user/guest transition boundaries.

## Important APIs, Types, And Functions

- `KASAN_SANITIZE := n`, `UBSAN_SANITIZE := n`, and `KCOV_INSTRUMENT := n` disable sanitizers and coverage for this directory.
- `ccflags-$(CONFIG_TRACE_BRANCH_PROFILING) += -DDISABLE_BRANCH_PROFILING` disables branch profiling when tracing branch profiling is enabled.
- `CFLAGS_REMOVE_common.o` removes stack protector flags for `common.o`, and `CFLAGS_common.o += -fno-stack-protector` enforces no stack protector.
- Object selection: `common.o` for `CONFIG_GENERIC_IRQ_ENTRY`, `syscall-common.o` and `syscall_user_dispatch.o` for `CONFIG_GENERIC_SYSCALL`, and `virt.o` for `CONFIG_VIRT_XFER_TO_GUEST_WORK`.

## Control Flow

Kbuild evaluates configuration symbols and includes only the matching objects. The build flags are applied before compiling the entry code so runtime behavior remains compatible with `noinstr` constraints.

## State And Persistence Behavior

There is no runtime state. The file affects build outputs and compiler instrumentation choices.

## Dependencies And Integration Points

The Makefile integrates with Kbuild, generic IRQ entry, generic syscall handling, syscall user dispatch, virtual guest-transfer work handling, sanitizer tooling, KCOV, branch profiling, and compiler stack-protector flags.

## Risks And Edge Cases

- Re-enabling sanitizers, coverage, branch profiling, or stack protector in `noinstr` entry paths can introduce instrumentation calls where tracing/RCU/lockdep state is not safe.
- Missing config guards can either omit required entry behavior or compile code on architectures that do not support it.

## Test Signals

Build kernels with combinations of `CONFIG_GENERIC_IRQ_ENTRY`, `CONFIG_GENERIC_SYSCALL`, `CONFIG_VIRT_XFER_TO_GUEST_WORK`, sanitizers, KCOV, branch profiling, and stack protector enabled. Runtime entry validation includes objtool/noinstr warnings, boot tests, interrupt/syscall smoke tests, and tracing sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/common.c -->
# sources/distributed-fs/ceph-client/kernel/entry/common.c

## Purpose

`common.c` implements generic IRQ/NMI entry and exit helpers plus the loop that completes pending thread work before returning to user mode. It coordinates scheduling, signals, uprobes, livepatch state, resume-user-mode work, architecture-specific work, RSEQ slice extension, RCU/lockdep tracing state, and NMI ftrace state at highly constrained entry boundaries.

## Important APIs, Types, And Functions

- `arch_do_signal_or_restart()` is a weak architecture hook for signal delivery/restart handling.
- `EXIT_TO_USER_MODE_WORK_LOOP`, `TIF_SLICE_EXT_SCHED`, and `TIF_SLICE_EXT_DENY` define which thread flags are handled in the loop and which flags deny RSEQ slice extension.
- `__exit_to_user_mode_loop()` processes pending work while interrupts are enabled, then disables interrupts and rereads flags.
- `exit_to_user_mode_loop()` wraps the loop and retries when `rseq_exit_to_user_mode_restart()` asks for another pass.
- `irqentry_enter()` dispatches between `irqentry_enter_from_user_mode()` and `irqentry_enter_from_kernel_mode()`.
- `raw_irqentry_exit_cond_resched()` conditionally schedules on IRQ exit if preemption state allows it.
- `irqentry_exit()` exits to user or kernel mode based on `user_mode(regs)`.
- `irqentry_nmi_enter()` and `irqentry_nmi_exit()` manage NMI entry/exit state, lockdep, context tracking, KMSAN register state, hardirq tracing, and ftrace NMI hooks.
- Dynamic preemption builds may expose `irqentry_exit_cond_resched` through static calls or static keys.

## Control Flow

Before returning to user mode, `__exit_to_user_mode_loop()` repeatedly enables interrupts and handles thread flags. Reschedule flags either grant an RSEQ slice extension or call `schedule()`. Uprobe, livepatch, signal, notify-resume, and architecture-specific work are handled in order. The loop then disables interrupts, prepares tick/nohz user entry, rereads thread flags, and repeats until no loop-relevant work remains.

`exit_to_user_mode_loop()` adds an outer retry for RSEQ restart handling. IRQ entry checks whether interrupted context was user mode; user entries call the user-mode transition helper and return state with `exit_rcu = false`, while kernel entries go through kernel-mode entry tracking. IRQ exit symmetrically chooses user-mode or kernel-mode exit. Kernel-mode IRQ exit can call `preempt_schedule_irq()` when preempt count is zero, RCU/stack checks pass, and rescheduling is needed.

NMI entry saves lockdep hardirq state, enters NMI/context tracking, marks hardirqs off, unpoisons entry registers for KMSAN inside instrumentation brackets, finishes hardirq-off tracing, and enters ftrace NMI state. NMI exit unwinds ftrace, hardirq tracing/lockdep state, context tracking, and `__nmi_exit()`.

## State And Persistence Behavior

The file mutates per-task thread flags indirectly by servicing work, scheduler state through `schedule()`/`preempt_schedule_irq()`, livepatch per-task patch state, RSEQ state, context tracking, lockdep hardirq state, ftrace NMI state, and tick/nohz state. There is no durable persistence.

## Dependencies And Integration Points

It depends on generic entry headers, scheduler/preemption, RSEQ, uprobes, livepatch, signal handling, resume-user-mode work, arch entry hooks, RCU, lockdep, context tracking, ftrace, KMSAN, tick/nohz, and dynamic preemption infrastructure. The Makefile deliberately suppresses unsafe instrumentation for this code.

## Risks And Edge Cases

- Entry/exit ordering is security- and correctness-sensitive. Enabling interrupts too early or disabling them too late can miss work or violate context tracking rules.
- `noinstr` sections must avoid compiler/tool instrumentation except inside explicit instrumentation regions.
- RSEQ slice extension interacts with scheduling latency, especially under `CONFIG_PREEMPT_RT`.
- NMI paths must preserve lockdep and tracing state exactly or later hardirq state reports become unreliable.
- Architecture hooks can add work; the loop must reread flags after interrupts were enabled because work can change concurrently.

## Test Signals

Useful signals include objtool `noinstr` validation, lockdep/RCU/context-tracking warnings, KMSAN entry-register behavior, syscall/interrupt stress, signal delivery and restart tests, uprobes and livepatch tests, RSEQ tests under reschedule pressure, PREEMPT_DYNAMIC toggles, PREEMPT_RT latency tests, and NMI/ftrace tracing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/syscall-common.c -->
# sources/distributed-fs/ceph-client/kernel/entry/syscall-common.c

## Purpose

`syscall-common.c` centralizes syscall tracepoint emission for generic syscall entry and exit paths. Keeping these helpers out of line prevents tracepoint code duplication in architecture entry code.

## Important APIs, Types, And Functions

- `CREATE_TRACE_POINTS` instantiates syscall trace events from `trace/events/syscalls.h`.
- `trace_syscall_enter()` emits `trace_sys_enter(regs, syscall)` and then rereads the syscall number with `syscall_get_nr(current, regs)`.
- `trace_syscall_exit()` emits `trace_sys_exit(regs, ret)`.

## Control Flow

On syscall entry, tracing runs first. Because probes or BPF hooks attached to the tracepoint can rewrite the syscall number, the helper rereads and returns the current syscall number from the registers. On syscall exit, the return value is passed to the exit tracepoint.

## State And Persistence Behavior

The file does not own state. Tracepoint handlers, probes, or BPF programs may observe or mutate syscall state during entry tracing.

## Dependencies And Integration Points

It depends on `entry-common.h`, syscall register helpers, the tracepoint subsystem, BPF/perf/ftrace consumers, and generic syscall entry code compiled through the entry Makefile.

## Risks And Edge Cases

- Consumers must use the returned syscall number from `trace_syscall_enter()`, not the original argument, because trace hooks may change it.
- Tracepoint overhead and instrumentation constraints matter because syscall entry is hot and sensitive.

## Test Signals

Validate with syscall tracepoints enabled, BPF programs that rewrite syscall numbers, perf/ftrace syscall tracing, and architecture generic syscall entry tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/syscall-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/syscall_user_dispatch.c -->
# sources/distributed-fs/ceph-client/kernel/entry/syscall_user_dispatch.c

## Purpose

`syscall_user_dispatch.c` implements Syscall User Dispatch, a per-task mechanism that lets user space redirect syscalls made outside an allowed dispatcher region into `SIGSYS`. It supports `prctl()` configuration, ptrace get/set of dispatch config, selector-byte filtering, inclusive/exclusive address ranges, syscall rollback, and precise `SIGSYS` metadata.

## Important APIs, Types, And Functions

- `trigger_sigsys()` builds `kernel_siginfo` with `SIGSYS`, `SYS_USER_DISPATCH`, call address, architecture, and syscall number, then forces the signal.
- `syscall_user_dispatch()` is the syscall-entry filter. It checks instruction pointer range, vDSO sigreturn exemption, optional selector state, and dispatches blocked syscalls.
- `task_set_syscall_user_dispatch()` validates and installs configuration for a target task.
- `set_syscall_user_dispatch()` applies configuration to `current`.
- `syscall_user_dispatch_get_config()` and `syscall_user_dispatch_set_config()` expose ptrace configuration using `struct ptrace_sud_config`.

## Control Flow

On syscall entry, `syscall_user_dispatch()` first allows syscalls whose instruction pointer lies in the configured direct-dispatch region. It also allows architecture-recognized vDSO sigreturn. If a selector pointer exists, it reads one byte from user memory. `SYSCALL_DISPATCH_FILTER_ALLOW` permits the syscall, `SYSCALL_DISPATCH_FILTER_BLOCK` continues to dispatch, a failed user read exits with `SIGSEGV`, and any invalid selector value exits with `SIGSYS`.

For a blocked syscall, the code sets `sd->on_dispatch`, rolls back the syscall register state with `syscall_rollback()`, and sends `SIGSYS` with syscall metadata. Configuration accepts `PR_SYS_DISPATCH_OFF`, `PR_SYS_DISPATCH_EXCLUSIVE_ON`, and `PR_SYS_DISPATCH_INCLUSIVE_ON`. Inclusive mode inverts the range by moving `offset` to the end and making `len` negative, relying on the unsigned wraparound-aware range check in the dispatch fast path. Enabling sets `SYSCALL_USER_DISPATCH` syscall work; disabling clears it.

Ptrace get copies mode, offset, len, and selector to user space. Ptrace set copies config from user space and uses the same validation path as prctl.

## State And Persistence Behavior

State lives in `task_struct.syscall_dispatch`: selector pointer, offset, length, and `on_dispatch`. The enabled bit is task syscall-work state. It persists for the task until changed by prctl/ptrace or task lifetime end. There is no disk persistence.

## Dependencies And Integration Points

The implementation depends on generic syscall entry work flags, `prctl` constants, ptrace ABI, signal delivery, user access helpers, scheduler/task stack helpers, architecture syscall helpers, vDSO sigreturn detection, and memory-tag untagging through `untagged_addr()`.

## Risks And Edge Cases

- Range validation must catch overflow and zero-length invalid regions. Inclusive mode intentionally stores a negative length, so maintenance must preserve the wraparound semantics in the fast-path comparison.
- The selector address is checked with `access_ok()` at configuration time, but each dispatch still uses `__get_user()` and handles faults.
- Tracers configuring tagged tracees need the selector address untagged for access checks.
- Failing to call `syscall_rollback()` before `SIGSYS` would expose partially committed syscall-entry state to the signal handler.
- Invalid selector byte values deliberately kill with `SIGSYS`.

## Test Signals

Exercise prctl off/exclusive/inclusive modes, overflow and zero-length validation, selector allow/block/fault/invalid-byte behavior, ptrace get/set ABI, vDSO sigreturn exemption, syscall rollback visible in signal handlers, tagged-address selector setup, and interactions with seccomp/audit/syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/syscall_user_dispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/virt.c -->
# sources/distributed-fs/ceph-client/kernel/entry/virt.c

## Purpose

`virt.c` handles generic pending work before transferring execution into a virtual guest, such as KVM guest mode. It lets the outer guest loop service signals, rescheduling, notify-resume work, and architecture-specific guest-transfer work before entering the guest.

## Important APIs, Types, And Functions

- `xfer_to_guest_mode_work()` loops over `XFER_TO_GUEST_MODE_WORK` thread flags.
- `xfer_to_guest_mode_handle_work()` is the exported public entry point for virtualization code.
- It calls `schedule()`, `resume_user_mode_work(NULL)`, and `arch_xfer_to_guest_mode_handle_work(ti_work)`.

## Control Flow

`xfer_to_guest_mode_handle_work()` reads thread flags with interrupts and preemption already enabled. If no guest-transfer work is pending it returns zero. Otherwise it calls the internal loop. The loop returns `-EINTR` immediately for pending signals or notify-signal work, schedules for resched flags, handles notify-resume work, delegates architecture-specific work, and rereads flags until no guest-transfer work remains. Any nonzero architecture return is propagated.

## State And Persistence Behavior

No persistent state is owned here. The function services per-task thread flags, scheduler state, resume-user-mode callbacks, and architecture-specific guest-entry state.

## Dependencies And Integration Points

It integrates with `entry-virt.h`, KVM or other virtualization outer loops, scheduler rescheduling, signal/notify flags, resume-user-mode work, and architecture-specific guest transfer hooks. It is exported GPL for virtualization users.

## Risks And Edge Cases

- Callers must enter with interrupts and preemption enabled as documented; the inner KVM loop checks pending work with interrupts disabled but this handler services it outside that context.
- Signals are prioritized with `-EINTR` so guest entry can be aborted cleanly.
- Architecture hooks can impose additional failure modes that must be propagated to the virtualization caller.

## Test Signals

Use KVM guest-entry tests with pending signals, lazy and normal reschedule flags, notify-resume work, architecture hook failures, and repeated flag changes while the loop runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/entry/virt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/Makefile -->
# sources/distributed-fs/ceph-client/kernel/events/Makefile

## Purpose

This Makefile selects perf event subsystem objects for the kernel events directory. The listed file in this work item builds core perf event support, the ring buffer, callchain handling, and optional hardware breakpoint/uprobe support.

## Important APIs, Types, And Functions

- `obj-y := core.o ring_buffer.o callchain.o` always builds the main perf event components for this directory.
- `obj-$(CONFIG_HAVE_HW_BREAKPOINT) += hw_breakpoint.o` includes hardware breakpoint support when the architecture supports it.
- `obj-$(CONFIG_HW_BREAKPOINT_KUNIT_TEST) += hw_breakpoint_test.o` includes KUnit tests for hardware breakpoints.
- `obj-$(CONFIG_UPROBES) += uprobes.o` includes uprobes integration.

## Control Flow

Kbuild evaluates configuration symbols and includes the matching objects. `callchain.o` is always part of the directory build, which makes the callchain research in this work item part of the core perf event build.

## State And Persistence Behavior

The Makefile has no runtime state. It determines which objects are compiled into the kernel build.

## Dependencies And Integration Points

It integrates with Kbuild, perf events, ring buffers, architecture hardware breakpoint support, KUnit, and uprobes.

## Risks And Edge Cases

- Misconfigured object selection can omit required perf functionality or compile optional code without required architecture support.
- Optional KUnit test inclusion must remain guarded so production builds do not accidentally include test-only objects unless configured.

## Test Signals

Build with perf events, uprobes, hardware breakpoint, and KUnit hardware breakpoint configurations. Confirm object inclusion through build logs and run perf callchain, breakpoint, and uprobe tests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/callchain.c -->
# sources/distributed-fs/ceph-client/kernel/events/callchain.c

## Purpose

`callchain.c` manages perf callchain capture buffers and callchain sysctls. It allocates per-CPU, recursion-context-aware buffers usable from NMI context, coordinates lifetime across perf events, captures kernel and user callchains through weak architecture hooks, fixes uretprobe trampoline entries, and exposes sysctl limits for maximum stack depth and context markers.

## Important APIs, Types, And Functions

- `struct callchain_cpus_entries` stores an RCU head and a flexible per-CPU array of `struct perf_callchain_entry *` buffers.
- `sysctl_perf_event_max_stack` and `sysctl_perf_event_max_contexts_per_stack` define global callchain limits.
- `perf_callchain_entry__sizeof()` computes per-entry size from the sysctl stack and context limits.
- `callchain_recursion` is a per-CPU recursion guard indexed by `PERF_NR_CONTEXTS`.
- `nr_callchain_events`, `callchain_mutex`, and `callchain_cpus_entries` manage buffer lifetime.
- Weak hooks `perf_callchain_kernel()` and `perf_callchain_user()` are implemented by architectures.
- `alloc_callchain_buffers()` and `release_callchain_buffers()` allocate and RCU-free per-CPU callchain buffers.
- `get_callchain_buffers()` and `put_callchain_buffers()` reference-count global buffers for perf events.
- `get_callchain_entry()` and `put_callchain_entry()` acquire/release a per-CPU buffer for the current recursion context.
- `fixup_uretprobe_trampoline_entries()` replaces uretprobe trampoline addresses with original return addresses.
- `get_perf_callchain()` captures a kernel and/or user callchain into a reusable entry.
- `perf_event_max_stack_handler()` updates sysctls only when no callchain events are active.
- `init_callchain_sysctls()` registers the `kernel.perf_event_max_stack` and `kernel.perf_event_max_contexts_per_stack` sysctls.

## Control Flow

Perf events call `get_callchain_buffers()` when they need callchains. Under `callchain_mutex`, the event count increments, per-event max-stack requests are rejected with `-EOVERFLOW` when above the global cap, and the first event allocates buffers. Allocation creates one top-level `callchain_cpus_entries` object sized for `nr_cpu_ids` and then one buffer per possible CPU sized for all recursion contexts. Releasing decrements the count, and the final put swaps the global pointer to NULL and frees buffers after an RCU grace period.

`get_callchain_entry()` obtains a recursion context from the per-CPU guard. If no context is available or global buffers are missing, it returns NULL after cleanup. Otherwise it returns the current CPU's buffer slice for that recursion context. `get_perf_callchain()` initializes a context wrapper, optionally stores kernel/user context markers, invokes the architecture kernel hook when requested and not already in user mode, then handles user callchain capture unless cross-task user-only capture was requested. For deferred user stacks, it stores `PERF_CONTEXT_USER_DEFERRED` and the cookie instead of walking the user stack.

After a user walk, `fixup_uretprobe_trampoline_entries()` scans newly added user IPs and replaces uretprobe trampoline addresses with pending return-instance original return addresses. Sysctl writes are staged through a temporary table; writes are accepted only while no callchain events are active, preventing buffer-size changes under active users.

## State And Persistence Behavior

Runtime state includes global sysctl variables, per-CPU recursion bytes, an atomic active-event count, mutex-protected buffer lifetime, RCU-protected buffer pointers, and per-task uprobe return instances inspected during fixup. Sysctl values persist during the kernel runtime and affect future buffer sizing; buffer allocations persist while at least one callchain event is active.

## Dependencies And Integration Points

The file depends on perf event internals, architecture callchain walkers, NMI-safe buffer access, per-CPU APIs, RCU, mutexes, sysctl registration, scheduler task stack helpers, uprobes, recursion guards, and context marker constants such as `PERF_CONTEXT_KERNEL`, `PERF_CONTEXT_USER`, and `PERF_CONTEXT_USER_DEFERRED`.

## Risks And Edge Cases

- Buffers are manually per-CPU allocated because normal percpu allocation is not suitable for NMI access; freeing must be RCU-delayed.
- Sysctl writes while events are active are rejected with `-EBUSY` to prevent buffer-size mismatch.
- `get_callchain_buffers()` increments the event count before validation and must decrement on errors.
- Cross-task user-only callchains are rejected because user stacks are not supported for that mode.
- Recursion guard exhaustion returns NULL and avoids corrupting nested callchain captures.
- Uretprobe fixup assumes pending return instances correspond to encountered trampoline addresses in order.

## Test Signals

Use perf record/report callchains for kernel-only, user-only, mixed, and deferred user stacks; stress NMI sampling; test nested perf contexts; change sysctls before and during active callchain events; validate `-EOVERFLOW` for per-event stack requests above the cap; run uretprobe return-probe callchain tests; and use KASAN/KCSAN/RCU debug builds to catch lifetime or concurrency errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/callchain.c -->
