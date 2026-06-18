<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.hh -->
# sources/distributed-fs/eos/mgm/egroup/Egroup.hh

## Purpose

`Egroup.hh` declares the MGM e-group support class. It exposes a cache-backed API for checking whether an EOS username belongs to a CERN e-group, while hiding LDAP calls and asynchronous refresh machinery behind one object.

## Important APIs, Types, and Functions

`Egroup::Status` models uncached lookup results: member, not member, or error. `CachedEntry` carries `isMember` and a `std::chrono::steady_clock::time_point`. Public APIs include constructor/destructor, `Reset()`, `query()`, convenience `Member()`, `DumpMember()`, `DumpMembers()`, `scheduleRefresh()`, `fetchCached()`, `inject()`, `getPendingQueueSize()`, and synchronous `refresh()`. Private helpers include `storeIntoCache()`, `isStale()`, background `Refresh()`, and `isMemberUncached()`.

## Control Flow

The header describes a cache-read-first model: callers use `Member()` or `query()`, stale cached values are refreshed asynchronously, and synchronous LDAP is reserved for cache misses or explicit `refresh()`. The object owns its refresh thread and joins it on destruction.

## State and Persistence Behavior

The class owns only process-local state. `kCacheDuration` is a fixed 30-minute TTL. `cache` stores membership entries by egroup and username under `mMutex`. `mPendingQueue` carries background work, while `mPendingSet` plus `mMutexPending` deduplicates queued refreshes. `injections` is a fake LDAP response map for testing. No state is persisted outside memory.

## Dependencies and Integration Points

The declaration depends on MGM namespace macros, EOS `AssistedThread`, `SteadyClock`, `RWMutex`, qclient `WaitableQueue`, XRootD pthread support, STL maps/sets, and chrono. It is intended for MGM permission paths that may already hold read locks, so asynchronous refresh avoids long lock contention.

## Risks and Edge Cases

The API returns only a boolean for `Member()`, so callers cannot distinguish not-member from lookup failure. `CachedEntry()` defaults the timestamp, so consumers must not infer freshness from a default object unless `fetchCached()` succeeded. The pending set key concatenates username and egroup with `:`, which can theoretically collide if either component contains that separator. The class is copyable by default unless prevented elsewhere, but copying thread, mutex, and queue state would be unsafe; callers should treat it as non-copyable.

## Test Signals

Compile tests should include this header independently. Unit tests should exercise `query()`/`Member()` with injected data, TTL staleness using a fake `SteadyClock`, queue size/deduplication from `scheduleRefresh()`, and safe object destruction with outstanding queued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.hh -->
