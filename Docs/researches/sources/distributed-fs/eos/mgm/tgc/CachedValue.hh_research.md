# sources/distributed-fs/eos/mgm/tgc/CachedValue.hh

## Purpose
`CachedValue.hh` provides a generic time-based cache for a single value. Tape-GC uses it to avoid re-reading per-space configuration from the MGM on every stats or worker iteration.

## Important APIs, Types, And Functions
`CachedValue<ValueType>` has constructor `CachedValue(std::function<ValueType()>, std::time_t maxAgeSecs)` and method `get()`. Members include a mutex, first-use flag, cached value, value getter callback, max age, and last update timestamp.

## Control Flow
`get()` locks, computes age from `time(nullptr) - m_timestamp`, and refreshes the cached value when it has never been set or when age is at least `m_maxAgeSecs`. A max age of zero causes every call to refresh because `age >= 0`.

## State And Persistence
The cache is in-memory only. It stores the last value by copy and the timestamp of the refresh. The callback is invoked while the cache mutex is held, so only one thread refreshes at a time.

## Dependencies And Integration Points
The template depends on standard time, function, and mutex facilities. `SmartSpaceStats` and likely space-specific GC code use it around `ITapeGcMgm::getTapeGcSpaceConfig()`.

## Risks And Edge Cases
The callback runs under lock, so slow MGM reads block all cache readers. Wall-clock rollback can make a value live longer than intended; wall-clock forward jumps can force early refresh. Exceptions from `m_valueGetter` propagate and leave previous cache state unchanged except for any timestamp changes already made.

## Test Signals
Tests should verify first-call refresh, reuse before max age, refresh after max age, zero-age always-refresh behavior, concurrent callers, and exception behavior from the getter.
