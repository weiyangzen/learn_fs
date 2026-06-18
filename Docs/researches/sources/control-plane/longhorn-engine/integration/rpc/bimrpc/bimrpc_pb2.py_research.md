# sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2.py

## Purpose
This generated protobuf module defines Python message classes and descriptors for `bimrpc/bimrpc.proto`, the backing image manager API used by Longhorn integration code.

## Important APIs, types, and functions
- Generated messages include `BackingImageSpec`, `BackingImageStatus`, `BackingImageResponse`, `DeleteRequest`, `GetRequest`, `ListResponse`, `VersionResponse`, `SyncRequest`, `SendRequest`, `FetchRequest`, `PrepareDownloadRequest`, `PrepareDownloadResponse`, `BackupCreateRequest`, `BackupStatusRequest`, and `BackupStatusResponse`.
- `ListResponse.backing_images` is a generated map from string to `BackingImageResponse`.
- `BackupCreateRequest.credential` is a generated map for credentials; labels are represented as repeated strings in this generated contract.
- `DESCRIPTOR` is registered through `_descriptor_pool.Default().AddSerializedFile(...)`, then `_builder` builds message classes into module globals.

## Control flow
The module has import-time generated setup only: import protobuf runtime, register the serialized file descriptor, build descriptors/messages, and optionally assign serialized offsets/options when Python descriptors are used.

## State and persistence behavior
It mutates the process-global protobuf descriptor pool and symbol database. It does not persist data itself; message instances are used by gRPC callers and servers.

## Dependencies and integration points
Depends on `google.protobuf` runtime and `google.protobuf.empty_pb2`. It pairs with `bimrpc_pb2_grpc.py`, whose stub/servicer serializers reference these message classes. It encodes the backing image manager service contract for delete/get/list/version/sync/send/fetch/download/backup/status/watch operations.

## Risks and edge cases
- This is generated code and should not be hand-edited; changes should come from the `.proto`.
- Runtime compatibility depends on the protobuf package version matching the generated style.
- API field names such as `gitCommit`, `buildDate`, and API version fields are part of the wire contract and can break callers if regenerated incompatibly.

## Test signals
Signals are import success, descriptor registration, message serialization/deserialization through `bimrpc_pb2_grpc`, and integration tests that call backing image manager APIs through clients built on this contract.
