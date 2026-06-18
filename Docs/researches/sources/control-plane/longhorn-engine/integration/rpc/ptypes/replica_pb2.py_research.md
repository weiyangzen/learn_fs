# sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2.py

Purpose: generated protobuf definitions for replica-service RPC data structures and the `ReplicaService` descriptor.

Important APIs/types/functions: request/response types cover replica create/delete/get/open/close/reload/revert/snapshot/expand, disk remove/replace/prepare/mark, rebuilding flag, revision counter, unmap behavior, and snapshot count/size limits. State messages include `DiskInfo`, `Replica`, and `PrepareRemoveAction`.

Control flow: protobuf descriptors and classes are built at import time; no application logic exists in this module.

State and persistence behavior: process-global descriptors only. `Replica` and `DiskInfo` instances report remote replica state such as head, parent, chain, disks, revision counter, snapshot usage, and rebuild flags.

Dependencies and integration points: imports `google.protobuf.empty_pb2`. Consumed by `replica_pb2_grpc.py` and by `replica/replica_client.py`.

Risks: `ReplicaCreateRequest.size` is a string while expand and limits use integer fields, so tests should catch accidental type assumptions. Map-entry fields for disks, labels, and children depend on generated protobuf map behavior. Generated code should not be edited manually.

Test signals: instantiate key request/response messages, verify map fields and repeated chains round trip, and assert the service descriptor exposes all replica/disk/snapshot limit RPCs.
