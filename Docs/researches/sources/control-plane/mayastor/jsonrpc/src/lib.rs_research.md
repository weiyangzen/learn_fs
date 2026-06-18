# sources/control-plane/mayastor/jsonrpc/src/lib.rs

Purpose: async JSON-RPC 2.0 client over Unix domain sockets.

Important APIs/types/functions: public `Request`, `Response`, and `RpcError` structs are serde-serializable/deserializable. `call<A, R>` builds request id `0`, serializes optional params, connects via `tokio::net::UnixStream`, writes and shuts down the socket, reads the full response, and delegates to private `parse_reply<T>`.

Control flow: `parse_reply` deserializes `Response`, accepts missing `jsonrpc` but rejects non-`2.0`, requires numeric id `0`, maps JSON-RPC standard negative codes and negative errno values to `RpcCode`, returns `Error::RpcError` when `error` is present, otherwise deserializes `result` or JSON null into `T`.

State/persistence: no long-lived state; each call opens one Unix socket connection and consumes one complete request/response exchange.

Dependencies/integration: depends on Tokio async I/O, serde JSON, nix errno mapping, tracing logs, and the local `error` module.

Risks: fixed request id `0` prevents multiplexing and assumes one in-flight request per socket. Missing `jsonrpc` is accepted for compatibility. `reply.result.unwrap_or(Null)` can turn absent result into unit success but will parse-error for non-unit expected types.

Test signals: tests exercise normal reply, invalid JSON, missing/wrong version, wrong id, empty result behavior, connect failure, and RPC error conversion.
