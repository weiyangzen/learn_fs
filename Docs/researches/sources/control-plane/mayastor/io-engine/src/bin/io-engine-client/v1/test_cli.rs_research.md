<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/test_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/test_cli.rs

### Purpose
`test_cli.rs` exposes v1 testing and fault-injection utilities. It lists test features, adds/removes fault injections, and streams wipe progress for test-only resource wiping.

### Important APIs, Types, And Functions
`TestArgs` wraps `Features`, `Inject`, and `Wipe`. `Resource` currently supports `Replica`. `WipeMethod` maps to v1 wipe methods and checksum algorithm. `WipeArgs` carries resource UUID, optional pool selector, method, and optional chunk size. Helpers format bandwidth, checksum, and byte units.

### Control Flow
`features` calls `get_features`. `injections` lists injections when no add/remove arguments are present; otherwise it iterates add requests then remove requests. `replica_wipe` builds an optional pool oneof, wipe options, and chunk size, then consumes a server stream. JSON mode prints each streamed response. Default mode spawns a task to transform streamed responses into rows and passes an mpsc receiver to `Context::print_streamed_list`.

### State, Persistence, And Dependencies
The module mutates remote fault-injection state and can wipe replica data. It depends on v1 test protobufs, futures streams, `byte_unit`, `uuid`, strum derives, colored JSON, SNAFU, and Tokio channels. It integrates with test/fault-injection builds and destructive test workflows.

### Risks And Test Signals
Wipe is destructive; CLI validation only restricts resource enum and pool selector conflicts. The spawned streaming task unwraps channel sends, so consumer failure can panic. Bandwidth is blank for missing or non-normal elapsed durations. Tests should cover pool oneof construction, method mapping, chunked streaming, JSON streaming, injection add/remove/list, checksum formatting, and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/test_cli.rs -->
