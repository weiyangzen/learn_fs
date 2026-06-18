<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.cc

Source read size: 91 lines, 2656 bytes.

## Purpose

Implements unweighted placement strategies: global round robin, thread-local round robin, random, and fid-derived random seeding.

## Important APIs, Types, and Functions

Key functions are `makeRRSeeder`, `RoundRobinPlacement::placeFiles`, and `RoundRobinPlacement::access`. The strategy uses `RRSeeder` implementations, `pickIndexRR`, `validDiskPlct`, and `MAX_PLACEMENT_ATTEMPTS`.

## Control Flow

`makeRRSeeder` selects a seeder based on `PlacementStrategyT`. `placeFiles` validates arguments, checks the bucket count fits the seed pool, obtains a seed for the bucket, then tries up to `MAX_PLACEMENT_ATTEMPTS` positions in the bucket item list. It skips duplicate selections and unusable disks, allows child buckets through, and succeeds only when the requested replica count is filled. `access` currently chooses a random selected filesystem index.

## State and Persistence Behavior

State is held in the seeder object or thread-local seed vector. There is no persistent placement record.

## Dependencies and Integration Points

Depends on cluster data, common random/container utilities, `RRSeed`, and `ThreadLocalRRSeed`. It is instantiated by `FlatScheduler`.

## Risks and Edge Cases

Random seeding may duplicate candidates and exhaust attempts. `RandomSeeder::get` returns a seed based on `mMaxBuckets`, not the selected bucket size. Access ignores disk health and geolocation and assumes `selectedfs` is nonempty. Bucket count greater than seed count is rejected.

## Test Signals

Cover each seeder type, duplicate avoidance, excluded/offline/status-filtered disks, child bucket selection, insufficient capacity, seed pool overflow, and access with empty and nonempty replica vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.cc -->
