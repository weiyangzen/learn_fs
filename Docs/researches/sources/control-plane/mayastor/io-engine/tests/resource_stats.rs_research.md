# sources/control-plane/mayastor/io-engine/tests/resource_stats.rs

Purpose: integration test for v1 I/O statistics across pools, replicas, and a nexus with two remote children and one local child.

Important APIs/types/functions: `test_resource_stats` uses v1 `stats` RPCs, `reset_io_stats`, `get_pool_io_stats`, `get_replica_io_stats`, `get_nexus_io_stats`, `IoStats`, `ReplicaIoStats`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, and `test_fio_to_nexus`.

Control flow: three io-engine containers are started on separate core masks. Each creates a thick 60 MiB replica in an 80 MiB pool; the nexus node also hosts a local replica. After publishing a three-child nexus, all stats are reset and asserted zero. A 10 second random read/write fio run is issued through the nexus, then stats are fetched and cross-checked.

State/persistence: runtime counters on pools, replicas, and nexus are reset and then accumulated during fio. No persistent state survives compose cleanup.

Dependencies/integration: integrates stats gRPC service, fio workload generation, nexus read/write distribution, local and remote replica accounting, and latency tick aggregation.

Risks: random fio can be timing-sensitive. The test assumes mirrored writes give equal write op counts across children and that pool-level counters match replica counters exactly.

Test signals: validates nonzero write counts, read aggregation across replicas, write equality across mirrored replicas/pools, and latency ordering between pool, replica, and nexus layers.
