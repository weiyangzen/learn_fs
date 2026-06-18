# sources/control-plane/mayastor/io-engine/src/jsonrpc.rs

## Purpose
This module is the Rust adapter for SPDK JSON-RPC server methods. It lets handlers be written as serde-typed async Rust closures while SPDK calls a C ABI callback with raw JSON values and request pointers.

## Important APIs, types, and functions
`Code` maps project-level RPC errors to SPDK JSON-RPC integer codes, including standard JSON-RPC errors and negative errno-style codes for not found and already exists. `RpcErrorCode` is implemented by handler error types to choose an RPC code. `JsonRpcError` is the default error wrapper with `new`, `json_code`, `Display`, `Debug`, and `Error` implementations. `Result<T, E = JsonRpcError>` is the module alias.

`print_error_chain` flattens an error and all sources into one client-visible string. `extract_json_object` turns SPDK's `spdk_json_val` object pointer into the exact object substring by counting braces. `jsonrpc_register` boxes a Rust handler closure, converts the method name to `CString`, and registers `jsonrpc_handler` through `spdk_rpc_register_method`.

## Control flow
SPDK invokes `jsonrpc_handler` with a request, optional params, and the boxed handler pointer. The callback rebuilds the `Box<H>`, extracts or defaults params to `"null"`, deserializes to `P`, then schedules the user future on `Reactors::master()`. Handler success serializes `R` to JSON, writes the raw JSON value into SPDK's result writer, and ends the result. Handler failure logs the error chain and sends an SPDK error response with the handler's code. Parameter extraction/deserialization failures send invalid-params responses immediately.

## State and persistence behavior
Registered handler closures become leaked/runtime-owned pointers passed to SPDK. Requests are owned by SPDK; the module must finish or error them exactly once. No durable state is written.

## Dependencies and integration points
The module depends on `spdk_rs::libspdk` JSON-RPC functions, `serde`, `serde_json`, `futures`, `nix::errno`, and `Reactors`. It is used by server-side RPC modules that expose io-engine operations without hand-writing C JSON parsing.

## Risks and test signals
The callback reconstructs a `Box` from the raw handler pointer, which is risky if SPDK calls the method more than once because dropping the box would invalidate future invocations; review should confirm intended ownership or whether this should borrow instead. `extract_json_object` counts braces without string-literal awareness, so braces inside JSON strings can confuse it despite the comment that SPDK validates params. `CString::new(...).unwrap()` can panic if serialized output or error messages contain NUL bytes. Tests should cover multiple invocations of one registered method, object extraction with nested structures and strings, invalid params, and handler error mapping.
