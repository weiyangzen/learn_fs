# sources/control-plane/mayastor/io-engine/tests/replica_snapshot.rs

Purpose: ignored snapshot integration test covering local and remote replicas behind a nexus, snapshot creation, snapshot sharing over NVMf, data stability, and unsupported custom NVMe admin handling.

Important APIs/types/functions: `Lvs`, `PoolArgs`, `PoolBackend`, `SnapshotParams`, `UntypedBdevHandle`, `nexus_create`, v0 pool/replica/share RPCs, `MayastorTest`, `bdev_io`, `Uuid`, `Utc`, `create_nexus`, `format_snapshot_name`, `create_snapshot`, and `custom_nvme_admin`.

Control flow: the test creates a remote NVMf replica and local LVS lvol with matching UUID, builds a two-child nexus, writes/reads patterns, sends an unsupported vendor admin opcode and expects error, creates a snapshot, and verifies normal I/O still works. It then shares the remote snapshot, creates a snapshot nexus from suffixed child URIs, writes new data to the original nexus, and checks the snapshot still shows old data and zeros at an unwritten offset.

State and persistence behavior: snapshot metadata lives in LVS/replica state; no etcd. Snapshot names are timestamp-suffixed and reused for local and remote children.

Dependencies and integration points: local LVS, remote NVMf replica, nexus creation, snapshot handle API, NVMe admin passthrough, and data pattern helpers.

Risks: ignored test; comments note read-only snapshot write enforcement is not enabled.

Test signals: unsupported admin command errors, snapshot creation returns timestamp, snapshot share succeeds, original writes do not alter snapshot reads.
