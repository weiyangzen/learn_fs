<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.hh

Source read size: 140 lines, 4113 bytes.

## Purpose

Declares the unweighted placement strategy and seed-provider abstraction.

## Important APIs, Types, and Functions

Defines `RRSeeder`, `GlobalRRSeeder`, `ThreadLocalRRSeeder`, `RandomSeeder`, `FidSeeder`, `makeRRSeeder`, and `RoundRobinPlacement`.

## Control Flow

Concrete seeders return a starting offset for a bucket. Global seeders use atomic counters, thread-local seeders use per-thread vectors, random seeders use `getRandom`, and fid seeders derive a deterministic seed from bucket index, replica count, and fid. `RoundRobinPlacement` delegates placement and access to the `.cc` implementation.

## State and Persistence Behavior

Seeder state is in memory. Thread-local seeds are initialized when a thread-local strategy object is constructed.

## Dependencies and Integration Points

Used by `FlatScheduler` and the round-robin strategy implementation. Depends on logging, cluster data, placement interfaces, `RRSeed`, `ThreadLocalRRSeed`, and random utilities.

## Risks and Edge Cases

The trailing namespace comment has a typo, harmless to compilation but a maintenance signal. `RandomSeeder::get` handles `index > mMaxBuckets`, not `>=`, and logs before returning an adjusted value. Fid seeding is deterministic but simple xor may collide heavily for related ids.

## Test Signals

Compile each seeder path, test thread-local initialization in multiple threads, deterministic fid seeding, random range bounds, and strategy construction for all accepted unweighted enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.hh -->
