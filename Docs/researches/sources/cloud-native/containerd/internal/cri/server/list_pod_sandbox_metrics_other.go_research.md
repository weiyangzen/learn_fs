
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_other.go -->
# sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_other.go

## Purpose

This non-Linux build file marks CRI `ListPodSandboxMetrics` as unsupported on non-Linux platforms.

## Important APIs, Types, and Functions

The only function is `(*criService).ListPodSandboxMetrics`, which returns a gRPC `Unimplemented` status.

## Control Flow

The function ignores the request and immediately returns nil response plus `status.Errorf(codes.Unimplemented, "ListPodSandboxMetrics not implemented on this platform")`.

## State and Persistence Behavior

No CRI, runtime, cgroup, or filesystem state is read or changed.

## Dependencies and Integration Points

Dependencies include context, gRPC status/codes, and CRI runtime API. It complements the Linux implementation selected by build tags.

## Risks and Edge Cases

Metrics collection is unavailable on non-Linux even for platforms that may expose some analogous data. Clients must handle gRPC unimplemented cleanly.

## Test Signals

Platform-specific tests should check the unimplemented status code and nil response.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_other.go -->
