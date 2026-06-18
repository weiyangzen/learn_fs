# sources/distributed-fs/ceph/src/rgw/driver/d4n/d4n_policy.h

## Purpose

`d4n_policy.h` declares the cache policy abstraction and two concrete D4N cache policy implementations: LFUDA and LRU. It is the policy contract used by the D4N SAL filter to ask whether cache entries exist, make room for new cache data, update cache metadata after reads/writes, manage dirty write-cache objects, erase entries, and run background cleaning. It also declares `PolicyDriver`, the small selector that instantiates a policy by configuration name.

## Important APIs and types

- `RefCount` is an enum with `NOOP`, `INCR`, and `DECR` operations used by policy update paths to protect active blocks from eviction.
- `State` is the dirty-object state machine: `INIT`, `IN_PROGRESS`, and `INVALID`.
- `CachePolicy` is the abstract base class. It defines protected `Entry`, `Entry_delete_disposer`, and `ObjEntry` types plus virtual methods for initialization, existence checks, eviction, refcount updates, block updates, dirty-object updates, block and dirty-object erase, dirty invalidation, and cleaning.
- `LFUDAPolicy` extends `CachePolicy` with heap-based LFUDA state, dirty-object cleaning state, Redis synchronization helpers, directory pointers, cache driver pointer, SAL driver pointer, timer, and cleaner thread.
- `LFUDAEntry` extends `Entry` with `localWeight` and a Fibonacci heap handle.
- `LFUDAObjEntry` extends `ObjEntry` with a heap handle for creation-time ordered dirty-object cleaning.
- `LRUPolicy` extends `CachePolicy` with an intrusive list, block and dirty-object maps, and a cache driver pointer.
- `PolicyDriver` owns a raw `CachePolicy*`, constructs `LFUDAPolicy` for `"lfuda"` and `LRUPolicy` for `"lru"`, and exposes `get_cache_policy()` and `get_policy_name()`.

## Control flow and API shape

The D4N SAL layer interacts through `CachePolicy`, not directly through LFUDA or LRU, for most operations:

1. `init()` receives the Ceph context, log provider, Asio context, and underlying SAL driver.
2. `eviction()` is called before caching new data to ensure enough local cache space.
3. `update()` records a cached block/head object access or insertion, optionally changing dirty state and refcount.
4. `update_refcount_if_key_exists()` is used around read paths to protect blocks while they are being served.
5. `update_dirty_object()` registers a dirty write-cache object for later write-back.
6. `invalidate_dirty_object()` handles deletes/overwrites of dirty objects so cleaner deletes instead of writes stale data.
7. `erase()` and `erase_dirty_object()` remove policy state when cache entries are deleted.
8. `cleaning()` is run as a background policy operation for write-cache flushing.

`LFUDAPolicy` uses two different heaps: one for eviction candidates ordered by LFUDA entry comparator and one for dirty objects ordered by creation time. Its comparator treats dirty blocks and positive-refcount blocks as lower eviction priority, so the heap top should be an eligible clean/unreferenced victim when one exists.

`LRUPolicy` intentionally provides a smaller subset of semantics. It satisfies the interface, but refcount update, dirty invalidation, and cleaning are no-ops or false-returning stubs.

## State and persistence behavior

The header declares in-memory state and the persistence collaborators:

- `entries_map` and `entries_heap`/`entries_lru_list` track cached block policy state.
- `o_entries_map` and `object_heap` track dirty objects pending write-back.
- `lfuda_lock` protects LFUDA block heap/map state.
- `lfuda_cleaning_lock`, `cond`, and `state_cond` protect dirty-object state and coordinate cleaner wakeups.
- `age`, `weightSum`, and `postedSum` support LFUDA scoring and Redis synchronization.
- `conn` is the Redis connection used for LFUDA global metadata.
- `blockDir`, `objDir`, and `bucketDir` are directory clients used by the LFUDA cleaner and eviction logic.
- `cacheDriver` persists cache bytes and cache xattrs.
- `driver` points to the underlying SAL driver for backend writes/deletes.
- `tc` is the dirty-object cleaner thread and `rthread_timer` drives Redis sync.

The header also shows ownership choices. `LFUDAPolicy` manually `new`s the three directory objects in its constructor and deletes them in its destructor. `PolicyDriver` manually owns `cachePolicy`.

## Dependencies and integration points

The header includes Boost.Asio coroutine primitives, Boost heap Fibonacci heap, Boost system error definitions, D4N directories, D4N SAL declarations, and RGW cache driver declarations.

Integration points:

- `rgw_sal_d4n.h` and `rgw_sal_d4n.cc` access `PolicyDriver` through `D4NFilterDriver::get_policy_driver()`.
- `d4n_policy.cc` provides the concrete implementation.
- `d4n_directory.h` types are used for Redis directory updates during eviction and cleaning.
- `rgw_cache_driver.h` provides local cache persistence and xattrs.
- Ceph configuration keys such as `d4n_writecache_enabled`, `rgw_lfuda_sync_frequency`, `rgw_d4n_cache_cleaning_interval`, `rgw_d4n_local_rgw_address`, and `rgw_max_chunk_size` are consumed by the implementation.

## Risks and edge cases

- `static std::string empty` is defined in a header with external linkage semantics that can be problematic across translation units; it is used as a default non-const reference argument. Calls that omit `restore_val` share this mutable object.
- Virtual methods accept `uint8_t op`, while callers use `RefCount` enum values. The unscoped enum converts implicitly, but stronger typing would reduce invalid operation values.
- `PolicyDriver::cachePolicy` is not default-initialized and unknown `policyName` leaves it indeterminate. `get_cache_policy()` or the destructor can then dereference/delete garbage.
- Raw owning pointers in `LFUDAPolicy` and `PolicyDriver` make exception safety and partial construction fragile.
- `LFUDAPolicy::quit` is `inline static std::atomic<bool>`, so all LFUDA policy instances share one stop flag. Multiple D4N filter instances could interfere with each other's cleaner lifecycle.
- The LFUDA comparator logic is subtle: it mixes dirty and refcount conditions with local weight ordering, and correctness depends on the heap top being an evictable candidate or proving none are evictable.
- `LRUPolicy` does not implement the full dirty-write-cache contract exposed by `CachePolicy`, so selecting `"lru"` in configurations that expect write-cache cleaning or invalidation can silently skip those behaviors.
- Several methods accept `optional_yield y` and store it in LFUDA state (`save_y()` and member `y`), so lifetime/thread use of yield contexts needs scrutiny.

## Test signals

Header-level tests should verify interface behavior through both policies:

- `PolicyDriver` selection for `"lfuda"` and `"lru"`, plus behavior for invalid names.
- `CachePolicy` polymorphic calls from SAL-style code for eviction/update/erase.
- LFUDA comparator ordering for clean, dirty, refcounted, and differently weighted entries.
- Dirty state-machine transitions for `INIT`, `IN_PROGRESS`, and `INVALID`.
- LRU implementation conformance where methods are intentionally no-op should be documented or guarded by configuration tests.
- Destructor/lifecycle behavior with cleaner thread and Redis timer cancellation.

No direct unit tests were found in the local source subset. Integration signals are the numerous calls from `rgw_sal_d4n.cc`, especially read refcount updates, write-cache dirty-object registration, delete invalidation, and eviction before cache insertion.
