# sources/distributed-fs/ceph-client/mm/kmsan/hooks.c

## Purpose
`hooks.c` connects KMSAN to kernel subsystems that allocate, free, map, copy, or hand memory to devices/userspace. It turns allocator and I/O lifecycle events into shadow/origin updates and explicit checks for information leaks.

## Important APIs, Types, And Functions
Task hooks are `kmsan_task_create()` and `kmsan_task_exit()`. Slab and large allocation hooks are `kmsan_slab_alloc()`, `kmsan_slab_free()`, `kmsan_kmalloc_large()`, and `kmsan_kfree_large()`. Vmalloc/ioremap metadata mapping is handled by `kmsan_vunmap_range_noflush()`, `kmsan_ioremap_page_range()`, and `kmsan_iounmap_page_range()`. Transfer hooks include `kmsan_copy_to_user()`, `kmsan_memmove()`, `kmsan_handle_urb()`, `kmsan_handle_dma()`, and `kmsan_handle_dma_sg()`. Public explicit APIs include `kmsan_poison_memory()`, `kmsan_unpoison_memory()`, `kmsan_unpoison_entry_regs()`, `kmsan_check_memory()`, `kmsan_enable_current()`, and `kmsan_disable_current()`.

## Control Flow
Allocation paths poison newly allocated memory unless `__GFP_ZERO` initializes it; free paths poison memory with the UAF bit set, except RCU-safe or constructor-backed slabs where reuse semantics make that unsafe. I/O mappings allocate and map shadow/origin pages in the vmalloc metadata ranges and unwind partial failures. `copy_to_user` checks only bytes actually copied, reporting `REASON_COPY_TO_USER`; if an architecture allows kernel addresses through this path, metadata is copied instead. DMA and USB hooks check outgoing buffers, unpoison incoming buffers, and do both for bidirectional transfers. Runtime guards prevent most hooks from recursing into instrumented code.

## State And Persistence
The hooks update persistent shadow/origin metadata owned by pages, slabs, vmalloc areas, and DMA-visible buffers. `kmsan_disable_current()` and `kmsan_enable_current()` manipulate the current task context depth to suppress or re-enable reporting in selected regions.

## Dependencies And Integration Points
This file integrates with slab internals, page allocation, vmalloc/vmap/ioremap internals, USB URBs, DMA directions and scatterlists, copy-to-user paths, user access save/restore, and KMSAN core metadata functions. It relies on the runtime being compiled without instrumentation because hooks may run in allocator and fault-sensitive paths.

## Risks
Incorrect hook gating can miss initialization events or recurse into KMSAN. Constructor and `SLAB_TYPESAFE_BY_RCU` handling trades UAF detection for valid kernel reuse patterns. Ioremap cleanup must avoid leaking metadata pages or leaving stale vmalloc mappings. DMA handling ignores highmem physical addresses, which avoids unsafe direct mapping assumptions but can reduce coverage. Copy-to-user checks happen after copying because the actual copied byte count is only known afterward.

## Test Signals
KUnit cases exercise kmalloc/kzalloc, large page UAF, vmalloc/vmap initialization, percpu propagation, explicit poison/unpoison/check calls, and copy-from-kernel nofault behavior. Integration signals also come from USB and DMA paths producing `kernel-infoleak`-style KMSAN reports when uninitialized data is submitted outward.
