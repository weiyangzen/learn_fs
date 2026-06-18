<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.cc -->
# sources/distributed-fs/eos/mgm/placement/FlatScheduler.cc

Source read size: 189 lines, 5818 bytes.

## Purpose

Implements `FlatScheduler`, the strategy-dispatching placement engine that walks cluster buckets and selects disks or sub-buckets for replicas.

## Important APIs, Types, and Functions

Important functions are `makePlacementStrategy`, constructors, `schedule`, `scheduleDefault`, `access`, and `accessStategyIndex`. It instantiates round-robin, weighted-random, and weighted-round-robin strategies in `mPlacementStrategy`.

## Control Flow

`schedule` validates replica count and strategy, then either calls `scheduleDefault` or performs a BFS over buckets according to selection rules. Each bucket level delegates to the chosen `PlacementStrategy::placeFiles`; returned negative ids are queued as child buckets and positive ids become final disk ids. `scheduleDefault` descends one bucket at a time until it reaches a valid disk placement, selecting all replicas at group level and optionally honoring `forced_group_index`. `access` maps several strategy names to an access strategy implementation and delegates replica read selection.

## State and Persistence Behavior

`FlatScheduler` owns strategy objects and their in-memory seeds/caches. It does not persist placements.

## Dependencies and Integration Points

Depends on `ClusterData`, `PlacementStrategy`, `RoundRobinPlacement`, `WeightedRandomPlacement`, and `WeightedRoundRobinPlacement`. It is owned by `FSScheduler`.

## Risks and Edge Cases

The early bucket check appears inverted: it returns "Bucket id out of range" when `isValidBucketId(args.bucket_id, cluster_data)` is true. The BFS branch shadows `result` inside the loop and returns the outer result, so non-default scheduling may drop successful ids. Rule indexing by `bucket.bucket_type` assumes valid type below `MAX_PLACEMENT_HEIGHT`. `accessStategyIndex` maps weighted round robin to weighted random for access.

## Test Signals

Test default placement through root/group/disk, forced group success/failure, non-default BFS rule traversal, invalid bucket ids, zero replicas, invalid strategy fallback, and access strategy mapping for all strategy enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.cc -->
