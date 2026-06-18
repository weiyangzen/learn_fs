# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_stats.go

## Purpose

This controller file reserves a metrics API for sandbox controllers but currently marks it unimplemented.

## Important APIs, Types, and Functions

`(*Controller).Metrics` accepts a sandbox ID and returns `nil, errdefs.ErrNotImplemented`.

## Control Flow

The method is a direct stub. It does not inspect the controller store or containerd metrics.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It satisfies part of the sandbox controller surface and returns containerd API `types.Metric` when implemented in the future.

## Risks and Test Signals

Callers must not assume controller-level metrics are available. Compile coverage and CRI stats tests for the outer service are the current signals.
