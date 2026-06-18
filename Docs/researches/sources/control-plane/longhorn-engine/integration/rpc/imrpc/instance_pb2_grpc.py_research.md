# sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2_grpc.py

## Purpose
This generated gRPC module defines transport bindings for `imrpc.InstanceService`.

## Important APIs, types, and functions
- `InstanceServiceStub` exposes unary RPCs `InstanceCreate`, `InstanceDelete`, `InstanceGet`, `InstanceList`, `InstanceReplace`, and `VersionGet`; streaming RPCs `InstanceLog` and `InstanceWatch`.
- `InstanceServiceServicer` provides unimplemented base methods.
- `add_InstanceServiceServicer_to_server` registers service handlers.
- `InstanceService` provides experimental static RPC helper methods.

## Control flow
Stub initialization binds serializers/deserializers to `/imrpc.InstanceService/...` method paths. Server registration creates unary and streaming handlers. Default servicer implementations set unimplemented status and raise.

## State and persistence behavior
No persistent state is stored. Stub instances hold channel-bound methods; server instances receive registered handlers.

## Dependencies and integration points
Depends on `grpc`, `empty_pb2`, generated `imrpc.imrpc_pb2` for log/version response types, and `imrpc.instance_pb2` for request/response types. It is the transport surface for instance lifecycle APIs in newer instance-manager flows.

## Risks and edge cases
- `InstanceWatch` streams `Empty` messages according to this generated contract, unlike process watch which streams `ProcessResponse`; consumers must not assume identical semantics.
- Streaming methods require iterator lifecycle management.
- Generated import paths require `imrpc` to be importable.

## Test signals
Signals include import/stub construction, successful instance create/delete/get/list/replace calls against an implementation, streaming log/watch behavior, and version responses.
