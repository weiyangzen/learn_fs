# File Research: sources/cow-pools/openzfs/module/zfs/abd.c

## Scope

Implements ARC Buffer Data abstraction shared by ARC/ZIO consumers: linear ABDs, scattered ABDs, gang ABDs, offset views, buffer ownership conversion, single-ABD and dual-ABD iteration, copy/compare/zero helpers, and RAID-Z iteration helpers.

## APIs And Behavior

- Allocation/lifetime: `abd_alloc()`, `abd_alloc_linear()`, `abd_alloc_sametype()`, `abd_alloc_gang()`, `abd_free()`, `abd_alloc_struct()`, and `abd_free_struct()`.
- Gang support: `abd_gang_add()`, `abd_gang_get_offset()`, and internal gang freeing/splicing let multiple ABDs be viewed as one logical ABD, with duplicate link wrappers when one ABD participates in multiple gang ABDs.
- Offset/view support: `abd_get_offset()`, `abd_get_offset_size()`, and `abd_get_offset_struct()` create child ABDs sharing underlying storage, with debug refcounts on parents.
- Buffer wrappers: `abd_get_from_buf()`, `abd_get_from_buf_struct()`, `abd_to_buf()`, `abd_release_ownership_of_buf()`, and `abd_take_ownership_of_buf()` handle linear wrappers and ownership transfer.
- Iteration: `abd_iterate_func()`, Linux kernel `abd_iterate_page_func()`, and `abd_iterate_func2()` map/unmap segments across linear, scatter, and gang layouts.
- Data operations: `abd_copy_to_buf_off()`, `abd_copy_from_buf_off()`, `abd_copy_off()`, `abd_cmp_buf_off()`, `abd_cmp()`, `abd_zero_off()`, and `abd_cmp_zero_off()`.
- RAID-Z helpers: `abd_raidz_gen_iterate()` and `abd_raidz_rec_iterate()` provide bounded mapped segments to parity generation/reconstruction callbacks.
- `abd_verify()` enforces layout, flag, parent, child, and gang invariants under debug builds.

## State And Dependencies

The file manipulates `abd_t` flags, size, parent/child debug refcounts, gang list links, mutexes, linear buffers, scatter chunks, and platform-provided ABD iterator operations. It depends on zio buffer allocators, scatter chunk alloc/free/stat helpers from ABD platform code, `list_t`, `zfs_refcount`, and RAID-Z callback contracts.

## Risks And Invariants

ABD ownership flags decide whether underlying memory is freed; incorrect ownership transfer can leak or double-free zio buffers. Offset ABDs must not outlive parents. Gang ABD links are protected by child `abd_mtx` because one ABD can appear in multiple gang aggregations through wrapper ABDs. Iteration code must progress across gang boundaries and unmap every mapped segment, including error exits. RAID-Z iteration assumes segment sizes are progressive and 512-byte aligned except at valid boundaries.
