<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/snapshot_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/snapshot_cli.rs

### Purpose
`snapshot_cli.rs` is the minimal v0 snapshot CLI. It exposes only a single command to create a snapshot for a nexus UUID.

### Important APIs, Types, And Functions
`SnapshotArgs` wraps `SnapshotCommands::Create`. `CreateArgs` carries the nexus UUID. `create` sends `CreateSnapshotRequest` through the v0 Mayastor client.

### Control Flow
The handler dispatches to `create`, which stringifies the UUID, calls `create_snapshot`, then prints either the full JSON response or the UUID in default mode.

### State, Persistence, And Dependencies
The module creates remote snapshot state and has no local persistence. It depends on v0 snapshot RPCs, `uuid`, colored JSON, SNAFU, and `Context`.

### Risks And Test Signals
The v0 surface gives no list or destroy operation in this CLI, so cleanup must use other APIs. Tests should cover UUID parsing, successful create output, JSON formatting, and server-side errors for absent or invalid nexus UUIDs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/snapshot_cli.rs -->
