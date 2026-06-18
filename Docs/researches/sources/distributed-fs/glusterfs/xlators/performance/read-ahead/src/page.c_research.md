# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/page.c

## Purpose
Implements the page-cache mechanics for the GlusterFS `performance/read-ahead` translator. It manages sorted per-fd read-ahead pages, asynchronous page faults, wait queues for user reads blocked on in-flight pages, page fill/unwind aggregation, stale/poisoned invalidation, and fd-cache destruction.

## Important APIs, Types, And Functions
The file operates on `ra_file_t`, `ra_page_t`, `ra_waitq_t`, and `ra_local_t` from `read-ahead.h`. `ra_page_get()` and `ra_page_create()` locate or insert page records at `gf_floor(offset, page_size)`. `ra_wait_on_page()` attaches a frame to a page wait queue and increments the frame-local wait count. `ra_page_fault()` copies the user frame, allocates a local, refs the fd, and winds a child `readv` for one page. `ra_fault_cbk()` stores the returned iovecs/iobref in the page or propagates errors to waiters. `ra_frame_fill()`, `ra_frame_return()`, and `ra_frame_unwind()` assemble page fragments into the user `readv` reply. `ra_page_wakeup()`, `ra_page_error()`, `ra_page_purge()`, and `ra_file_destroy()` are the completion and teardown primitives.

## Control Flow
Callers create or find pages under the file lock, then either fill immediately from a ready page or wait on a pending page. A fault frame reads a full page from the child translator. On callback, the code verifies the fd context, handles pages removed or marked stale, marks dirty+poisoned read-ahead pages as canceled, copies successful data into the page, and wakes all queued frames. Each waiting frame receives the relevant subrange via `iov_subset()` and only unwinds once `wait_count` reaches zero. Stale pages are retried if the in-flight read completed after invalidation.

## State And Persistence
All state is in memory and scoped to an open fd. `ra_page_t` stores offset, size, copied vectors, iobref, readiness, dirty/stale/poisoned flags, and waiters. `ra_file_t` owns the page list and file lock. Data is not durable; it is a client-side cache that must be invalidated on writes, truncates, discard, zerofill, and release.

## Dependencies And Integration Points
Depends on Gluster call frames, STACK_WIND/UNWIND, fd contexts, `iobref`, iovec helpers, memory accounting types from `read-ahead-mem-types.h`, and message IDs from `read-ahead-messages.h`. It is called by `read-ahead.c` for user reads, speculative reads, mutation invalidation, and fd release.

## Risks
Correctness depends on careful lock ordering and wait-count accounting. `ra_frame_unwind()` assumes the fd context still exists to supply `file->stbuf`; release races or missing fd context paths are high-risk. The code copies page iovecs but relies on iobref lifetimes to keep backing buffers valid. Dirty/poisoned handling prevents stale speculative data from being served, but mistakes around stale retry can either drop data or loop. Memory failures while filling a multi-page read turn the whole request into an error.

## Test Signals
Useful tests include sequential reads spanning several pages, concurrent readers waiting on the same page, OOM/error injection in `copy_frame`, `iov_dup`, `iobref_new`, and `iov_subset`, writes racing with in-flight speculative reads, fd release with pending pages, and short final-page reads. Statedump should show page offsets and waiters disappearing after wakeup or purge.
