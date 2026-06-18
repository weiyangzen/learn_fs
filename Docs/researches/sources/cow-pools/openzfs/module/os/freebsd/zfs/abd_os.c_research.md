# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/abd_os.c

## Scope

FreeBSD implementation of ARC Buffered Data OS primitives. It allocates and accounts for linear/scatter ABDs, wraps user pages for direct I/O, maps/unmaps ABD chunks, provides kstats, and supports borrow/return buffer operations for GEOM and other consumers.

## Main Interfaces

- Allocation/accounting: `abd_size_alloc_linear()`, `abd_alloc_chunks()`, `abd_free_chunks()`, `abd_alloc_struct_impl()`, `abd_free_struct_impl()`.
- Stats lifecycle: `abd_init()`, `abd_fini()`, `abd_update_scatter_stats()`, `abd_update_linear_stats()`, `abd_kstats_update()`.
- Zero/scatter support: `abd_alloc_zero_scatter()` and `abd_free_zero_scatter()`.
- Direct-I/O page wrapping: `abd_alloc_from_pages()`, `abd_get_offset_scatter()`, `abd_get_offset_from_pages()`.
- Iteration: `abd_iter_init()`, `abd_iter_at_end()`, `abd_iter_advance()`, `abd_iter_map()`, `abd_iter_unmap()`.
- Raw buffer borrowing: `abd_borrow_buf()`, `abd_borrow_buf_copy()`, `abd_return_buf()`, `abd_return_buf_copy()`.

## State And Control Flow

Scatter ABDs are page-chunk arrays allocated from `abd_chunk_cache`. Linear ABDs are used for small allocations or when scatter is disabled. `abd_zero_scatter` represents a full `SPA_MAXBLOCKSIZE` zero ABD by pointing every chunk at `zero_region`, avoiding per-page zero allocations.

`abd_alloc_from_pages()` can create a linear-page ABD for single-page user buffers or a scatter ABD whose chunks point directly at `vm_page_t` user pages. Iteration maps linear data directly, maps user pages through `zfs_map_page()`, or uses kernel-addressed scatter chunks without mapping.

Borrowing returns a direct pointer for linear ABDs and temporary `zio_buf` storage for scatter/gang ABDs; copy variants move contents in or out.

## Dependencies

Depends on ARC space accounting, kstats/wmsums, FreeBSD VM page mapping, `kmem_cache`, ZIO buffer allocation, ABD core helpers, and direct-I/O UIO page state.

## Correctness Notes

Scatter waste is charged to ARC via `ARC_SPACE_ABD_CHUNK_WASTE`. ABDs created from user pages must not free their underlying pages. Debug return checks intentionally avoid asserting unchanged direct-I/O read pages because user space may mutate them; ZIO checksums are expected to catch that.
