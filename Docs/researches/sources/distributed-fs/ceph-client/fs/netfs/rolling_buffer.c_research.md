<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/rolling_buffer.c -->
# sources/distributed-fs/ceph-client/fs/netfs/rolling_buffer.c

## Purpose
Implements rolling folio_queue buffers shared by netfs read/write issuers and collectors. The design lets producer and consumer move independently while retaining at least one queue node as a stable placeholder.

## Important APIs, Types, And Functions
Exports `netfs_folioq_alloc()` and `netfs_folioq_free()`. Defines `rolling_buffer_init()`, `rolling_buffer_make_space()`, `rolling_buffer_load_from_ra()`, `rolling_buffer_append()`, `rolling_buffer_delete_spent()`, and `rolling_buffer_clear()`.

## Control Flow
Initialization allocates an empty queue, sets both head and tail, and creates a folio_queue iterator. Producers call make-space before appending or loading readahead folios. When a head queue fills, a new queue is allocated and linked with release ordering because the consumer may delete the old node immediately after `next` becomes visible. Consumers delete spent tail queues only when there is a following node; otherwise they return NULL and keep the placeholder. Clear walks all nodes and drops marked folios in batches.

## State And Persistence
State is transient in `struct rolling_buffer`: head, tail, iterator, next-head slot, and per-queue marks. Mark 1 means folio references are released on clear; mark 2 is used by abandoned read-page handling.

## Dependencies And Integration Points
Used by read readahead buffering, writeback/writethrough buffers, pgpriv2 copy-to-cache, object cleanup, and folio queue stats/tracing. Depends on `linux/rolling_buffer.h`, folio_queue helpers, and tracepoints.

## Risks
Producer/consumer races around queue linking/deletion are the main hazard. Iterator adjustment when head is full prevents pointing at a soon-freed node. Incorrect marks can leak folio refs or release pages still owned elsewhere.

## Test Signals
Readahead loading across multiple queue nodes, append/advance/delete under concurrent producer/collector timing, clear with marked and unmarked folios, and memory allocation failure in make-space.
