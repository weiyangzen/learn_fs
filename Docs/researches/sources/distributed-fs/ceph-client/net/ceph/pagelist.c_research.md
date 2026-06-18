# sources/distributed-fs/ceph-client/net/ceph/pagelist.c

## Purpose
`pagelist.c` implements `struct ceph_pagelist`, a reference-counted list of pages used as a growable encoded byte buffer for Ceph messages. It is used when request metadata or payload fragments need to be appended incrementally without requiring one contiguous allocation.

## Important APIs, types, and functions
- `ceph_pagelist_alloc()` allocates and initializes the page list, free reserve list, length/room counters, mapped tail pointer, and refcount.
- `ceph_pagelist_release()` drops a reference, unmaps the tail page, frees all active pages, frees reserved pages, and releases the container.
- `ceph_pagelist_append()` appends bytes across page boundaries, allocating or consuming reserved pages as needed.
- `ceph_pagelist_reserve()` preallocates enough pages to satisfy a future append without allocation.
- `ceph_pagelist_free_reserve()` frees all unused reserved pages.
- `ceph_pagelist_addpage()` and `ceph_pagelist_unmap_tail()` are internal helpers for page management and `kmap()`/`kunmap()` state.

## Control flow
Allocation starts with an empty active page list and zero room, so the first append enters the while loop, copies zero bytes if no room is available, calls `ceph_pagelist_addpage()`, maps the new page, and then copies data to `mapped_tail`. Longer appends copy up to the current room, allocate a new page when room is insufficient, and continue until all bytes are appended.

Reservation computes the number of pages beyond current room needed for a future byte count and fills `free_list` with `__page_cache_alloc(GFP_NOFS)` pages. `ceph_pagelist_addpage()` prefers reserved pages before allocating. Release unmaps any mapped tail before freeing active pages, then frees reserves.

## State and persistence behavior
The pagelist is strictly in-memory. Persistent state consists only of `length`, `room`, active page order, reserve page count, and the currently mapped tail address. The active pages store encoded wire data until the owning Ceph message consumes or releases the pagelist. Reference counting allows multiple users to retain the same pagelist, as seen in notify resend paths.

## Dependencies and integration points
The file depends on Linux page allocation, highmem mapping, list manipulation, and Ceph pagelist declarations. Inline encoding helpers in `pagelist.h` build on `ceph_pagelist_append()`. `osd_client.c` uses pagelists for class request info, xattr payloads, notify payloads, notify ACKs, and other encoded request data.

## Risks and edge cases
- `ceph_pagelist_append()` assumes `mapped_tail` is valid once nonzero data is copied; callers rely on `ceph_pagelist_addpage()` before the final copy when room was initially insufficient.
- Pointer arithmetic on `const void *buf` is a GNU C kernel extension.
- Highmem mappings must be balanced; forgetting `ceph_pagelist_unmap_tail()` would leak mappings.
- Reserve accounting must stay exact; `BUG_ON(pl->num_pages_free)` catches mismatches only at reserve-free time.
- Allocation uses `GFP_NOFS`, appropriate for filesystem paths but still failure-prone under memory pressure.

## Test signals
Tests should cover zero-length append, single-page append, cross-page append, append after reserve, reserve larger than room, release with mapped tail, release with active and reserved pages, reference count retention, and encoded integer/string helpers from `pagelist.h`.
