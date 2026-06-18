# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/abd_os.c

## Purpose

Linux-specific ABD implementation. It backs ARC buffered data with either linear kernel buffers or scatterlists of Linux pages, supporting highmem, compound pages, direct-I/O user pages, BIO mapping, zero scatter buffers, and ABD kstats.

## Main Concepts

- Linear ABDs behave like normal contiguous virtual buffers.
- Scatter ABDs use physical pages in a Linux scatterlist and map chunks only during access.
- On non-highmem systems, a one-entry scatter ABD can be represented as a linear page-backed ABD for faster cached reads.
- ABDs created from user pages are marked with `ABD_FLAG_FROM_PAGES` and are handled carefully because user memory cannot be write-protected by ABD code.

## Main State

- `abd_stats`: named kstats template.
- `abd_sums`: writable sums backing stats.
- `zfs_abd_scatter_min_size`: minimum size for scatter allocation.
- `zfs_abd_scatter_max_order`: maximum compound-page order for scatter ABD allocation.
- `abd_zero_scatter`: SPA_MAXBLOCKSIZE scatter ABD backed by one zero page.
- `abd_zero_page`: shared zero page or allocated substitute.
- `abd_cache`: cache for `abd_t`.
- `abd_ksp`: abdstats kstat.

## Allocation

- `abd_alloc_struct_impl()` / `abd_free_struct_impl()`: allocate/free `abd_t` from cache and update struct-size stats.
- `abd_alloc_chunks()`: allocates pages for scatter ABDs.
  - Non-highmem path prefers high-order compound pages, tries to stay within a NUMA zone, and degrades allocation order on failure.
  - Highmem path allocates individual pages for maximum compatibility.
- `abd_free_chunks()`: unmarks and frees pages unless ABD is from caller-provided pages, then frees the scatter table.
- `abd_alloc_zero_scatter()` / `abd_free_zero_scatter()`: create and destroy shared zero-filled scatter ABD.
- `abd_size_alloc_linear()`: chooses linear allocation for small sizes or when scatter is disabled.
- `abd_alloc_from_pages()`: constructs an ABD over caller-provided pinned pages, representing single-page mappings as linear when possible.
- `abd_alloc_for_io()`: currently delegates to `abd_alloc()`.

## Stats And Initialization

- Tracks struct memory, linear count/bytes, scatter count/bytes, scatter chunk waste, allocation order distribution, multi-chunk/multi-zone ABDs, page allocation retries, and sg table retries.
- `abd_init()` creates the ABD cache, initializes sums, installs `zfs/abdstats`, and creates zero scatter.
- `abd_fini()` tears down zero scatter, kstats, sums, and cache.

## Iteration And Mapping

- `abd_iter_init()`: initializes an iterator for linear or scatter ABDs.
- `abd_iter_at_end()`: checks completion.
- `abd_iter_advance()`: advances through linear offset or scatterlist entries.
- `abd_iter_map()` / `abd_iter_unmap()`: maps the current chunk into kernel address space, using local kmap for scatter pages.
- `abd_iter_page()`: yields page pointer, data offset, and data length without mapping. It handles compound tail pages by moving to the compound head and expanding the yielded segment when possible.

## Buffer Borrowing

- `abd_borrow_buf()`: returns direct linear storage when safe, otherwise allocates a temporary zio buffer.
- `abd_borrow_buf_copy()`: borrows and copies ABD contents when needed.
- `abd_return_buf()`: validates or frees borrowed buffers, with special handling for gang ABDs and user-page ABDs.
- `abd_return_buf_copy()`: copies modified data back before returning the temporary buffer.

## BIO Mapping

- `abd_nr_pages_off()`: counts pages needed for a range, including gang ABD recursion.
- `bio_map()`: maps a linear virtual range into a BIO.
- `abd_gang_bio_map_off()`: maps gang ABD ranges across children.
- `abd_bio_map_off()`: maps linear, gang, or scatter ABD ranges into a Linux BIO.

## Tunables And Export

- Exports `abd_alloc_from_pages`.
- Module parameters:
  - `zfs_abd_scatter_enabled`
  - `zfs_abd_scatter_min_size`
  - `zfs_abd_scatter_max_order`

## Correctness Notes

Pages may be marked private on 64-bit builds so ZFS data pages can be excluded from crash dumps. Scatter allocation loops intentionally retry with sleeps when page or sg table allocation fails. Direct-I/O user page ABDs are not trusted to remain stable, so temporary buffers and checksum verification are used to catch concurrent user modifications.
