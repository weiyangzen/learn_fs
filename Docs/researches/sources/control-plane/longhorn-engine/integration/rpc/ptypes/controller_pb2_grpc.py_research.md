# sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2_grpc.py

Purpose: generated gRPC Python binding for `ptypes.ControllerService`.

Important APIs/types/functions: `ControllerServiceStub` exposes unary-unary methods for volume get/start/shutdown/snapshot/revert/expand/frontend, snapshot limit settings, `VolumeIO`, replica list/get/create/delete/update/prepare/verify rebuild, rebuild sync limit get/set, `JournalList`, `VersionDetailGet`, and `MetricsGet`. `ControllerServiceServicer` is an unimplemented base. `add_ControllerServiceServicer_to_server` registers serializers/deserializers. `ControllerService` provides experimental static unary calls.

Control flow: stub construction binds channel callables to `/ptypes.ControllerService/...`. Server registration builds `grpc.unary_unary_rpc_method_handler` entries and attaches a generic handler to a server.

State and persistence behavior: no durable state. Stub instances keep channel method handles; server state belongs to concrete servicer implementations.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `ptypes.controller_pb2`. It is the Python transport layer for controller RPC integration tests.

Risks: generated request/response wiring must stay aligned with `controller_pb2.py`. The base servicer always returns `UNIMPLEMENTED`. The experimental static API should not be the primary extension point.

Test signals: import and stub-construction smoke tests; fake/in-process server tests for registration paths; golden tests for method-to-message mappings, especially mutating RPCs returning `Volume` versus `Empty`.
