# sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2.py

## Purpose
This generated protobuf module defines shared instance-manager enums used by other `imrpc` contracts.

## Important APIs, types, and functions
- Enum `BackendStoreDriver` with values `v1` and `v2`.
- Enum `DataEngine` with values `DATA_ENGINE_V1` and `DATA_ENGINE_V2`.
- `DESCRIPTOR` registers `imrpc/common.proto` with the protobuf descriptor pool.

## Control flow
At import time, protobuf runtime objects register the serialized descriptor and build enum descriptors into module globals.

## State and persistence behavior
The file mutates the process-global protobuf descriptor pool. It stores no external or persistent state.

## Dependencies and integration points
Depends on `google.protobuf` descriptor/builder runtime. It is imported by generated modules such as `instance_pb2.py` and `proxy_pb2.py` to share backend-store and data-engine enum types.

## Risks and edge cases
- The enum value names `v1`/`v2` are lowercase, which can be surprising for Python callers.
- Backward compatibility is important because these enums are embedded in multiple service requests.
- This generated file should be regenerated from `.proto`, not hand-edited.

## Test signals
Import success and successful serialization of messages that include `BackendStoreDriver` or `DataEngine` validate this module indirectly.
