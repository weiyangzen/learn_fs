# sources/cloud-native/cri-o/server/version.go

## Purpose
Implements the CRI `Version` RPC.

## Important APIs, Types, And Functions
Constants `kubeAPIVersion = "0.1.0"` and `containerName = "cri-o"`. `(*Server).Version(ctx, req)` returns a `types.VersionResponse`.

## Control Flow
Looks up build/runtime version information via `internal/version.Get(false)`, wraps lookup errors, and returns Kubernetes API version, runtime name, CRI-O runtime version, and runtime API version `v1`.

## State And Persistence
Read-only. It reads version metadata but does not mutate server state.

## Dependencies And Integration Points
Directly serves kubelet CRI version negotiation and `crictl version` style calls.

## Risks And Test Signals
The Kubernetes API version constant is intentionally legacy per the comment. Test coverage asserts non-empty fields and exact runtime API version.
