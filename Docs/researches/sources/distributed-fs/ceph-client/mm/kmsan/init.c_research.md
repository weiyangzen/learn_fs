# sources/distributed-fs/ceph-client/mm/kmsan/init.c

## Purpose
`init.c` prepares KMSAN metadata during early boot and enables the runtime once enough memory infrastructure exists. It records boot-time ranges needing metadata, allocates shadow/origin pages for reserved and kernel data ranges, and coordinates metadata allocation while memblock pages are released to the buddy allocator.

## Important APIs, Types, And Functions
`struct start_end_pair` and `start_end_pairs[]` store future metadata ranges. `kmsan_record_future_shadow_range()` normalizes and merges those ranges. `kmsan_init_shadow()` records reserved memory, `.data`, and `NODE_DATA()` ranges, then calls `kmsan_init_alloc_meta_for_range()`. `struct metadata_page_pair held_back[]` stores held shadow/origin page blocks per order for eager metadata assignment. `kmsan_memblock_free_pages()` consumes every third memblock-free block as real memory and assigns the previous two blocks as metadata. `kmsan_memblock_discard()` and helper `smallstack` logic split leftovers and free usable thirds. `kmsan_init_runtime()` initializes the initial task, discards leftovers, logs warnings, and sets `kmsan_enabled`.

## Control Flow
Early boot records ranges before the page allocator is fully online. As memblock frees pages, KMSAN holds back two blocks for each order and uses them as shadow and origin for the third block via `kmsan_setup_meta()`. When memblock is about to disappear, leftover held blocks are collected from high to low order, repeatedly grouping triples into page/shadow/origin sets and splitting leftovers to smaller orders. Runtime starts only after this metadata bootstrap is complete.

## State And Persistence
Boot-only state uses `__initdata` arrays and stacks, which are discarded after initialization. Persistent state is page-to-shadow/origin associations installed by `kmsan_setup_meta()` and `kmsan_init_alloc_meta_for_range()`, plus the global `kmsan_enabled` flag set at runtime start.

## Dependencies And Integration Points
The file depends on memblock, reserved memory enumeration, NUMA node data, kernel section symbols, page allocator internals, and `shadow.c` metadata setup helpers. It is part of the architecture-specific KMSAN boot contract because every normal page needs corresponding shadow and origin storage before instrumentation can safely trust metadata.

## Risks
The eager 2/3 metadata allocation scheme is memory-expensive and boot-order-sensitive. `NUM_FUTURE_RANGES` bounds range tracking; overflow is a warning condition. Range merging is intentionally simple and assumes a small number of ranges. Incorrect held-back bookkeeping can either leak memory to metadata or release pages without metadata, causing later false reports or metadata faults.

## Test Signals
Boot logs `Starting KernelMemorySanitizer` and the production-use warning indicate runtime activation. Early boot warnings from KMSAN assertions, page metadata faults, or later metadata contiguity failures indicate initialization problems. KUnit page, vmalloc, and vmap tests indirectly validate this setup.
