
# sources/distributed-fs/ceph-client/tools/perf/util/ordered-events.h

Purpose: declares timestamp-ordered perf event queue types and lifecycle/flush APIs.

Important APIs/types/functions: `struct ordered_event` stores timestamp, file offset/path, perf event pointer, and list node. `enum oe_flush` defines none, final, round, half, top, and time flush modes. `ordered_events__deliver_t` is the callback signature. `struct ordered_events_buffer` owns flexible arrays of event nodes. `struct ordered_events` stores flush timestamps, allocation limits/accounting, event/cache/free lists, current buffer, last node, deliver callback, counters, copy mode, and caller data. Inline setters configure allocation size and copy-on-queue; an inline getter exposes `last_flush`.

Control flow: callers initialize with a delivery callback, queue events, flush by policy, and free/reinit when done.

State and persistence: queue state is mutable and in memory only. If `copy_on_queue` is false, queued `event` pointers must remain valid until delivery; if true, this layer owns duplicates.

Dependencies: Linux types and list support through included headers in users. `union perf_event` is forward-used.

Integration points: session processing and perf.data readers include this header to buffer samples before ordered delivery.

Risks: wrong copy-on-queue mode causes dangling event pointers or unnecessary memory pressure. `max_alloc_size` defaults to unlimited until explicitly set. Test signals are compile coverage, queue/flush unit tests, and session processing regression tests.
