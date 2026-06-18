# sources/control-plane/longhorn-engine/integration/rpc/disk/disk_client.py

## Purpose
This wrapper provides a simple gRPC client for the instance-manager disk service used in Longhorn integration tests.

## Important APIs, types, and functions
- `DiskClient.__init__(url)` creates an insecure channel and `DiskServiceStub`.
- `version_get` calls service version.
- `disk_create`, `disk_get`, and `disk_delete` construct the corresponding disk protobuf requests.
- `disk_replica_instance_list` lists replica instances on a disk.
- `disk_replica_instance_delete` deletes a named replica instance from a disk.

## Control flow
Each public method synchronously invokes one generated stub method with a protobuf request from `imrpc.disk_pb2`. No response transformation is performed; generated protobuf responses are returned directly.

## State and persistence behavior
The client stores only address/channel/stub in memory. Server-side side effects include creating/deleting disks and deleting replica-instance records. No local persistence exists.

## Dependencies and integration points
Depends on `grpc`, `imrpc.disk_pb2`, `imrpc.disk_pb2_grpc`, and `empty_pb2`. It integrates tests with the instance-manager disk service contract.

## Risks and edge cases
- `disk_replica_instance_delete` passes `replcia_instance_name`, matching the misspelled generated proto field. This typo is wire-contract significant; correcting it only in the client would break calls until the proto changes.
- No RPC timeouts/deadlines are set.
- The wrapper does not validate disk type/name/uuid consistency before issuing destructive delete calls.

## Test signals
Signals include successful disk create/get/delete responses, version response fields, replica instance list contents, and expected server-side deletion of replica instances.
