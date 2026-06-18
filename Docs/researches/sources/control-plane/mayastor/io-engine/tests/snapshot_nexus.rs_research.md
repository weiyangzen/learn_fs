# sources/control-plane/mayastor/io-engine/tests/snapshot_nexus.rs

Purpose: integration tests for remote replica snapshots created directly through handles, through nexus snapshot orchestration, and through gRPC list/query APIs.

Important APIs/types/functions: helpers `launch_instance`, `create_nexus`, `create_device`, `check_replica_snapshot`, and `check_nexus_snapshot_status` coordinate compose, remote replicas, local nexus objects, and snapshot metadata checks. Tests use v1 pool/replica/snapshot RPCs, `NexusReplicaSnapshotDescriptor`, `NexusCreateSnapshotReplicaDescriptor`, `NexusSnapshotStatus`, `SnapshotParams`, `ListSnapshotsRequest`, `ListReplicaOptions`, `CreateReplicaSnapshotRequest`, `CreateSnapshotCloneRequest`, and `DestroySnapshotRequest`.

Control flow: the suite starts a remote io-engine with two shared replicas, optionally creates local NVMe bdevs and nexuses, then creates snapshots via remote bdev handles or nexus orchestration. It validates empty listings, duplicate snapshot UUID/name status mapping, ancestor/referenced-byte accounting after nexus writes and multiple snapshots, discarded snapshot list filters after clone/destroy, replica list filters for replica/snapshot/clone combinations, and multi-replica nexus snapshot request validation.

State/persistence: pools, replicas, snapshots, clones, and nexus objects are transient but distributed between a remote io-engine and local Mayastor context. Snapshot usage counters persist in replica metadata while NVMe-oF host devices and connections are explicitly connected/disconnected.

Dependencies/integration: covers compose networking, gRPC v1 services, NVMe-oF host discovery, SPDK nexus snapshot fan-out, errno status conversion, query filter semantics, and replica usage reporting.

Risks: relies on fixed NQNs, localhost NVMe-oF connects, exact snapshot ordering logic, and timeout options. Duplicate and multi-replica paths are especially sensitive to request validation and per-replica status contracts.

Test signals: passing tests show nexus snapshot fan-out, remote snapshot metadata, duplicate handling, usage/referenced-byte accounting, clone/discard filters, and multi-replica validation remain compatible.
