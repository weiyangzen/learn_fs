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
