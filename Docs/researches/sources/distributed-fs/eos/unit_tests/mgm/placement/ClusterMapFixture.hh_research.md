# sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapFixture.hh

## sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapFixture.hh

Purpose: defines `SimpleClusterF`, a reusable placement-test fixture with a small hierarchical cluster.

Important APIs and types: `ClusterMgr`, `StorageHandler`, `addBucket`, `addDisk`, `Disk`, `StdBucketType::ROOT`, `SITE`, and `GROUP`, plus disk `ConfigStatus::kRW` and `ActiveStatus::kOnline`.

Control flow: setup builds root bucket 0, two site buckets, three group buckets, and thirty disks distributed as ten disks per group. Group IDs are negative bucket IDs; disk IDs are positive.

State and persistence: fixture owns an in-memory `ClusterMgr`. No external cluster state is used.

Dependencies and integration: used heavily by `SchedulerTests.cc` to exercise round-robin, random, thread-local, and flat scheduler behavior over a stable topology.

Risks and test signals: topology assumptions are embedded in downstream expected counts. Changing disk distribution or bucket IDs will affect many scheduler expectations.
