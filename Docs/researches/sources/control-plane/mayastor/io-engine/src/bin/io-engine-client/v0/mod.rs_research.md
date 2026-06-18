<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/mod.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/mod.rs

### Purpose
`v0/mod.rs` defines the v0 command tree for `io-engine-client`. It wires global options, v0 subcommands, context construction, and dispatch to each v0 CLI module.

### Important APIs, Types, And Functions
The file exports modules for bdev, controller, device, jsonrpc, nexus, perf, pool, rebuild, replica, and snapshot commands. `Opts` defines global `--bind`, `--quiet`, `--verbose`, `--units`, and `--output`. `Commands` enumerates all v0 command groups. `main_` is called by the top-level binary when `API_VERSION=v0`.

### Control Flow
`main_` parses clap arguments, builds a shared `Context`, then matches the selected `Commands` variant and awaits the corresponding handler. The default bind is `http://127.0.0.1:10124`; the default unit base is raw bytes; output defaults to human-readable tables.

### State, Persistence, And Dependencies
The module keeps only process-local parsed options. It depends on clap, `version_info`, SNAFU context mapping, and the shared context. It integrates with `main.rs` through `pub(super) async fn main_`.

### Risks And Test Signals
Every command pays the cost and failure surface of constructing all clients in `Context::new`, even if it only needs one. Global option defaults differ from v1, especially unit base and bind environment support. Tests should validate clap command availability, global option propagation, default values, quiet/verbose conflict, and dispatch to each handler.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/mod.rs -->
