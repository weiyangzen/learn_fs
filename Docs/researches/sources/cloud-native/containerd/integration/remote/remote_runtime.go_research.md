# sources/cloud-native/containerd/integration/remote/remote_runtime.go

## Purpose

`remote_runtime.go` adapts the upstream Kubernetes CRI runtime client to the legacy integration-test interface and keeps an additional raw gRPC client connection for streaming RPCs not exposed in the same shape by the upstream abstraction.

## Important APIs, Types, and Functions

- `RuntimeService` stores an upstream `RuntimeService`, raw `RuntimeServiceClient`, and raw `grpc.ClientConn`.
- `NewRuntimeService` creates both the upstream runtime service and raw connection, cleaning up on partial failure.
- `newRuntimeClientConn` resolves endpoint/dialer with CRI utilities, sets insecure credentials, authority, context dialer, and a 16 MiB max receive size.
- `clientTargetForAddress` prefixes Unix socket paths with `passthrough:///` so gRPC does not DNS-resolve socket paths.
- Methods wrap CRI operations: version, sandbox lifecycle/resources/status/list, container lifecycle/status/resources/stats/log reopen, exec/attach/port-forward, runtime config/status, and event streaming.
- `GetContainerEvents` calls the raw streaming client directly.

## Control Flow

Most wrapper methods call the upstream service with `context.Background()` and translate request/response shape where the legacy tests expect plain IDs or statuses. `Close` joins errors from closing both the upstream service and raw gRPC connection.

## State and Persistence Behavior

The adapter keeps connection state only. Runtime, sandbox, container, log, and stats state remains in the CRI server under test.

## Dependencies and Integration Points

The file integrates `k8s.io/cri-client`, CRI runtime API, gRPC, insecure credentials, and CRI endpoint dialer utilities. It is central to integration tests that need a stable client surface while Kubernetes CRI client APIs evolve.

## Risks and Edge Cases

Per-call `context.Background()` prevents test-level cancellation through most wrapper methods. Socket targets must use `passthrough:///`; otherwise gRPC treats paths as DNS names and Unix stream calls can fail. The wrapper must close both client layers to avoid leaking sockets.

## Test Signals

`remote_runtime_test.go` specifically covers Unix socket event streaming through `newRuntimeClientConn`. Most integration tests indirectly cover the remaining wrapper methods.
