# sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2_grpc.py

Purpose: generated gRPC Python binding for `ShareManagerService`.

Important APIs/types/functions: `ShareManagerServiceStub` provides unary callables for `FilesystemTrim`, `Unmount`, and `Mount`. `ShareManagerServiceServicer` is the unimplemented server base. `add_ShareManagerServiceServicer_to_server` registers handlers. `ShareManagerService` exposes experimental static unary helpers.

Control flow: stub construction binds `/ShareManagerService/...` channel methods. Server registration maps each method to its request deserializer and response serializer.

State and persistence behavior: no local persistent state. Actual mount/unmount/trim state belongs to a concrete share-manager service.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `smrpc.smrpc_pb2`. Integrates with tests that exercise share-manager filesystem operations.

Risks: service path has no package prefix in the method string, unlike `ptypes.*` and `imrpc.*` generated services. That path difference matters for clients and test servers. Base servicer methods always return `UNIMPLEMENTED`.

Test signals: in-process server registration for all three paths; client call tests for request/response serialization; base-servicer negative tests.
