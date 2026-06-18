# sources/distributed-fs/ceph-client/include/linux/kmsan.h

## Purpose

`kmsan.h` is the primary subsystem API for Kernel Memory Sanitizer. It declares task, page, slab, vmalloc, ioremap, DMA, USB, entry-regs, metadata, and per-task enable/disable hooks used to maintain initialization shadow/origin state. The source was read as a complete 411-line file.

## Important APIs, Types, and Functions

Key APIs include `kmsan_task_create()`, `kmsan_task_exit()`, `kmsan_init_shadow()`, `kmsan_init_runtime()`, `kmsan_memblock_free_pages()`, `kmsan_alloc_page()`, `kmsan_free_page()`, `kmsan_copy_page_meta()`, `kmsan_slab_alloc()`, `kmsan_slab_free()`, `kmsan_kmalloc_large()`, `kmsan_kfree_large()`, `kmsan_vmap_pages_range_noflush()`, `kmsan_vunmap_range_noflush()`, `kmsan_ioremap_page_range()`, `kmsan_iounmap_page_range()`, `kmsan_handle_dma()`, `kmsan_handle_dma_sg()`, `kmsan_handle_urb()`, `kmsan_unpoison_entry_regs()`, `kmsan_get_metadata()`, `kmsan_enable_current()`, `kmsan_disable_current()`, `memset_no_sanitize_memory()`, and `KMSAN_WARN_ON()`.

## Control Flow

Boot initializes shadow metadata, then allocator and mapping paths notify KMSAN as memory changes ownership. DMA and USB hooks check outgoing buffers and initialize incoming buffers. Entry code unpoisons register frames. Runtime sections can temporarily disable KMSAN for the current task and re-enable it with nested depth accounting.

## State and Persistence Behavior

KMSAN maintains shadow and origin metadata for kernel memory and per-task context. `kmsan_enabled` and `panic_on_kmsan` control runtime behavior. Disabled builds stub hooks and return success.

## Dependencies and Integration Points

It integrates with page allocator, slab, vmalloc/ioremap, DMA API, scatterlists, USB URBs, low-level entry, and LLVM/MSan instrumentation.

## Risks and Edge Cases

Must-check return values on metadata mapping paths are important; missed failures break sanitizer correctness. DMA direction handling must match hardware ownership. Nested `kmsan_disable_current()`/`kmsan_enable_current()` pairs must balance. `KMSAN_WARN_ON()` may disable KMSAN or BUG based on policy.

## Test Signals

KMSAN boot and runtime selftests, allocator poisoning tests, DMA direction tests, USB transfer tests, vmalloc/ioremap metadata mapping tests, balanced disable/enable tests, and disabled-config builds are important.
