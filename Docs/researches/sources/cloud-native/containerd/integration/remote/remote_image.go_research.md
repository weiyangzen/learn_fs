# sources/cloud-native/containerd/integration/remote/remote_image.go

## Purpose

`remote_image.go` adapts the upstream Kubernetes CRI image client to the older method shapes used by containerd integration tests.

## Important APIs, Types, and Functions

- `ImageService` wraps `upstreamapi.ImageManagerService`.
- `NewImageService` creates a remote image client with an endpoint and connection timeout.
- `Close` closes the upstream service and tolerates a nil receiver.
- `ListImages`, `ImageStatus`, `PullImage`, `RemoveImage`, and `ImageFsInfo` bridge legacy calls to the current CRI client.
- `PullImage` clones `ImageSpec` when a runtime handler is supplied so it can populate `RuntimeHandler` without mutating the caller's original annotations map.

## Control Flow

Every method uses `context.Background()` and delegates directly to the upstream CRI client. Response-shaping methods unwrap nested response fields such as `ImageStatusResponse.Image` and `ImageFsInfoResponse.ImageFilesystems`.

## State and Persistence Behavior

The adapter owns only the upstream client handle. It does not cache image data or persist state; image persistence is handled by the CRI implementation under test.

## Dependencies and Integration Points

It depends on `k8s.io/cri-client`, CRI API/runtime types, `grpc.CallOption` compatibility, and Go `maps.Clone`. It is used heavily by integration tests that expect pre-upstream client method signatures.

## Risks and Edge Cases

Using `context.Background()` means callers cannot cancel individual operations through this wrapper. `PullImage` must clone annotations before injecting `RuntimeHandler` to avoid test cross-contamination. Nil `ImageSpec` is passed through unchanged, so upstream validation owns that error.

## Test Signals

There is no dedicated test for this file. It is indirectly covered by image pull/list/status/remove operations in upgrade, restart, truncindex, volume, and Windows integration tests.
