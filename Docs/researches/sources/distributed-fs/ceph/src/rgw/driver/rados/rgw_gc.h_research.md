# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.h

## Purpose
`rgw_gc.h` declares the RGW garbage collection service interface. It manages deferred cleanup of raw objects and chains through sharded GC logs and a background worker.

## Important APIs, Types, And Functions
`RGWGC` derives from `DoutPrefixProvider`. Public APIs include `initialize()`, `finalize()`, `send_split_chain()`, `async_defer_chain()`, `on_defer_canceled()`, `remove()`, `list()`, `process()`, `start_processor()`, and `stop_processor()`.

Private helpers include `tag_index()` for shard selection and `send_chain()` for enqueueing. Nested `GCWorker` derives from `Thread` and owns a mutex and condition variable for periodic processing and shutdown notification.

## Control Flow
Clients initialize the service with `CephContext` and `RGWRados`, enqueue or defer chains, optionally list GC entries for admin operations, and run processing either manually or through the worker. `stop_processor()` sets `down_flag`, wakes the worker, joins it, and deletes it.

## State And Persistence Behavior
The object stores GC shard count, shard object names, a transition cache, and a `down_flag`. Persistent queue contents live in RADOS and are manipulated in `rgw_gc.cc`. The destructor stops processing and finalizes the object-name array.

## Dependencies And Integration Points
It depends on librados, Ceph mutex and threading primitives, RGW common and SAL types, `RGWRados`, and cls RGW GC types. It exposes the cleanup service used by the RADOS backend.

## Risks And Edge Cases
Lifetime and async callbacks are important because the implementation schedules AIO operations that may outlive immediate calls. The destructor calls `stop_processor()` and `finalize()`, but external references or callbacks must not race destruction.

## Test Signals
Tests should cover initialization/finalization, worker start and stop idempotence, `going_down()` visibility, shard count sizing against configuration, and public list/process behavior with mocked GC pool responses.
