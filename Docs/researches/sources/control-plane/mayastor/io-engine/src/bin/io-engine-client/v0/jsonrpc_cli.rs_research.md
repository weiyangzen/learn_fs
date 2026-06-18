<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/jsonrpc_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/jsonrpc_cli.rs

### Purpose
`jsonrpc_cli.rs` provides a v0 escape hatch for calling a raw SPDK JSON-RPC method through io-engine's gRPC JSON proxy. It is useful for methods not modeled by typed CLI subcommands.

### Important APIs, Types, And Functions
`JsonrpcArgs` carries a method name and optional raw JSON parameter string. `json_rpc_call` sends `JsonRpcRequest { method, params }` through `ctx.json`.

### Control Flow
The command does not parse the params locally; it forwards the string to the server. It logs that default output is JSON when the user did not request JSON explicitly, then prints `response.result` using colored JSON formatting. There is no separate table mode.

### State, Persistence, And Dependencies
The module persists no state and delegates all side effects to the named JSON-RPC method. Dependencies are v0 JSON protobuf types, `colored_json`, SNAFU status mapping, and tracing debug logs.

### Risks And Test Signals
Because params are raw strings, malformed JSON errors surface from the server. `to_colored_json_auto().unwrap()` can panic if the result is not valid JSON text. Tests should exercise empty params, invalid params propagation, successful raw call output, default-mode JSON behavior, and server errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v0/jsonrpc_cli.rs -->
