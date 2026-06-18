# sources/control-plane/mayastor/jsonrpc/src/error.rs

Purpose: error model for JSON-RPC client requests and response parsing, including conversion to tonic gRPC status.

Important APIs/types/functions: `RpcCode` enumerates parse/invalid/method/internal plus `NotFound` and `AlreadyExists`. `Error` covers invalid JSON-RPC version/id, I/O, parse, connect, RPC error, and generic string errors. `From<RpcCode> for Code`, `From<Error> for tonic::Status`, `Display`, `std::error::Error`, and `From` conversions for `io::Error`, `serde_json::Error`, `&str`, and `String` are implemented.

Control flow: conversion maps `InvalidParams` to `InvalidArgument`, `NotFound` to `NotFound`, `AlreadyExists` to `AlreadyExists`, and most other RPC codes to `Internal`. Non-RPC client errors become tonic internal statuses with formatted messages.

State/persistence: no persistent state; error values carry messages and source errors.

Dependencies/integration: used by `jsonrpc::call`/`parse_reply` and by higher layers that expose JSON-RPC failures over tonic.

Risks: `std::error::Error::cause` is legacy and always returns `None`, so source chains are not exposed. `ConnectError` is defined but the current client maps Unix connect errors through `IoError`.

Test signals: unit tests in `src/test.rs` cover parse errors, invalid version/id, connect errors, and JSON-RPC errno mapping.
