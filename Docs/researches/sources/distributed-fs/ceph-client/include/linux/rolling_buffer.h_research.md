# sources/distributed-fs/ceph-client/include/linux/rolling_buffer.h

## Purpose
`rolling_buffer.h` declares a folio-queue backed rolling buffer used to stream folios from a producer to a consumer while tracking the live window with an `iov_iter`.

## Important APIs, types, and functions
The main type is `struct rolling_buffer`, with producer `head`, consumer `tail`, `iter`, `next_head_slot`, and `first_tail_slot`. `struct rolling_buffer_snapshot` records the current queue segment, slot, and folio order for read snapshots. Mark bits are `ROLLBUF_MARK_1` and `ROLLBUF_MARK_2`. APIs include `rolling_buffer_init()`, `rolling_buffer_make_space()`, `rolling_buffer_load_from_ra()`, `rolling_buffer_append()`, `rolling_buffer_delete_spent()`, `rolling_buffer_clear()`, and inline `rolling_buffer_advance()`.

## Control flow, state, and persistence
The buffer is never allowed to become empty: at least one `folio_queue` segment remains so producer and consumer do not both have to mutate both queue pointers. Producers append folios or load them from readahead into head slots, extending the iterator; consumers advance `iter`, delete spent queue segments from the tail, or snapshot the current read position. State is in-memory queue/iterator state and persists only while the owner keeps the rolling buffer live.

## Dependencies and integration points
It depends on `linux/folio_queue.h`, `linux/uio.h`, folio batches, and readahead control. It integrates with file/network/cache paths that want folio-granular producer/consumer buffering without copying data into a linear buffer.

## Risks and test signals
Risks include violating the non-empty invariant, slot index wrap mistakes, deleting a queue segment still referenced by a snapshot or iterator, mismatched folio marks, and producer/consumer races outside the intended one-thread-per-end model. Test signals include init/clear, append across queue segment boundaries, readahead loading, iterator advancement, deleting spent folios, snapshot reads, and concurrent producer/consumer stress under KCSAN.
