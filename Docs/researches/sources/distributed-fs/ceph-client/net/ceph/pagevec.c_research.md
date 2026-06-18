# sources/distributed-fs/ceph-client/net/ceph/pagevec.c

## Purpose
`pagevec.c` provides small exported helpers for allocating, releasing, dirtying, copying from, and zeroing vectors of `struct page *` used by Ceph message payloads and replies.

## Important APIs, types, and functions
- `ceph_alloc_page_vector()` allocates an array of page pointers and fills it with newly allocated page-cache pages.
- `ceph_release_page_vector()` frees pages that were allocated by Ceph and then frees the pointer array.
- `ceph_put_page_vector()` drops caller-held page references and optionally marks pages dirty before `put_page()`.
- `ceph_copy_from_page_vector()` copies bytes from a page vector into a linear buffer starting at a page-relative offset.
- `ceph_zero_page_vector_range()` zeros a byte range spanning one or more pages.

## Control flow
Allocation first creates the pointer array, then loops page-by-page. If any page allocation fails, it releases the pages already allocated and returns `ERR_PTR(-ENOMEM)`. Copying and zeroing both compute page offset from the caller-provided range, then walk pages until the byte count is exhausted. Dirty release loops pages and calls `set_page_dirty_lock()` before `put_page()` when requested.

## State and persistence behavior
The vector is in-memory ownership state only. Callers choose between freeing allocated pages (`ceph_release_page_vector()`) and putting referenced pages (`ceph_put_page_vector()`). Zeroing mutates page contents, and dirtying marks pages for writeback through normal kernel page-cache mechanisms.

## Dependencies and integration points
This file depends on Linux page allocation, page dirtying, `zero_user_segment()`, and Ceph allocation helpers. `osd_client.c` uses it for reply buffers, notify IDs, list-watchers, copy-from payload pages, and sparse/read data buffers. Higher CephFS code uses page vectors for file IO paths.

## Risks and edge cases
- Callers must use the correct release function for owned allocated pages versus referenced page-cache pages.
- `ceph_copy_from_page_vector()` starts from `pages[0]` plus `off & ~PAGE_MASK`; it expects the page vector itself to already be aligned to the logical range.
- Zeroing and copying assume the range fits the provided vector; there is no local bounds check.
- `page_address()` requires pages that are directly addressable in this kernel configuration.

## Test signals
Exercise partial-first-page copy, full-page copy, multi-page copy, leading and trailing zero ranges, allocation failure cleanup, dirty versus non-dirty put behavior, and ownership handoff from OSD reply paths.
