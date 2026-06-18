<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/jsonrpc_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/jsonrpc_cli.rs

### Purpose
`jsonrpc_cli.rs` exposes raw JSON-RPC calls over the v1 JSON gRPC service. It is a compatibility and debugging escape hatch for SPDK or io-engine methods not covered by typed commands.

### Important APIs, Types, And Functions
`JsonrpcArgs` carries `method` and optional raw `params`. `json_rpc_call` sends `v1rpc::json::JsonRpcRequest` through `ctx.v1.json`.

### Control Flow
The command forwards method and parameter string unchanged. It treats default output as JSON, logs that fact at debug level, and prints the server `result` through colored JSON formatting.

### State, Persistence, And Dependencies
No local state is stored. Effects depend entirely on the invoked JSON-RPC method. Dependencies include v1 JSON protobufs, colored JSON, SNAFU status mapping, and tracing.

### Risks And Test Signals
Malformed params are detected server-side. Non-JSON or unexpected result text can panic in the colored JSON unwrap. Tests should cover empty params, successful raw method output, server parse errors, default-vs-json behavior, and error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/jsonrpc_cli.rs -->
