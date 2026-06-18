# sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2.py

## Purpose
This generated protobuf module defines the process-manager API messages used by Longhorn instance-manager integration tests.

## Important APIs, types, and functions
- Messages: `ProcessSpec`, `ProcessStatus`, `ProcessCreateRequest`, `ProcessDeleteRequest`, `ProcessGetRequest`, `ProcessResponse`, `ProcessListRequest`, `ProcessListResponse`, `LogRequest`, `ProcessReplaceRequest`, `LogResponse`, and `VersionResponse`.
- `ProcessStatus.conditions` is a string-to-bool map.
- `ProcessListResponse.processes` is a string-to-`ProcessResponse` map.
- `ProcessResponse.deleted` marks deleted process records.
- `VersionResponse` carries instance-manager and proxy API version/min-version fields.

## Control flow
The module registers the serialized `imrpc/imrpc.proto` descriptor and builds message classes at import time. There is no custom control flow beyond generated protobuf setup.

## State and persistence behavior
It registers descriptors in memory. Actual process state lives in the remote instance manager and is represented by message instances.

## Dependencies and integration points
Depends on protobuf runtime and `empty_pb2`. It pairs with `imrpc_pb2_grpc.py` and handwritten process manager clients used by launcher tests and common helpers.

## Risks and edge cases
- The generated service package path is `/ProcessManagerService/...` rather than `/imrpc.ProcessManagerService/...`, so clients and servers must agree on this path.
- Map field semantics may hide ordering; tests should avoid assuming process map order.
- Generated code should be regenerated, not hand-edited.

## Test signals
Signals include import success, correct construction of process specs/responses, process list map behavior, and gRPC serialization through `ProcessManagerServiceStub`.
