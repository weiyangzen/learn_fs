<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_cli.rs

### Purpose
`snapshot_cli.rs` implements v1 snapshot and clone management. It supports nexus-coordinated snapshot creation, per-replica snapshot creation, listing, destruction, clone creation, and clone listing.

### Important APIs, Types, And Functions
`SnapshotArgs` wraps `CreateForNexus`, `CreateForReplica`, `List`, `Destroy`, `CreateClone`, and `ListClone`. Input structs carry nexus/replica/snapshot UUIDs, snapshot names, entity and transaction IDs, pool selectors, and clone identifiers.

### Control Flow
`create_for_nexus` requires equal counts of replica UUIDs and snapshot UUIDs, zips them into descriptors, sends `NexusCreateSnapshotRequest`, and prints nexus plus per-replica status. `create_for_replica` sends a direct snapshot request and prints snapshot metadata. `list` filters by optional source and snapshot UUID. `destroy` builds a oneof pool selector from optional pool UUID or name. Clone commands create or list replicas derived from snapshots and print allocation and ancestry fields.

### State, Persistence, And Dependencies
The module creates and deletes remote snapshot metadata and clone replicas. Dependencies include v1 snapshot protobufs, `uuid`, colored JSON, SNAFU, and shared context. It integrates with replica and nexus data paths, snapshot metadata persistence, and clone allocation accounting.

### Risks And Test Signals
Several optional fields are unwrapped, including nexus response and clone usage. Timestamp defaults may hide missing metadata. The count-mismatch error uses `MissingValue`, which is semantically approximate. Tests should cover count validation, pool selector conflicts, optional usage absence, clone list empty behavior, JSON/default output, and server failures for invalid snapshot/replica IDs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_cli.rs -->
