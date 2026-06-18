# sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2.py

## Purpose
This generated protobuf module defines the instance-manager disk service messages and `DiskType` enum.

## Important APIs, types, and functions
- Messages: `Disk`, `ReplicaInstance`, `DiskCreateRequest`, `DiskGetRequest`, `DiskDeleteRequest`, `DiskReplicaInstanceListRequest`, `DiskReplicaInstanceListResponse`, `DiskReplicaInstanceDeleteRequest`, and `DiskVersionResponse`.
- Enum `DiskType` with `filesystem` and `block`.
- `DiskReplicaInstanceListResponse.replica_instances` is a map from string to `ReplicaInstance`.
- `DiskReplicaInstanceDeleteRequest` contains the misspelled field `replcia_instance_name`, which the client must use.

## Control flow
The module registers the serialized `imrpc/disk.proto` descriptor, builds message/enum classes, and assigns serialized metadata at import time.

## State and persistence behavior
It mutates the process-global protobuf descriptor pool and symbol registry only. Disk state is remote service state represented by message instances.

## Dependencies and integration points
Depends on protobuf runtime and `empty_pb2`. It pairs with `disk_pb2_grpc.py` and the handwritten `rpc/disk/disk_client.py` wrapper.

## Risks and edge cases
- The misspelled field name is part of the generated Python API and likely the wire-compatible proto; changing it requires coordinated proto/server/client regeneration.
- Disk sizes and block counts are 64-bit integer fields, so callers must avoid lossy conversions.
- Generated code should not be hand-edited.

## Test signals
Signals include import success, construction of disk request/response messages, map field behavior for replica instances, and successful use through `DiskServiceStub`.
