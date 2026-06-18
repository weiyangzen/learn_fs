<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/perf_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/perf_cli.rs

### Purpose
`perf_cli.rs` exposes the v0 resource-usage command. It reports process-level usage data, primarily the values returned by a server-side `getrusage`-style call.

### Important APIs, Types, And Functions
`PerfArgs` wraps `PerfCommands::Resource`. `get_resource_usage` calls `ctx.client.get_resource_usage(Null {})` and formats soft faults, hard faults, voluntary context switches, and involuntary context switches.

### Control Flow
The handler dispatches to `get_resource_usage`. The function logs a verbose request message, performs the RPC, and either prints the whole response as JSON or, when `usage` exists, prints a single table row. If `usage` is absent the table remains empty and is passed to `print_list`.

### State, Persistence, And Dependencies
The command is read-only and has no local persistence. It depends on v0 protobufs, `colored_json`, SNAFU gRPC mapping, and `Context` table printing.

### Risks And Test Signals
If the server returns `usage: None` in default mode, `ctx.print_list` receives an empty table and panics. Tests should cover populated usage, absent usage, JSON output, verbose logging, and empty response behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/perf_cli.rs -->
