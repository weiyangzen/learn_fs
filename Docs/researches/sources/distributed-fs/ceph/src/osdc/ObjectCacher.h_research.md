<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.h -->
# sources/distributed-fs/ceph/src/osdc/ObjectCacher.h

## Purpose

`ObjectCacher.h` declares the cache and writeback interface for object byte ranges used by Ceph filesystem clients. It defines the buffer-head state model, object grouping, read/write request containers, public cache operations, file-layout convenience wrappers, and performance counter ids used by `ObjectCacher.cc`.

## Important APIs and Types

The perf counter enum declares cache hit/miss operation counters, hit/miss byte counters, data read/written/flushed counters, overwritten-during-flush bytes, and dirty-limit blocking counters.

`ObjectCacher::OSDRead` carries a vector of `ObjectExtent`s, a read snap id, output buffer pointer, and fadvise flags. `prepare_read` allocates it. `ObjectCacher::OSDWrite` carries extents, `SnapContext`, data buffer, mtime, fadvise flags, and optional journal tid. `prepare_write` allocates it.

`BufferHead` is the per-object interval cache entry. Its states are `STATE_MISSING`, `STATE_CLEAN`, `STATE_ZERO`, `STATE_DIRTY`, `STATE_RX`, `STATE_TX`, and `STATE_ERROR`. It stores extent start/length, flags (`dontneed`, `nocache`), owning `Object`, data `bufferlist`, read/write tids, write time, snap context, journal tid, read error, and waiters by offset. Its refcount pins LRU entries during RX/TX states.

`Object` represents one cached `sobject_t` and owns a sorted `map<loff_t, BufferHead*> data`. It tracks object number, object set, locator, truncate size/seq, `complete`, `exists`, last write/commit tids, dirty-or-tx bytes, commit waiters, and in-flight read callbacks. It exposes interval manipulation (`split`, `merge_left`, `map_read`, `map_write`, `truncate`, `discard`) and reference/LRU helpers.

`ObjectSet` groups cached objects for a higher-level inode and pool. It stores owner pointer, inode, truncate metadata, pool id, object list, aggregate dirty/tx bytes, and `return_enoent` policy.

`ObjectCacher` owns the writeback handler, shared lock, dirty/cache sizing limits, trace endpoint, object indexes, wait queues, LRUs, dirty-or-tx set, flusher thread, finisher, stats, and public operations. Important public APIs are `start`, `stop`, `readx`, `writex`, `is_cached`, `flush_set`, `flush_all`, `purge_set`, `release_set`, `release_all`, `discard_set`, `discard_writeback`, `clear_nonexistence`, and tuning setters.

The file convenience methods `file_is_cached`, `file_read`, `file_read_ex`, `file_write`, and `file_flush` call `Striper::file_to_extents` and then use the object-level cache operations.

## Control Flow and Contracts

Most methods require the caller-provided cache lock to be held; the implementation asserts this extensively. Public non-blocking read and write calls return immediately with a byte count/error or zero for async in progress. Completion contexts are used for deferred reads, dirty-limit freespace notifications, flush completion, and discard-writeback completion.

The header separates allocation of request containers from execution. Callers build `OSDRead`/`OSDWrite` through helpers, populate extents through either direct object mappings or file convenience wrappers, and transfer ownership to `readx`/`writex`.

`ObjectCacher::start` and `stop` control the background flusher thread. Destruction expects all cache objects and LRUs to be empty, so owners must flush/release/purge before destroying the cacher.

## State and Persistence Behavior

The header declares only in-memory cache state. Durable writes are delegated through `WritebackHandler`; durable read state is reflected as clean/zero/error buffer heads. Dirty and TX bytes are tracked globally and per object set, and flushing transitions them toward clean. Snap context and truncate sequence fields are preserved in write requests and cached objects so writeback can be ordered correctly relative to snapshots and truncates.

LRU state is split between dirty buffers, non-dirty buffers, and objects. RX/TX buffers pin themselves with the `BufferHead` refcount so they cannot be evicted while I/O is active. `Object::can_close` requires no buffers and no commit waiters.

## Dependencies and Integration Points

`ObjectCacher.h` depends on Ceph core types, `LRUObject`, `Context`, `object.h`, `xlist`, `Cond`, `Finisher`, `SnapContext`, `Thread`, `zipkin_trace`, and `Striper`. It forward-declares `WritebackHandler`, which is the main persistence integration.

The API integrates with higher file clients through `ObjectSet` and file-layout wrappers. `flush_set_callback_t` lets owners be notified when an object set has no more dirty/TX data, which is important for journal/capability accounting outside the cache.

## Risks and Edge Cases

Because this is a lock-coupled API, callers must respect locking and lifetime rules. Passing request objects or completion contexts with insufficient lifetime will fail asynchronously. `return_enoent` is only meaningful for single-extent reads, and the implementation asserts that constraint.

The state enum allows many transitions, but only some are valid in context. Dirty/TX counters, journal tid replacement, and LRU membership must remain synchronized. The destructor's assertions make leaked dirty, RX, TX, or object refs visible at shutdown.

File convenience wrappers depend on correct `ObjectSet::truncate_size` and layout metadata. Incorrect truncate metadata can cause the cache to map or flush ranges inconsistent with OSD truncate ordering.

## Test Signals

Header/API tests should cover state predicate behavior, refcount pin/unpin, object close eligibility, object-set aggregation, request ownership transfer, public lock assertions in debug builds, file wrapper extent mapping, dirty limit setters, flusher start/stop lifecycle, and `return_enoent` single-extent enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.h -->
