# sources/control-plane/mayastor/jsonrpc/src/test.rs

Purpose: unit tests for the JSON-RPC Unix-socket client.

Important APIs/types/functions: `run_test` starts a per-thread Unix listener, invokes `call`, and runs assertion callbacks under `panic::catch_unwind`. Tests define `EmptyArgs`, request handlers returning raw JSON bytes, and result assertions for several `Result<R, Error>` types.

Control flow: each async test binds `/tmp/jsonrpc-ut.sock.<thread-id>`, spawns a one-shot server that reads the request, deserializes `Request`, writes handler output, then the client call is awaited and checked. Cleanup removes the socket after callback execution.

State/persistence: temporary Unix socket path under `/tmp`; no persistent test state. Per-thread suffix mitigates Rust parallel-test collisions.

Dependencies/integration: covers Tokio UnixListener/UnixStream behavior, serde request/response encoding, `nix::Errno`, and the crate error model.

Risks: `panic::UnwindSafe` is manually implemented for `Error`; server task panics would surface indirectly. `connect_error` uses a runtime manually and expects `ErrorKind::NotFound`.

Test signals: validates happy-path inversion, parse failures, invalid/missing version, wrong id, unit-result handling, and `ENOENT` to `RpcCode::NotFound`.
