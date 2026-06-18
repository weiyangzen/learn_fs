# sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2_grpc.py

## Purpose
This generated gRPC module defines client/server bindings for the instance-manager `ProcessManagerService`.

## Important APIs, types, and functions
- `ProcessManagerServiceStub` exposes unary RPCs `ProcessCreate`, `ProcessDelete`, `ProcessGet`, `ProcessList`, `ProcessReplace`, and `VersionGet`; streaming RPCs `ProcessLog` and `ProcessWatch`.
- `ProcessManagerServiceServicer` defines unimplemented server methods.
- `add_ProcessManagerServiceServicer_to_server` registers method handlers.
- `ProcessManagerService` provides experimental static RPC helpers.

## Control flow
Stub initialization binds channel methods to paths such as `/ProcessManagerService/ProcessCreate`. Server registration maps method names to unary or unary-stream handlers. Default servicer methods set `UNIMPLEMENTED` and raise.

## State and persistence behavior
The module stores no persistent state. Stub instances hold channel callables; process state is remote in instance-manager implementations.

## Dependencies and integration points
Depends on `grpc`, `empty_pb2`, and generated `imrpc_pb2`. It backs process-manager clients used by `test_launcher_basic.py` and common lifecycle helpers.

## Risks and edge cases
- The service path lacks the `imrpc.` package prefix, unlike disk/instance/proxy services; this is contractually important.
- `ProcessLog` and `ProcessWatch` are streaming APIs, so consumers need to manage iterators and cancellation.
- No deadlines or retries are generated.

## Test signals
Signals include successful process create/delete/get/list calls, process log/watch streams, replacement calls, version responses, and the launcher tests' observed process state transitions.
