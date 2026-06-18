# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_gc.cc

## Purpose
`rgw_gc.cc` implements RGW garbage collection for deferred object deletion. It shards GC logs across RADOS objects, supports transition from legacy omap entries to the `cls_rgw_gc` queue, processes expired entries under per-shard locks, schedules asynchronous refcount puts, and runs a background worker loop.

## Important APIs, Types, And Functions
`RGWGC::initialize()` sizes the GC shard set, initializes object names `gc.<index>`, prepares `transitioned_objects_cache`, and initializes each GC object with versioned queue state. `tag_index()` hashes tags with XXH64 and a fixed seed to choose a shard.

`send_split_chain()` splits large object chains according to `rgw_max_chunk_size`. `send_chain()` enqueues a chain into the v2 queue and falls back to legacy `cls_rgw_gc_set_entry()` on `-ECANCELED` or `-EPERM`.

`async_defer_chain()` defers a chain asynchronously, using queue operations when a shard has transitioned and legacy omap operations otherwise. `on_defer_canceled()` handles version-check cancellation as a transition signal and rewrites the defer into the queue.

`list()` merges legacy omap and queue entries while tracking markers and whether queue processing is in progress. `process()` handles one shard with a `gc_process` cls lock, lists expired entries, schedules tail object deletion through `RGWGCIOManager`, and removes retired GC entries. The overload `process(bool)` iterates shards from a random start. `GCWorker::entry()` runs periodic expired-only processing.

`RGWGCIOManager` batches asynchronous tail-object operations, tracks tag removal only after all shadow objects for a tag are done, limits concurrent AIO, and removes queue entries or legacy tags.

## Control Flow
Producers enqueue GC chains by tag. Processing begins by locking a GC shard object for a bounded duration. The processor lists up to 100 entries, respecting legacy or queue mode. For each chain, it opens the target pool when needed, sets object locator, allows deletion when pool is full, issues `cls_refcount_put(tag, true)` against each raw object, and later removes the GC tag or queue entries after successful scheduling and completion.

The background worker sleeps for `rgw_gc_processor_period` minus work duration and stops when `down_flag` is set.

## State And Persistence Behavior
GC state persists in RADOS GC pool objects named `gc.<index>`. Legacy entries live in cls_rgw omap-like structures at object version 0; queue entries live in `cls_rgw_gc` queue at version 1. `transitioned_objects_cache` memoizes which shard objects can use the queue path. Locks use cls lock name `gc_process`.

Tail deletion uses refcount class operations rather than direct removes. Successful tag removal retires entries from the GC log.

## Dependencies And Integration Points
The file depends on `RGWRados` GC pool contexts, cls_rgw, cls_rgw_gc, cls_refcount, cls_version, cls_lock, RGW perf counters, random utilities, and XXH64 hashing. It is used by RGW object delete, overwrite, lifecycle, and transition paths that defer raw object cleanup.

## Risks And Edge Cases
The async defer state has an explicit TODO about holding a reference to `RGWGC` to avoid use-after-free if the GC object destructs before callback completion. Transition handling mixes legacy and queue paths and must avoid deleting queue entries before all tail object puts succeed. `RGWGCIOManager::schedule_io()` drains only while `ios.size() > max_aio`, allowing one more than the configured max.

Failure behavior differs by mode: queue mode returns deletion errors to avoid removing queue entries; legacy mode often logs and continues to prevent unbounded tag buildup. Lock duration depends on `max_secs`, and zero or negative time returns `-EAGAIN`.

## Test Signals
Tests should cover enqueue fallback, chain splitting at encoded size boundaries, legacy-to-queue transition via `-ECANCELED`, list pagination across legacy and queue entries, per-shard locking, AIO concurrency and drain behavior, tag removal after multiple shadow objects, queue entry removal only after successful deletes, and worker shutdown wakeup.
