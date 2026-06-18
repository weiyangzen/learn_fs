
# sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.c

Purpose: maintains a timestamp-ordered queue of perf events so session processing can tolerate moderately out-of-order input and deliver records in time order.

Important APIs/types/functions: `ordered_events__queue` queues a record with timestamp, file offset, and file path. `ordered_events__flush` and `ordered_events__flush_time` deliver queued records according to final, round, half, top, or explicit time policies. `ordered_events__delete` moves delivered nodes to a cache. `ordered_events__init`, `ordered_events__free`, `ordered_events__reinit`, and `ordered_events__first_time` manage lifecycle. Internal allocation uses 64 KiB buffers of `struct ordered_event` plus optional duplicated perf records when `copy_on_queue` is enabled.

Control flow: `queue_event` inserts new nodes near `oe->last`, optimizing for nearly sorted input while preserving ascending timestamps. `alloc_event` reuses cached nodes, then current buffer slots, then allocates a new buffer under `max_alloc_size`; it also duplicates input records when requested. `ordered_events__queue` rejects zero or all-ones timestamps, increments unordered counters for timestamps older than `last_flush`, flushes half the queue on allocation failure, and retries. Flushing computes `next_flush`, iterates until timestamps exceed the limit, calls the client deliver callback, deletes delivered nodes, updates progress and last-flush state, then repairs `oe->last`.

State and persistence: `struct ordered_events` holds the ordered event list, cache list, allocation buffers, allocation accounting, flush timestamps, counters, callback, copy mode, and caller data. State is entirely in memory and freed through `ordered_events__free`.

Dependencies: Linux lists, perf session abort checks, debug ordered-event logging, `ui_progress`, `memdup`, and caller-supplied delivery logic.

Integration points: used by perf session processing for ordered sample delivery, especially `perf report/script` paths consuming perf.data records. File offset/path fields support diagnostics and data provenance during processing.

Risks: allocation accounting is shared between duplicated records and buffers; incorrect accounting can defeat limits or underflow. `ordered_events__free` must free only allocated slots in the current buffer. Delivery callbacks returning errors stop flushing and leave remaining records queued. Test signals include ordered-events unit tests, final/half/time flush scenarios, `copy_on_queue` memory tests, unordered-event counters, allocation-limit retry behavior, and report/script runs on out-of-order perf.data.
