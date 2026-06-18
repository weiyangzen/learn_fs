<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.h -->
# sources/distributed-fs/ceph-client/io_uring/memmap.h

## Purpose
`memmap.h` declares io_uring memory-region mapping APIs and special mmap offset constants for parameter and zero-copy receive regions. It also provides inline helpers for inspecting and publishing `io_mapped_region` objects.

## Important APIs, Types, and Functions
- `IORING_MAP_OFF_PARAM_REGION`, `IORING_MAP_OFF_ZCRX_REGION`, and `IORING_OFF_ZCRX_SHIFT` define additional mmap offset classes beyond core rings and pbuf rings.
- `io_pin_pages()` pins userspace pages for fixed regions.
- `io_uring_get_unmapped_area()` and `io_uring_mmap()` are file operation hooks.
- `io_free_region()` and `io_create_region()` manage region lifecycle.
- `io_region_get_ptr()`, `io_region_is_set()`, `io_region_publish()`, and `io_region_size()` expose common region operations.

## Control Flow
Callers create a local `io_mapped_region` with `io_create_region()`, access the kernel pointer with `io_region_get_ptr()`, and publish it to a context-visible destination with `io_region_publish()` when mmap lookup may need to see it. `io_region_publish()` takes `ctx->mmap_lock` before copying the region because mmap lookup may run with only that lock rather than `uring_lock`.

## State and Persistence Behavior
The header treats `nr_pages` as the indicator that a region is set and derives byte size from `nr_pages << PAGE_SHIFT`. Publishing copies the entire region struct; after publication, the destination owns the page pointers and mapping state.

## Dependencies and Integration Points
It is consumed by `io_uring.c`, `kbuf.c`, `memmap.c`, and zcrx-related code. It relies on `struct io_ring_ctx`, `struct io_mapped_region`, and UAPI `io_uring_region_desc` definitions from the broader io_uring type headers.

## Risks and Edge Cases
- `io_region_publish()` is a shallow struct copy; callers must avoid freeing the source as an owner after publishing unless ownership is explicitly transferred.
- `io_region_is_set()` only checks `nr_pages`, so partially initialized regions must be cleaned with `io_free_region()`.
- Offset constants must remain disjoint from other mmap classes.

## Test Signals
Build and runtime signals should verify region publication under mmap races, correct size calculations, and mmap offset dispatch for parameter/zcrx/pbuf/ring regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/memmap.h -->
