# sources/cloud-native/containerd/internal/cri/bandwidth/unsupported.go

## Purpose

`unsupported.go` provides the non-Linux `Shaper` implementation.

## Important APIs, Types, and Functions

- `unsupportedShaper` is the concrete non-Linux type.
- `NewTCShaper` returns an unsupported shaper.
- `Limit`, `ReconcileInterface`, and `ReconcileCIDR` return `errdefs.ErrNotImplemented`.
- `Reset` is a no-op success.
- `GetCIDRs` returns an empty slice.

## Control Flow

All methods are simple stubs, allowing non-Linux builds to compile while reporting unsupported operations where shaping would be required.

## State and Persistence Behavior

There is no shaping state and no persistence.

## Dependencies and Integration Points

It depends on build tag `!linux`, containerd `errdefs`, and Kubernetes resource quantities. It satisfies the same `Shaper` interface used by platform-neutral code.

## Risks and Edge Cases

Callers must tolerate `ErrNotImplemented` on non-Linux platforms. `Reset` returning nil can hide cleanup requests for limits that were never applied, which is reasonable for unsupported platforms but should be documented at call sites.

## Test Signals

Compile success on non-Linux platforms and any platform-specific CRI tests provide coverage.
