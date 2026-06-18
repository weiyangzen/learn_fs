## sources/distributed-fs/beegfs-rust/shared/src/grpc.rs

### Purpose
Provides shared gRPC helper macros and utilities for BeeGFS Rust services using tonic: handler forwarding, response streams, error-to-status mapping, and required-field validation.

### Important APIs, Types, and Functions
- `impl_grpc_handler!` generates tonic service methods for unary and server-streaming RPCs by forwarding to a handler module/function with `self.app`.
- `StreamSender<Msg>` wraps an `mpsc::Sender<Result<Msg, Status>>` and exposes async `send`.
- `RespStream<T>` aliases a pinned boxed Tokio stream of tonic results.
- `resp_stream(buf_size, source_fn)` creates a channel-backed response stream and maps source errors to gRPC statuses.
- `AnyhowContextStatus` stores a tonic `Code` plus optional source error.
- `AnyhowErrorStatusExt::status_code` wraps errors with a desired gRPC status code.
- `process_grpc_handler_error` walks an anyhow error chain, extracts the last status-code wrapper, logs, and returns `tonic::Status`.
- `required_field` converts `Option<T>` protobuf fields into `anyhow::Result<T>`.

### Control Flow and State
Generated handlers call the real handler asynchronously, convert `Ok` values to tonic responses, and convert errors through `process_grpc_handler_error`. `resp_stream` spawns a producer task; source errors are sent as a final stream error unless the receiver closed early.

### Dependencies and Integration Points
Uses tonic `Status`/`Code`, Tokio `mpsc`, `tokio_stream`, and anyhow. It is gated by the `grpc` feature in `lib.rs`, and depends on consuming service structs having an `app` field.

### Risks and Edge Cases
The macro is not fully generic despite being shared; it assumes `self.app` and handler module naming. Error responses include the full stringified error chain, which may leak internal detail. `process_grpc_handler_error` defaults to `Code::Unknown` despite comments mentioning generic internal status. Stream producer tasks can outlive request context until channel closure or source completion.

### Test Signals
No local tests. Tests should assert status-code extraction, required-field errors, receiver-cancel behavior, and generated handler behavior in a minimal tonic service.
