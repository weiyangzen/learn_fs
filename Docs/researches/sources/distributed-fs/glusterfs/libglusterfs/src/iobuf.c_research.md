# sources/distributed-fs/glusterfs/libglusterfs/src/iobuf.c

## Purpose
`iobuf.c` implements GlusterFS' reusable I/O buffer allocator and `iobref` reference container. It supplies page-sized buffers for network and storage paths, amortizes allocations through mmap-backed arenas for larger buffers, uses direct allocation for small or oversized requests, and exposes statedump metrics for active/passive arena state.

## Important APIs, Types, And Functions
The public API from `glusterfs/iobuf.h` includes `iobuf_pool_new()`, `iobuf_pool_destroy()`, `iobuf_get()`, `iobuf_get2()`, `iobuf_get_page_aligned()`, `iobuf_ref()`, `iobuf_unref()`, `iobuf_to_iovec()`, `iobuf_copy()`, `iobuf_size()`, `iobuf_stats_dump()`, and `iobuf_get_from_small()`. `iobref` APIs include `iobref_new()`, `iobref_ref()`, `iobref_unref()`, `iobref_add()`, `iobref_merge()`, `iobref_clear()`, and `iobref_size()`.

The allocator uses sorted `gf_iobuf_init_config[]` classes from 128 bytes through 1 MiB. `struct iobuf_pool` owns per-class `arenas`, `filled`, and `purge` lists. `struct iobuf_arena` represents an mmap region split into `struct iobuf` objects with active and passive lists. `struct iobuf` has a refcount, lock, data pointer, page size, and arena pointer.

## Control Flow
Pool creation initializes list heads, sets a 128 KiB default page size, preallocates one arena per configured class, and creates a special standard-allocation arena at index `IOBUF_ARENA_MAX_INDEX`. `iobuf_get2()` normalizes zero-size requests to the default. Requests at or below `USE_IOBUF_POOL_IF_SIZE_GREATER_THAN` use `iobuf_get_from_small()` and allocate one standalone object. Larger requests are rounded to a configured class; if the size exceeds all classes, `iobuf_get_from_stdalloc()` allocates an individually aligned object and increments `request_misses`. Pooled requests take the pool mutex, select an arena with passive buffers or add/unprune one, move one iobuf from passive to active, and ref it.

`iobuf_unref()` atomically decrements the buffer ref; the zero transition calls `iobuf_put()`. Pooled buffers re-enter the arena passive list and may cause empty arenas to move to purge or be destroyed. Standalone small/stdalloc buffers are freed directly. `iobref` owns a growable array of referenced `iobuf *`; add and merge operations take references, and destroy/clear releases them.

`iobuf_copy()` computes source iovec length, allocates one destination iobuf and iobref, adds the iobuf to the ref set, unloads the source iovec into the buffer, and returns a destination iovec view.

## State And Persistence
State is in-memory only. The pool tracks arena count, total arena bytes, request misses, and per-arena allocation/max-active counters. `iobuf` refs and `iobref` refs are atomic; arena list membership is protected by the pool mutex. No buffer contents are persisted by this module.

## Dependencies And Integration Points
The file depends on `glusterfs/iobuf.h`, statedump helpers, logging/message IDs, list primitives, atomics, locks, `mmap/munmap`, iovec utilities (`iov_length`, `iov_unload`), and Gluster allocation wrappers. It integrates with transport and storage code that needs `struct iovec` plus `iobref` lifetime coupling.

## Risks
The threshold name is counterintuitive: requests less than or equal to 128 KiB bypass the arena pool, based on observed small-file performance. `gf_iobuf_get_pagesize()` returns `(size_t)-1` on oversize; comparisons rely on that sentinel. `iobuf_get2()` does not validate a NULL pool before reading `default_page_size` for zero-size requests. `iobref_clear()` unrefs all contained iobufs and then unrefs the iobref itself, so callers must not use the object afterward unless they hold another ref. Alignment in `iobuf_get_page_aligned()` shifts `ptr` inside a larger allocation; code must use `page_size` carefully because requested size was inflated by `align_size`.

## Test Signals
Tests should cover class rounding, small allocation path, stdalloc oversize path, ref/unref zero transitions, arena movement among arenas/filled/purge, pool destruction with no leaks, `iobref` growth beyond 16 entries, merge semantics, page-aligned pointer checks, `iobuf_copy()` data integrity, and statedump under active buffers. Race tests should stress concurrent `iobuf_get2()`/`iobuf_unref()` on shared pools.
