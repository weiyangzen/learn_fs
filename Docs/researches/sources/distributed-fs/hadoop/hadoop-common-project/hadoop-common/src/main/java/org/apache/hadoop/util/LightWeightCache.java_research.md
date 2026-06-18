# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightCache.java

## Purpose

`LightWeightCache` extends `LightWeightGSet` with low-overhead expiration and optional size-limit eviction. It is designed for entries that already carry their own hash-chain links and expiration timestamp.

## Important APIs, Types, And Functions

Entries must implement `LightWeightCache.Entry`, extending `LinkedElement` with `setExpirationTime()` and `getExpirationTime()`. Public APIs override `get()`, `put()`, `remove()`, and `iterator()`. Internal helpers are `setExpirationTime()`, `isExpired()`, `evict()`, `evictExpiredEntries()`, and `evictEntries()`.

## Control Flow, State, And Persistence

Construction validates creation/access expiration periods, adjusts recommended hash length for size limits, and creates a `PriorityQueue` ordered by expiration time. `put()` evicts expired entries, replaces any equal entry, sets creation expiration, queues it, and enforces size limit. `get()` optionally refreshes access expiration by removing/reinserting in the queue. `remove()` also evicts expired entries. State is hash table plus priority queue and timer; no persistence.

## Dependencies And Integration Points

It depends on `LightWeightGSet`, Hadoop `Timer`, `Preconditions`, `HadoopIllegalArgumentException`, and Java `PriorityQueue`. It supports memory-sensitive caches in HDFS and common services.

## Risks And Test Signals

The class is explicitly not thread-safe. Queue `remove(Object)` is linear, and expired entries are evicted only opportunistically with a per-call limit. Tests should cover expiration, access refresh, replacement, size-limit enforcement, iterator remove rejection, invalid constructor args, and queue/hash consistency.
