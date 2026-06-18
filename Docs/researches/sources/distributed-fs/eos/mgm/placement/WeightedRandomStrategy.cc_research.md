<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.cc

Source read size: 168 lines, 4627 bytes.

## Purpose

Implements weighted-random placement and a weighted access-selection path. Disk and bucket weights are derived from cluster snapshot weights.

## Important APIs, Types, and Functions

Important pieces are `WeightedRandomPlacement::Impl`, `populateWeights`, `Impl::placeFiles`, public `placeFiles`, `access`, and destructor. It uses `std::discrete_distribution`, a shared mutex, thread-local `std::mt19937`, `hashFid`, and `validDiskPlct`.

## Control Flow

Weights are populated lazily the first time placement is requested: one distribution for buckets and one per bucket's item list. Placement samples item indexes from the distribution for `args.bucket_id`, skips duplicates and unusable disks, and fills requested replicas up to `MAX_PLACEMENT_ATTEMPTS`. Access walks the already selected fs ids, filters invalid/unavailable/read-disallowed disks, computes `hashFid(inode, fsid) / weight`, and selects the lowest score.

## State and Persistence Behavior

The strategy caches distributions inside `Impl` for the process lifetime. It does not currently track cluster epochs, so cached distributions can become stale after weights or topology change.

## Dependencies and Integration Points

Instantiated by `FlatScheduler` for weighted-random strategy and also used as the access strategy for weighted modes. Depends on C++ random facilities, cluster data, logging, and placement helpers.

## Risks and Edge Cases

`populateWeights` iterates default bucket slots too, so bucket id/index validity matters. Placement sets `ret_code=0` even if fewer than requested replicas were added. Access stores `best_index = fsid` but `selectedIndex` convention may expect an index into `selectedfs`; the final `best_index <= args.selectedfs.size()` check is suspicious for fs ids greater than the vector length. Division by zero is possible if disk weight is zero.

## Test Signals

Test distribution population for sparse buckets, duplicate/filtered candidates, stale cache after weight changes, insufficient replicas, zero weights, weighted access index semantics, unavailable/excluded replicas, and deterministic hash ranking for a fixed inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.cc -->
