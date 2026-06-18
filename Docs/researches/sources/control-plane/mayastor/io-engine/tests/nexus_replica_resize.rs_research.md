# sources/control-plane/mayastor/io-engine/tests/nexus_replica_resize.rs

Purpose: tests multi-replica nexus expansion before/after replica resize, while a replica is rebuilding, and around snapshot creation with I/O running.

Important APIs/types/functions: `ResizeTest`, `ResizeTestTrait`, `StorConfig`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `NexusState`, `SnapshotParams`, `NexusCreateSnapshotReplicaDescriptor`, `FioBuilder`, `FioJobBuilder`, `JoinHandle<Fio>`, `NEXUS_CONNECT_PATH`, and `setup_cluster_and_run`.

Control flow: setup creates three replicas across a nexus node and two replica nodes, publishes the nexus, opens it over NVMf, and starts a 20 second FIO. `WithoutReplicaResize` asserts nexus resize fails before all children grow. `AfterReplicaResize` resizes all replicas then the nexus. `WithRebuildingReplica` removes and re-adds a child to make the nexus degraded before resizing. `ResizeAfterSnapshot` creates a snapshot before expansion, expands, waits for FIO, creates a post-expansion snapshot, and runs post-resize I/O.

State and persistence behavior: snapshot metadata is held in `SnapshotParams`; no external persistent store is used. The tests observe replica sizes, nexus size/state, and snapshot creation state.

Dependencies and integration points: compose, NVMf, FIO, replica resize RPCs, nexus resize RPCs, and snapshot creation RPCs.

Risks: global `OnceCell` path can be problematic under parallel test execution; resize while FIO runs is timing-sensitive.

Test signals: expected resize errors, expanded replica sizes, exact nexus expanded size, `NexusDegraded` before rebuilding resize, successful snapshots, and successful post-resize FIO.
