# File Research: sources/block-storage/stratisd/src/jsonrpc/server/server.rs

## Purpose

Implements the min JSON-RPC Unix socket server, including request dispatch, ancillary FD handling, async listener/request/response futures, and server startup.

## Main Types and Behavior

- `StratisParams::process` is the central dispatcher from `StratisParamType` to server handlers.
- `StratisServer` owns the engine and Unix listener, accepts requests, spawns per-request tasks, and sends responses.
- `handle_cmsgs` extracts at most one `SCM_RIGHTS` file descriptor and closes extras on protocol violation.
- `try_recvmsg` receives JSON plus optional FD and builds `StratisParams`.
- `try_sendmsg` serializes and sends the response.
- `StratisUnixRequest` waits for read readiness and deserializes a request.
- `StratisUnixResponse` waits for write readiness and sends a response.
- `StratisUnixListener` binds a nonblocking Unix stream socket, creating/removing the socket path as needed.
- `run_server` spawns the server task on the configured socket path.

## Integration Points

This is the transport and dispatch backbone for `stratis-min`. It integrates with the engine, server pool/key/filesystem/report modules, systemd readiness notification, and JSON-RPC constants/interface types.

## Notable Semantics

`expects_fd!` enforces FD expectations per method. Unexpected FDs are closed before returning protocol errors. The listener uses `listen` backlog `0`, so connection queuing behavior is intentionally minimal.
