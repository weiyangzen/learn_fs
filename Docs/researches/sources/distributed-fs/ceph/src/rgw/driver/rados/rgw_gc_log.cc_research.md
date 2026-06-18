# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc_log.cc

## Purpose
`rgw_gc_log.cc` provides small helper functions that compose version-checked RADOS object operations for RGW GC log initialization, enqueue, and defer paths. It centralizes the transition boundary between legacy version-0 entries and version-1 `cls_rgw_gc` queue entries.

## Important APIs, Types, And Functions
`gc_log_init2()` checks object version 0, initializes the queue with configured max size and max deferred count, then sets version 1. `gc_log_enqueue1()` writes a legacy cls_rgw GC entry under version 0. `gc_log_enqueue2()` checks version 1 and enqueues into the queue.

`gc_log_defer1()` checks version 0 and defers an existing legacy entry by tag. `gc_log_defer2()` checks version 1, defers into the queue, and removes the legacy tag as cleanup.

## Control Flow
`RGWGC::initialize()` uses `gc_log_init2()`. Producer paths prefer `gc_log_enqueue2()` and fall back to legacy operations when version checks fail. Asynchronous defer paths use `gc_log_defer1()` until a version-check cancellation indicates transition, then retry through queue operations.

## State And Persistence Behavior
These helpers do not execute operations; they append cls operations to a caller-owned `librados::ObjectWriteOperation`. Version state is stored through `cls_version_check()` and `cls_version_set()`. Queue state is managed by `cls_rgw_gc_queue_*` operations; legacy state by `cls_rgw_gc_set_entry()`, `cls_rgw_gc_defer_entry()`, and `cls_rgw_gc_remove()`.

## Dependencies And Integration Points
The file depends on cls RGW, cls RGW GC, and cls version client APIs. It is included by `rgw_gc.cc` enqueue, defer, and initialization paths.

## Risks And Edge Cases
Correct operation ordering matters: version checks must precede mutations to prevent writing legacy entries after transition or queue entries before initialization. `gc_log_defer2()` removes the legacy tag after queue defer; comments note this should ideally be conditional on omap emptiness knowledge.

## Test Signals
Tests should verify composed operation order, expected version checks for each helper, fallback-triggering return codes in callers, and migration behavior with mixed legacy and queue entries.
