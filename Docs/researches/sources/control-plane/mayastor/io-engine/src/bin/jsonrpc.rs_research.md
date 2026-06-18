<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/jsonrpc.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/jsonrpc.rs

### Purpose
This standalone binary is a raw SPDK JSON-RPC client over a Unix socket. It is retained as a low-level debugging tool even though typed gRPC commands cover most user workflows.

### Important APIs, Types, And Functions
`Opt` parses the socket path and subcommand. `Sub::Raw` carries a method and optional JSON argument string. The Tokio `main` calls `jsonrpc::call`.

### Control Flow
The binary parses CLI args, matches `raw`, parses the optional argument into `serde_json::Value` when present, calls the method with `Some(args)` or `None`, pretty-prints the returned JSON, and prints the result. If pretty-printing a returned value fails in the argument path, it debug-prints the value and returns an empty string.

### State, Persistence, And Dependencies
The binary stores no state. Its effects depend entirely on the JSON-RPC method invoked through the socket, defaulting to `/var/tmp/mayastor.sock`. Dependencies include clap, serde_json, the repository `jsonrpc` crate, Tokio, and version info.

### Risks And Test Signals
Raw methods can mutate SPDK state without typed validation. The code assumes argument strings are JSON and returns parse errors locally. Tests should cover no-arg and arg calls, invalid JSON, socket failures, method errors, and pretty-printed output stability.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/jsonrpc.rs -->
