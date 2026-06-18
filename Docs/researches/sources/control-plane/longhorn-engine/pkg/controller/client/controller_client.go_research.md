<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client.go -->
## sources/control-plane/longhorn-engine/pkg/controller/client/controller_client.go

Purpose: Go client wrapper for the Longhorn controller gRPC service.

Important APIs/types/functions: `ControllerServiceContext` owns `grpc.ClientConn` and generated client. `NewControllerClient` builds a service URL, opens an insecure gRPC client with identity-validation interceptor, and returns `ControllerClient`. Conversion helpers map `enginerpc.Volume`, `ControllerReplica`, and `SyncFileInfo` to internal `types`. Methods wrap volume lifecycle, snapshots, revert, expand, frontend control, unmap/snapshot limits, replica CRUD, rebuild prepare/verify/limit, journal, version detail, health check, and metrics.

Control flow: each method creates a `context.WithTimeout` using `GRPCServiceTimeout` and calls the generated client, wrapping errors with contextual messages. Health check opens a separate health client connection.

State and persistence: no persistence. Holds one client connection until `Close`.

Dependencies and integration points: integrates CLI/manager code with `enginerpc.ControllerService`, health service, identity interceptors, meta/version structs, and internal `types`.

Risks: insecure transport relies on local/trusted networking and identity metadata. Malformed server responses are now guarded for replica address nils, but other response fields may still be assumed. A visible duplicate context line around `VolumeUnmapMarkSnapChainRemovedSet` should be validated by compilation in this checkout.

Test signals: `controller_client_test.go` covers malformed `ControllerReplica` responses. Broader gRPC integration tests should exercise every wrapper and identity validation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client.go -->
