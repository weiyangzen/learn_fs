<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.cc

Source read size: 150 lines, 4596 bytes.

## Purpose

Implements an approximate weighted round-robin placement strategy using decrementing per-item weight budgets.

## Important APIs, Types, and Functions

Important methods are `WeightedRoundRobinPlacement::Impl::fill_weights`, `Impl::placeFiles`, public `placeFiles`, `access`, and destructor. State includes `mItemWeights`, `mBucketIndex`, `total_wt`, `total_disk_wt`, and `wt_mtx`.

## Control Flow

`placeFiles` locks the weight state, refills weights when total remaining weight is below the requested replica count, takes and increments a per-bucket round-robin index, then scans bucket items with `pickIndexRR`. Disk candidates are skipped when weight is exhausted, excluded, unknown, offline, or below requested config status; accepted disks decrement item, bucket, and total weights. Child buckets are accepted only if their remaining weight can satisfy the requested replicas. Success requires all replicas to be filled.

## State and Persistence Behavior

Weight budgets and bucket indexes persist in the strategy object between calls. They are not tied to cluster epochs except by refill decisions, so topology/weight changes may be reflected only on refill.

## Dependencies and Integration Points

Instantiated by `FlatScheduler` for `kWeightedRoundRobin`. Depends on cluster data, common round-robin picking, logging, and placement validation.

## Risks and Edge Cases

The strategy serializes placement with one mutex. `mCurrentEpoch` is declared but not used. Weight maps include default bucket slots and can be stale. `access` is unimplemented and returns `EINVAL`; `FlatScheduler` maps weighted round-robin access to weighted random instead.

## Test Signals

Test weight refill, proportional placement over repeated calls, excluded/offline/status-filtered disks, child bucket weights, insufficient capacity, topology changes between refills, and access fallback through `FlatScheduler`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.cc -->
