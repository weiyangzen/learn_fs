# sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2.py

## Purpose
This generated protobuf module defines the newer instance service data model for process and SPDK instances in Longhorn instance-manager.

## Important APIs, types, and functions
- Messages: `ProcessInstanceSpec`, `SpdkInstanceSpec`, `InstanceSpec`, `InstanceStatus`, `InstanceCreateRequest`, `InstanceDeleteRequest`, `InstanceGetRequest`, `InstanceResponse`, `InstanceListResponse`, `InstanceLogRequest`, and `InstanceReplaceRequest`.
- `SpdkInstanceSpec.replica_address_map` is a generated string-to-string map.
- `InstanceStatus.conditions` is a string-to-bool map.
- `InstanceSpec` carries name, type, volume name, port metadata, process/SPDK one-of-like nested specs, and `data_engine`.
- Some `backend_store_driver` fields are marked deprecated in generated options.

## Control flow
At import time, the module imports shared `common_pb2` and process-manager `imrpc_pb2`, registers `imrpc/instance.proto`, builds descriptors/messages, and applies serialized options.

## State and persistence behavior
It mutates the protobuf descriptor pool. Actual instance lifecycle state is remote and represented by generated messages.

## Dependencies and integration points
Depends on protobuf runtime, `empty_pb2`, shared `imrpc.common_pb2`, and `imrpc.imrpc_pb2` for `LogResponse`/`VersionResponse` references in the gRPC companion. It supports process-backed and SPDK-backed instance management.

## Risks and edge cases
- Deprecated `backend_store_driver` fields remain in request messages for compatibility; callers should prefer `data_engine` where applicable.
- Both process and SPDK specs are ordinary fields, so caller/server validation must enforce valid combinations.
- Generated code should not be hand-edited.

## Test signals
Signals include import success, correct construction/serialization of instance requests, map-field behavior for SPDK replica addresses and conditions, and use through `InstanceServiceStub`.
