<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rpc/server.go -->
## sources/control-plane/longhorn-engine/pkg/controller/rpc/server.go

Purpose: gRPC server adapter exposing `controller.Controller` as `enginerpc.ControllerService`, plus health, reflection, and profiler services.

Important APIs/types/functions: `GetControllerGRPCServer` creates a gRPC server with identity-validation interceptor and registers controller, health, reflection, and profiler services. `ControllerServer` converts internal replica/sync/volume/metrics structs to protobufs. RPC methods wrap volume start/shutdown/snapshot/revert/expand/frontend/flags/limits, replica list/get/create/delete/update/rebuild, journal list, version detail, and metrics. `ControllerHealthCheckServer` implements `Check`, `Watch`, and `List`.

Control flow: each RPC mostly delegates to controller methods and returns current volume/replica state. Health `Watch` sends status every second indefinitely. `JournalList` flushes sparse-tools operation journal.

State and persistence: server holds pointer to controller; no independent persistence. Controller operations may persist data in replicas.

Dependencies and integration points: generated `enginerpc`, gRPC health/reflection, profiler RPC, identity interceptors, metadata, sparse-tools journal, and controller package.

Risks: most errors are returned directly without gRPC status normalization, so clients see implementation strings. `ReplicaUpdate` dereferences `req.Address` without nil guard. Health check reports serving if controller pointer is non-nil, not necessarily if backend/frontend is healthy. `Watch` has no context cancellation handling in the loop.

Test signals: controller client integration tests, health probe tests, and identity validation tests. Unit tests should cover nil/malformed RPC payloads.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rpc/server.go -->
