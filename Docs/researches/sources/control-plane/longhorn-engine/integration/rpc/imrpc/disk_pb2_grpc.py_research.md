# sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2_grpc.py

## Purpose
This generated gRPC module defines the transport bindings for `imrpc.DiskService`.

## Important APIs, types, and functions
- `DiskServiceStub` exposes unary RPCs `DiskCreate`, `DiskDelete`, `DiskGet`, `DiskReplicaInstanceList`, `DiskReplicaInstanceDelete`, and `VersionGet`.
- `DiskServiceServicer` provides unimplemented server methods.
- `add_DiskServiceServicer_to_server` registers method handlers with serializers/deserializers.
- `DiskService` provides experimental static RPC helpers.

## Control flow
Stub construction binds request serializers and response deserializers to paths such as `/imrpc.DiskService/DiskCreate`. Server registration builds a handler map and attaches it to a supplied gRPC server. Default servicer methods raise unimplemented errors.

## State and persistence behavior
No persistent state is maintained. Stub instances store bound channel callables; servers receive registered handlers.

## Dependencies and integration points
Depends on `grpc`, `google.protobuf.empty_pb2`, and generated `imrpc.disk_pb2`. The handwritten `DiskClient` is a thin wrapper around this stub.

## Risks and edge cases
- No service-level retry/deadline behavior is embedded; callers handle call lifecycle.
- Generated imports require the `imrpc` package path to be resolvable.
- Hand edits would desynchronize from proto-generated message classes.

## Test signals
Signals include successful import/stub construction, correct method path binding, and integration tests successfully creating/getting/deleting disks or listing/deleting replica instances.
