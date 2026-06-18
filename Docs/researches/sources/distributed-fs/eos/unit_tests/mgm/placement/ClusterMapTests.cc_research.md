# sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapTests.cc

Purpose: tests `ClusterMgr` and storage-handler construction of placement cluster data.

Important APIs and types: `ClusterMgr`, `ClusterData`, `StorageHandler`, `addClusterData`, `getClusterData`, `addBucket`, `addDiskSequential`, `addDisk`, `Bucket`, `Disk`, and standard bucket types.

Control flow: default and dummy-data tests verify cluster-data pointer presence and empty structures. Storage-handler tests build root/site/group hierarchies and validate bucket vector size, bucket indices, IDs, item ordering, and disk vector sizes for sequential, in-order, and sparse/out-of-order disk IDs. `BM_Layout` creates a larger root-to-groups layout with 32 groups and 16 disks per group.

State and persistence: all cluster data is in memory. Sparse disk IDs can grow the disk vector to the maximum ID range, as shown by out-of-order disk test expecting size 150.

Dependencies and integration: this is foundational for placement schedulers that consume `ClusterData`.

Risks and test signals: bucket indexing uses negative bucket IDs mapped to positive vector indexes, which is easy to break. Sparse disk IDs have memory implications and are explicitly tested.
