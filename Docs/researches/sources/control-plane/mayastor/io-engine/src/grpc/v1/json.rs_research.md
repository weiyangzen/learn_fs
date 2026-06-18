# sources/control-plane/mayastor/io-engine/src/grpc/v1/json.rs

Purpose: this v1 service proxies typed gRPC JSON-RPC requests to the local SPDK JSON-RPC endpoint, equivalent to the v0 proxy but using v1 protobuf messages.

Important APIs/types/functions: `JsonService` stores the JSON-RPC address as `Cow<'static, str>`. `json_rpc_call` extracts the method and raw parameter string. `empty_as_none` treats empty params as absent. `spdk_jsonrpc_call` parses params into `serde_json::Value`, calls `jsonrpc::call`, and pretty-prints the returned JSON value.

Control flow: the handler performs JSON parsing and network/client I/O directly in the tonic async context. There is no resource locking, request serialization, or reactor submission, because it delegates to the SPDK JSON-RPC service rather than directly touching reactor-bound Rust objects.

State and persistence: no local state beyond the configured address. Proxied methods may mutate SPDK state externally to the typed gRPC locking model.

Dependencies and integration points: depends on `io_engine_api::v1::json`, `jsonrpc`, `serde_json`, and the RPC address passed by `server.rs`.

Risks: arbitrary method proxying can bypass typed validation and locks; invalid params fail dynamically; pretty JSON response formatting may not match clients expecting compact JSON; address lifetime is acknowledged as a workaround. Test signals should include empty params, malformed params, JSON-RPC transport failures, and read-only SPDK calls.
