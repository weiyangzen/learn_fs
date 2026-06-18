# sources/control-plane/ceph-csi/internal/csi-common/utils.go

Purpose: shared CSI utility layer for endpoint parsing, default server construction, capability construction, gRPC middleware/logging/restart behavior, request ID extraction, filesystem stats, and access-mode classification.

Important APIs/types/functions: key functions include `parseEndpoint()`, `NewVolumeCapabilityAccessMode()`, `NewDefaultNodeServer()`, `NewDefaultIdentityServer()`, `NewDefaultControllerServer()`, `NewControllerServiceCapability()`, `NewGroupControllerServiceCapability()`, `NewMiddlewareServerOption()`, `NewMiddlewareStreamServerOption()`, `GetIDFromReplication()`, `FilesystemNodeGetVolumeStats()`, `IsBlockMultiNode()`, `IsFileRWO()`, `IsReaderOnly()`, and `IsBlockMultiWriter()`. Internal middleware/helpers include `getReqID()`, `contextIDInjector()`, `wrapperServerStream`, `streamInterceptor()`, `logGRPC()`, `logSlowGRPC()`, `killOnSlowGRPCWithThreshold()`, `panicHandler()`, and `requirePositive()`.

Control flow: middleware chains inject a monotonically increasing context ID, derive request IDs from CSI/replication/volume group requests, log sanitized requests/responses, optionally log slow calls after context cancellation, optionally kill the process when unary handlers exceed ten minutes, and recover panics into internal errors. Stream middleware injects IDs and logs metadata snapshot requests. Filesystem stats verify mountpoint status, use Kubernetes statfs metrics, clamp negative usage values, optionally include inodes, and return a healthy volume condition. Access-mode helpers scan capability lists for block/multi-node/RWO/reader-only/multi-writer properties.

State and persistence: package-level atomic `id` labels requests. Package variable `osExit` is overrideable in tests. No durable state is written. `FilesystemNodeGetVolumeStats()` reads mount and filesystem state.

Dependencies and integration points: used by both standard CSI and CSI-addons servers, RBD replication ID extraction, RBD reclaim-space capability checks, and node stats implementations. Depends on CSI and CSI-addons protobufs, grpc middleware, proto sanitizer, klog/logging, Kubernetes mount-utils and volume metrics.

Risks: request ID extraction must track proto evolution, especially deprecated replication `VolumeId` versus `ReplicationSource`. `killOnSlowGRPC` exits the process for stuck unary calls, with reclaimspace excluded by prefix. Access helpers assume non-nil access modes in some paths (`IsBlockMultiNode()`), so callers must pass well-formed capabilities. Metrics conversion logs but does not fail for unavailable available/used values, while capacity/inodes failures do fail.

Test signals: broad tests cover request IDs, filesystem stats, positive clamping, access-mode helpers, and slow-GRPC restart/exclusion behavior. More tests could cover endpoint parsing, panic recovery, stream interceptor request IDs, and nil capability robustness.
