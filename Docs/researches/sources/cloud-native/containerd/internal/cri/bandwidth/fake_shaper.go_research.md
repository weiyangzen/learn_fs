# sources/cloud-native/containerd/internal/cri/bandwidth/fake_shaper.go

## Purpose

`fake_shaper.go` provides a minimal in-memory `Shaper` implementation for tests.

## Important APIs, Types, and Functions

- `FakeShaper` stores `CIDRs` and `ResetCIDRs`.
- `Limit`, `ReconcileInterface`, and `ReconcileCIDR` return `errdefs.ErrNotImplemented`.
- `Reset` appends the CIDR to `ResetCIDRs`.
- `GetCIDRs` returns the configured `CIDRs`.

## Control Flow

Methods either mutate simple slices, return stored data, or report not implemented.

## State and Persistence Behavior

State is in-memory on the struct instance. No OS shaping or persistence occurs.

## Dependencies and Integration Points

It depends on containerd `errdefs` and Kubernetes `resource.Quantity` to satisfy the `Shaper` interface. It is intended for unit tests of code that only needs reset/list behavior.

## Risks and Edge Cases

Most methods are deliberately unimplemented, so using it in code paths expecting actual shaping will fail. `GetCIDRs` returns the slice directly, so callers could mutate it.

## Test Signals

Coverage is indirect through tests that instantiate `FakeShaper` in the broader CRI bandwidth or cleanup code.
