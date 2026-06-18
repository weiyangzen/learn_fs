
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_other.go -->
# sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_other.go

## Purpose

This non-Linux build file implements `ListMetricDescriptors` as an unimplemented CRI method on unsupported platforms.

## Important APIs, Types, and Functions

The only function is `(*criService).ListMetricDescriptors`, returning a gRPC status error with code `Unimplemented`.

## Control Flow

The handler ignores request contents and immediately returns nil response plus `status.Errorf(codes.Unimplemented, ...)`.

## State and Persistence Behavior

No state is read or mutated.

## Dependencies and Integration Points

Dependencies include context, gRPC status/codes, and CRI runtime API. The file is selected for `!linux` builds and complements the Linux implementation.

## Risks and Edge Cases

Metrics descriptor discovery is unavailable on non-Linux platforms even where some metrics might theoretically be collectable. Clients must handle gRPC unimplemented.

## Test Signals

Platform-specific tests should assert the exact `codes.Unimplemented` status and nil response.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_other.go -->
