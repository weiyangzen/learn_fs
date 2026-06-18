<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.c -->
# sources/distributed-fs/ceph-client/io_uring/memmap.c

## Purpose
`memmap.c` owns io_uring mapped memory regions: pinning user-provided pages, allocating kernel-owned pages for rings and auxiliary regions, creating kernel virtual mappings, accounting memory, freeing regions, dispatching mmap offsets to the correct region, and supporting both MMU and NOMMU mappings.

## Important APIs, Types, and Functions
- `io_pin_pages()` pins a page-aligned user range with `FOLL_WRITE|FOLL_LONGTERM`.
- `io_create_region()` validates an `io_uring_region_desc`, accounts pages, either pins user pages or allocates kernel pages, initializes a kernel pointer, and returns a mmap offset for kernel-owned memory.
- `io_free_region()` releases pinned or allocated pages, unmaps vmap mappings, unaccounts memory, and clears the region.
- `io_uring_mmap()` maps ring, SQE, pbuf, parameter, or zcrx regions into userspace.
- `io_uring_get_unmapped_area()` provides cache-aliasing-aware placement for MMU builds and direct pointer return for NOMMU builds.
- `io_uring_nommu_mmap_capabilities()` advertises direct read/write mapping support on NOMMU.
- Internal helpers allocate compound or bulk pages, initialize direct/vmap pointers, resolve mmap offsets, and validate mmap requests.

## Control Flow
Region creation begins with `io_create_region()`. It rejects already initialized regions, nonzero reserved fields, unsupported flags, mismatched user-address flags, missing size, pre-set mmap offset/id, non-page-aligned address/size, oversized page counts, and address overflow. It accounts memory against `ctx->user` if needed, sets `nr_pages`, then either pins user pages via `io_region_pin_pages()` or allocates zeroed pages via `io_region_allocate_pages()`. Finally, `io_region_init_ptr()` uses direct page address when the pages coalesce into one lowmem folio, otherwise vmaps the pages.

Mmap requests enter `io_uring_mmap()` through ring file operations. Under `ctx->mmap_lock`, the code resolves `vma->vm_pgoff` with `io_mmap_get_region()`, validates the region is set and not user-provided, and inserts pages. SQ/CQ ring mappings may map a limited number of pages based on requested VMA size because SQ and CQ share the same backing region. For cache-color-sensitive architectures, `get_unmapped_area` rejects caller-specified addresses and asks the mm layer for an alias-coherent mapping based on the kernel pointer.

NOMMU mapping requires shared mappings with exact region size, pins pages with `get_page()` for the VMA lifetime, and releases those extra references in `io_uring_nommu_vm_close()`.

## State and Persistence Behavior
`struct io_mapped_region` stores `pages`, `nr_pages`, `ptr`, and internal flags for vmap, user-provided pages, and single-ref compound allocation. Regions persist in `io_ring_ctx` (`ring_region`, `sq_region`, `param_region`) or subsidiary structures such as pbuf lists and zcrx contexts. Memory accounting is tied to `ctx->user` and reversed on free.

## Dependencies and Integration Points
This module integrates with `kbuf.c` through pbuf ring mmap offsets, with `rsrc.c` through coalesced buffer/page helpers and memory accounting, with `zcrx` through zero-copy receive regions, and with `io_uring.c` for ring/SQE region creation and file operations. It depends on mm APIs, GUP pinning, page allocation, vmap/vunmap, `vm_insert_pages()`, NOMMU VMA hooks, and architecture SHM coloring.

## Risks and Edge Cases
- Long-term user page pins must be fully released on partial failure; `io_pin_pages()` handles partial GUP by unpinning.
- User-provided regions are deliberately not mmap-able through the ring fd to avoid aliasing rule violations.
- Compound allocations use `IO_REGION_F_SINGLE_REF`, so free paths must release only one page ref in that case.
- `io_region_pin_pages()` currently returns `-EFAULT` without freeing `pages` if a WARN detects an unexpected page count mismatch; this is theoretically unreachable because page count was derived from the same size.
- Mmap offset dispatch shares bit ranges with pbuf/zcrx ids; incorrect shifts/masks map the wrong region.
- Cache aliasing on SHM-colored architectures can break if callers bypass `get_unmapped_area()` semantics.

## Test Signals
Tests should cover setup mmap of SQ/CQ/SQEs, `IORING_SETUP_NO_MMAP` user-provided regions, invalid descriptors/reserved fields/alignment/overflow, pbuf ring mmap offsets, zcrx region offsets when enabled, memory accounting failure, mmap after unregister, NOMMU exact-size/shared rules, and teardown unmapping with active VMAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.c -->
