# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/StatsCounter.java

## Purpose
`StatsCounter` centralizes counter-based cache metrics accounting for metastore caches.

## Important APIs and Types
- Package-private final class constructed with metric keys for evictions, hits, load times, and misses.
- Records hits, misses, evictions, and aggregate load duration against `MetricsSystem` counters.
- Registers the global `MASTER_INODE_CACHE_HIT_RATIO` gauge from hit and miss counters.

## Control Flow
Cache implementations call `recordHit`, `recordMiss`, `recordLoad`, and `recordEvictions` at read, load, and eviction points. The class maps those calls to configured counters and exposes hit ratio as hits divided by hits plus misses.

## State and Persistence
No metadata persistence. Metrics are accumulated in the global metrics registry counters/gauge.

## Dependencies and Integration Points
Used by `Cache` and `ListingCache`. Depends on `MetricKey`, `MetricsSystem`, and Dropwizard `Counter`.

## Risks and Edge Cases
Incorrect metric key wiring can report cache activity under the wrong name. Recording is side-effect-only and should remain lightweight because it runs on hot read/write paths. The hit-ratio gauge can compute `0 / 0` before any access, producing a non-finite value depending on metric consumer behavior.

## Test Signals
Tests should validate each record method increments the expected counter, load times accumulate as nanoseconds, evictions add counts, and the hit-ratio gauge behavior before and after hits/misses.
