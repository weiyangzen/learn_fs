<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/perf_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/perf_cli.rs

### Purpose
`perf_cli.rs` provides the v1 command-tree entry for process resource usage, but it still calls the legacy v0 RPC because no v1 equivalent exists.

### Important APIs, Types, And Functions
`PerfArgs` wraps `PerfCommands::Resource`. `get_resource_usage` is marked with a TODO noting the lack of a v1 RPC and uses `ctx.client.get_resource_usage`.

### Control Flow
The handler calls `get_resource_usage`, which sends v0 `Null {}` to the legacy client, prints JSON if requested, or builds a single table row from optional `usage` fields.

### State, Persistence, And Dependencies
The command is read-only and stores nothing locally. It depends on v0 performance protobufs from inside the v1 command tree, colored JSON, SNAFU, and table formatting.

### Risks And Test Signals
The v1 CLI remains coupled to v0 service availability for this command. As in v0, missing `usage` can lead to an empty table passed to `print_list`. Tests should cover legacy-client use, missing usage, output modes, and behavior if future v1 APIs replace this path.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/perf_cli.rs -->
