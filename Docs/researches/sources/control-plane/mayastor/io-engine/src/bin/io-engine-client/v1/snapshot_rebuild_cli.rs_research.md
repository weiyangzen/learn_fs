<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_rebuild_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_rebuild_cli.rs

### Purpose
This file exposes v1 snapshot-rebuild operations: create/start, destroy, and list. It is a separate command group from normal child rebuilds and targets replica reconstruction from snapshot sources.

### Important APIs, Types, And Functions
`SnapshotRebuildArgs` wraps `Create`, `Destroy`, and `List`. `CreateArgs` carries replica UUID and snapshot URI. `UuidArgs` and `ListArgs` identify rebuilds. `rebuild_status_to_str` maps `RebuildStatus` to display strings.

### Control Flow
Create sends `CreateSnapshotRebuildRequest` using the replica UUID as both `replica_uuid` and `uuid`, with empty snapshot UUID and replica URI, the provided snapshot URI, and bitmap disabled. Destroy sends UUID and always prints a deletion message. List optionally filters by rebuild UUID and prints rebuild UUID, snapshot URI, status, total/rebuilt/remaining, and timestamps.

### State, Persistence, And Dependencies
The module creates and destroys remote snapshot rebuild jobs. It depends on v1 snapshot-rebuild protobufs, `uuid`, colored JSON, and SNAFU. It integrates with experimental snapshot rebuild support enabled in the io-engine binary.

### Risks And Test Signals
Create hardcodes several empty/default request fields, so it may only cover one narrow server path. Destroy ignores output mode and always prints. The table header labels the rebuild UUID column as `REPLICA`, which may confuse operators. Tests should cover create request construction, status mapping, optional timestamps, JSON/default modes, destroy output, and server-side validation of empty fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/snapshot_rebuild_cli.rs -->
