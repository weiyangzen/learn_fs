# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iova_bitmap.c

## Purpose
`iova_bitmap.c` implements a helper for setting bits in a userspace bitmap that represents an IOVA range. It is used by dirty tracking and similar report paths that need to mark arbitrary IOVA subranges without permanently pinning an entire large bitmap.

## Important APIs, Types, And Functions
The exported namespace APIs are `iova_bitmap_alloc()`, `iova_bitmap_free()`, `iova_bitmap_for_each()`, and `iova_bitmap_set()`. Internal `struct iova_bitmap` tracks the full IOVA range, userspace bitmap pointer, mapped word indices, and current `struct iova_bitmap_map`. The map stores the currently pinned user pages, base IOVA, length, page granularity shift, page offset, and page count.

## Control Flow
Allocation records the base IOVA, length, bit granularity, total u64 word count, and allocates one page for `struct page *` pointers. `iova_bitmap_for_each()` currently invokes the callback once for the full range, while `iova_bitmap_set()` lazily pins the bitmap window containing the requested IOVA range. If the set spans outside the pinned window, it advances, unpins old pages, pins the next pages, and continues setting bits through `kmap_local_page()` and `bitmap_set()`.

## State And Persistence
Only the bitmap object and transient pinned user pages persist across calls. The user-visible persistent result is the modified userspace bitmap. `iova_bitmap_put()` releases pinned pages, and `iova_bitmap_free()` unpins, frees the pointer page, and frees the object.

## Dependencies And Integration Points
The helper depends on GUP (`pin_user_pages_fast()`), highmem local mappings, and kernel bitmap operations. It exports symbols in the `IOMMUFD` namespace for use by dirty tracking code.

## Risks And Test Signals
Risks concentrate around arithmetic: bitmap byte-vs-u64 indexing, unaligned userspace bitmap addresses, page-window rollover, range-end overflow, and silently returning from `iova_bitmap_set()` if advancing fails. Tests should include unaligned bitmap pointers, multi-window dirty ranges, end-of-range ranges, different page sizes, partial final words, GUP failure injection, and verification that all pinned pages are released.
