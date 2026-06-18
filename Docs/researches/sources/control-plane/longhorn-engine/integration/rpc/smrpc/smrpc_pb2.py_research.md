# sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2.py

Purpose: generated protobuf definitions for share-manager RPCs.

Important APIs/types/functions: exports `FilesystemTrimRequest` with `encrypted_device` boolean and a `ShareManagerService` descriptor with `FilesystemTrim`, `Unmount`, and `Mount` unary RPCs.

Control flow: import-time descriptor registration builds message and service descriptors. No implementation logic exists.

State and persistence behavior: only protobuf descriptors are registered. Mount/trim state is remote in the share-manager service.

Dependencies and integration points: imports `google.protobuf.empty_pb2`; consumed by `smrpc_pb2_grpc.py` and share-manager RPC clients/servers.

Risks: small schema means changes are easy to miss without descriptor tests. The generated Go package option ties it to Longhorn share-manager types. Manual edits are overwritten.

Test signals: import and instantiate `FilesystemTrimRequest`; descriptor test for the three service methods and their request/response types.
