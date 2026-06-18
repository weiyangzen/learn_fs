# sources/control-plane/mayastor/io-engine/src/grpc/v0/json_grpc.rs

Purpose: this small v0 service proxies gRPC requests to the local SPDK JSON-RPC endpoint. It preserves old clients that invoke arbitrary SPDK methods through the gRPC API.

Important APIs/types/functions: `JsonRpcSvc` stores a `Cow<'static, str>` JSON-RPC address. `json_rpc_call` implements generated `JsonRpc` by extracting method and params. `empty_as_none` converts an empty params string into `None`. `spdk_jsonrpc_call` parses params into `serde_json::Value`, calls `jsonrpc::call`, and pretty-serializes the JSON result.

Control flow: the service does not use the SPDK reactor submission helpers. It runs async JSON-RPC client I/O directly from the tonic handler, propagating parse/call/serialization failures through `jsonrpc::error::Error` into tonic via existing conversions.

State and persistence: no persistent state; only the configured RPC address is stored. The proxied method may mutate SPDK state outside this module’s type system.

Dependencies and integration points: depends on `io_engine_api::v0`, the `jsonrpc` helper crate, `serde_json`, and the address supplied by `server.rs`. It bypasses typed service validation and can reach SPDK methods not modeled by protobuf.

Risks: params are accepted as a raw JSON string, so malformed JSON fails at runtime; pretty serialization changes formatting but not semantic content; arbitrary method access can bypass higher-level locks and validation; the static lifetime comment indicates address ownership is a workaround. Test signals should exercise empty params, invalid JSON params, JSON-RPC failure propagation, and a harmless read-only SPDK method.
