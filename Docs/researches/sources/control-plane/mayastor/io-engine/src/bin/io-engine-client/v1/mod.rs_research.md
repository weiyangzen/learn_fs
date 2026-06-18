<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/mod.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/mod.rs

### Purpose
`v1/mod.rs` defines the default v1 `io-engine-client` command tree. It wires v1 global options, command modules, context construction, and dispatch.

### Important APIs, Types, And Functions
The file exports v1 command modules for bdev, controller, device, jsonrpc, nexus, perf, pool, rebuild, replica, snapshot, stats, plus private snapshot-rebuild and test modules. `Opts` defines global bind/quiet/verbose/units/output options. `Commands` includes v1-only `Stats`, `Test`, and `snapshot-rebuild`.

### Control Flow
`main_` parses clap options, creates `Context`, and matches the selected command to its handler. The default bind is `http://127.0.0.1` with optional `MY_POD_IP` environment override; `Context::new` adds port 10124. The default unit base is decimal.

### State, Persistence, And Dependencies
The module holds process-local CLI options only. It depends on clap, `version_info`, SNAFU context mapping, and all sibling command modules. It is selected by default from top-level `main.rs`.

### Risks And Test Signals
Differences from v0 defaults can surprise scripts: v1 is default, bind can come from `MY_POD_IP`, and units default to decimal. Tests should validate command availability, environment bind handling, global option propagation, command dispatch, quiet/verbose conflict, and default units.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/mod.rs -->
