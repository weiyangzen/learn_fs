<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RRSeed.hh -->
# sources/distributed-fs/eos/mgm/placement/RRSeed.hh

Source read size: 77 lines, 3347 bytes.

## Purpose

Defines a small atomic round-robin seed generator used by placement strategies to advance per-bucket selection offsets.

## Important APIs, Types, and Functions

The header defines `AtomicWrapper<T>` and template class `RRSeed<T>`. `RRSeed::get(index, n_items)` atomically fetch-adds the seed at an index, and `getNumSeeds()` reports the seed vector size.

## Control Flow

Construction initializes a vector of copyable atomic wrappers. Each `get` call reserves a range by adding `n_items`, letting callers select consecutive bucket items without a global scheduler lock.

## State and Persistence Behavior

State is process-local atomic counters. It is not a synchronization primitive for other data and is not persisted.

## Dependencies and Integration Points

Used by `GlobalRRSeeder` in `RoundRobinPlacementStrategy.hh`. Depends on atomics and vectors.

## Risks and Edge Cases

Only unsigned integral types are allowed because wraparound is expected. `get` uses `at`, so out-of-range indexes throw. Copying atomics is intentionally only for initialization/storage, not live synchronization.

## Test Signals

Test monotonic increments per index, multi-thread fetch-add behavior, wraparound for unsigned types if feasible, out-of-range exceptions, and construction with zero seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RRSeed.hh -->
