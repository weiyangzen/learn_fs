# sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2_grpc.py

Purpose: generated gRPC Python binding for `imrpc.ProxyEngineService`. It exposes client stubs, server base methods, server registration, and experimental one-shot static RPC helpers for the proxy engine API used by Longhorn integration tests.

Important APIs/types/functions: `ProxyEngineServiceStub` binds unary-unary callables for `ServerVersionGet`, volume operations, snapshot operations, backup/restore operations, replica membership/rebuild/mode operations, `MetricsGet`, and `RemountReadOnlyVolume`. `ProxyEngineServiceServicer` declares matching methods that set `UNIMPLEMENTED` and raise until a concrete test server overrides them. `add_ProxyEngineServiceServicer_to_server` registers each method with exact request deserializers and response serializers. `ProxyEngineService` mirrors the methods through `grpc.experimental.unary_unary`.

Control flow: constructing a stub stores channel callables keyed by fully qualified paths such as `/imrpc.ProxyEngineService/VolumeGet`. Server registration builds a dictionary of `grpc.unary_unary_rpc_method_handler` entries, wraps them in `grpc.method_handlers_generic_handler`, and adds them to the supplied server. The file has no business branching beyond generated method wiring.

State and persistence behavior: the module holds no persistent state. Stub instances hold channel-bound RPC callables; servicer base methods do not mutate durable state.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, and `imrpc.proxy_pb2`. It is tightly coupled to the generated `proxy_pb2` message classes and to the service path namespace `imrpc.ProxyEngineService`.

Risks: any mismatch between `proxy.proto`, `proxy_pb2.py`, and this generated file breaks serialization at runtime. The base servicer is not usable without overrides. The experimental static helper API is less stable than normal stubs. Because this is generated code, manual edits are likely to be overwritten.

Test signals: import the module with the same `PYTHONPATH` used by integration tests; instantiate a stub against a fake/in-process gRPC channel; verify server registration exposes every expected method path; assert base servicer methods return `UNIMPLEMENTED`; use descriptor or golden-path tests to catch request/response type drift.
