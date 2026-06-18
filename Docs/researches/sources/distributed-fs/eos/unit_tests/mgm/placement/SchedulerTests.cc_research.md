# sources/distributed-fs/eos/unit_tests/mgm/placement/SchedulerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/placement/SchedulerTests.cc

Purpose: extensively tests placement strategies and `FlatScheduler` across hierarchical cluster topologies, weighted strategies, excluded filesystem IDs, forced groups, and concurrent cluster updates.

Important APIs and types: `RoundRobinPlacement`, `FlatScheduler`, `PlacementArguments`, `AccessArguments`, `PlacementResult`, `PlacementStrategyT`, `WeightedRandomStrategy`, `ClusterMgr`, `StorageHandler`, `Disk`, bucket types, `kBaseGroupOffset`, and `SimpleClusterF`.

Control flow: basic tests descend root-to-site-to-group-to-disk using round-robin, random, and thread-local round-robin. Loop tests count distribution across 30 disks and assert every disk is selected. Flat scheduler tests verify recursive scheduling returns valid replica sets. Single-site/no-site tests build alternate topologies and run repeated scheduling. Exclusion tests run many iterations across several strategies and assert excluded fsid 1 never appears. Forced-group tests constrain placement to a specified group and verify out-of-range errors. Weighted tests check that higher disk weights receive more selections. The concurrency test starts many reader threads scheduling while writer threads add groups and disks.

State and persistence: scheduler and cluster state are in memory, but concurrency tests exercise shared `ClusterMgr` snapshot/update behavior. Diagnostic memory output reads `/proc/self/status`.

Dependencies and integration: this is a major integration surface for placement logic, cluster maps, strategy selection, weighting, and thread safety.

Risks and test signals: randomized/weighted behavior is asserted statistically and can be sensitive to algorithm changes. High iteration counts and 100 reader threads make the concurrency test valuable but potentially expensive. Forced-group and exclusion behavior are high-risk because they are policy constraints.
