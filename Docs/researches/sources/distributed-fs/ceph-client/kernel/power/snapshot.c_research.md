# sources/distributed-fs/ceph-client/kernel/power/snapshot.c

## Purpose
Builds, streams, loads, and restores the in-memory hibernation image used by swsusp. It tracks which physical pages must be saved, copies saveable memory into image pages, serializes image metadata as PFN bitmaps, allocates safe restore memory, and performs final page restoration support including highmem handling.

## Important APIs, Types, and Functions
Public/shared entry points include `hibernate_reserved_size_init()`, `hibernate_image_size_init()`, `get_safe_page()`, `register_nosave_region()`, `swsusp_set_page_free()`, `swsusp_unset_page_free()`, `swsusp_page_is_forbidden()`, `create_basic_memory_bitmaps()`, `free_basic_memory_bitmaps()`, `clear_or_poison_free_pages()`, `snapshot_additional_pages()`, `hibernate_preallocate_memory()`, `swsusp_save()`, `snapshot_get_image_size()`, `snapshot_read_next()`, `snapshot_write_next()`, `snapshot_write_finalize()`, `snapshot_image_loaded()`, and `restore_highmem()`.

Key types are `struct pbe`, `struct linked_page`, `struct chain_allocator`, `struct memory_bitmap`, `struct mem_zone_bm_rtree`, `struct rtree_node`, `struct bm_position`, `struct nosave_region`, and highmem-only `struct highmem_pbe`. Global image state includes `restore_pblist`, `safe_pages_list`, `buffer`, `allocated_unsafe_pages`, `forbidden_pages_map`, `free_pages_map`, `orig_bm`, `copy_bm`, `zero_bm`, `nr_copy_pages`, `nr_meta_pages`, `nr_zero_pages`, `alloc_normal`, and `alloc_highmem`.

## Control Flow
Before hibernation, `create_basic_memory_bitmaps()` creates two memory bitmaps and marks nosave ranges. `hibernate_preallocate_memory()` creates `orig_bm`, `copy_bm`, and `zero_bm`, marks free pages, counts saveable data/highmem pages, estimates metadata overhead and minimum image size, preallocates image pages under `image_size` and `reserved_size` constraints, and frees unnecessary pages.

During the architecture snapshot, `swsusp_save()` computes available normal/highmem pages, calls `swsusp_alloc()` to allocate copy pages, then `copy_data_pages()` copies saveable pages into allocated image pages while marking original PFNs, copy PFNs, and zero pages. The image is later streamed out through `snapshot_read_next()`: first a `struct swsusp_info` header, then metadata pages packed by `pack_pfns()`, then copied data pages.

During resume, `snapshot_write_next()` receives that stream. It loads and validates the header, builds copy and zero bitmaps from metadata pages, calls `prepare_image()` to mark unsafe original PFNs and allocate safe restore storage, then returns buffers where the caller should place each image page. It skips zero pages by clearing them directly. `snapshot_write_finalize()` drains trailing zero pages, copies pending highmem data, protects restored pages when strict RWX protection is enabled, and recycles bitmap memory.

For final atomic restore, `restore_highmem()` swaps highmem copy pages back to original pages when the direct restore path cannot overwrite them immediately. Lowmem final restore is completed by architecture code using `restore_pblist`.

## State and Persistence Behavior
All state is runtime memory used for one hibernation/resume attempt. The serialized image format is persistent while stored by `swap.c`: header, PFN metadata pages, and data pages. `register_nosave_region()` records boot-time PFN ranges that must not enter the image. `image_size` and `reserved_size` are initialized here but exposed through hibernation sysfs.

## Dependencies and Integration Points
This file depends on MM zones, memblock, highmem, page flags, direct-map/set_memory helpers, architecture hibernation headers, TLB/cache maintenance, debug pagealloc, freezer/suspend orchestration, and swap/user snapshot readers. It is the memory engine behind `hibernate.c`, `swap.c`, and `/dev/snapshot`.

## Risks
Risks are severe: bitmap off-by-one errors, PFN validation mistakes, unsafe-page allocation during restore, highmem copy-list corruption, image-size underestimation, failure to exclude nosave/free pages, missed cache/TLB maintenance, strict RWX protection not undone correctly on errors, and memory pressure deadlocks during atomic phases. Resume image loading must reject mismatched kernel/memory metadata to avoid corrupting the running kernel.

## Test Signals
Run hibernation on lowmem and highmem systems, with zero-heavy memory, memory hotplug-like layouts, strict RWX image protection, debug pagealloc, and constrained free memory. Validate `image_size` and `reserved_size` tuning, nosave-region registration, `/dev/snapshot` read/write streaming, CRC/compressed and uncompressed swap paths, and injected allocation failures around bitmap creation and safe-page allocation.
