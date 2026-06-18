# sources/cloud-native/containerd/internal/cri/bandwidth/interfaces.go

## Purpose

`interfaces.go` defines the abstraction for pod network bandwidth shaping.

## Important APIs, Types, and Functions

- `Shaper` declares `Limit`, `Reset`, `ReconcileInterface`, `ReconcileCIDR`, and `GetCIDRs`.
- `Limit` takes a CIDR plus egress and ingress quantities in bits per second.

## Control Flow

The file declares an interface only; concrete control flow is in Linux, unsupported, and fake implementations.

## State and Persistence Behavior

No state is stored here. Implementations own OS or in-memory state.

## Dependencies and Integration Points

It depends on Kubernetes `resource.Quantity`. CRI networking code can use this interface without directly depending on Linux `tc` or test fake implementations.

## Risks and Edge Cases

The contract permits overlapping CIDRs and aggregate limits, so implementations must avoid assuming unique IP-only matches. Unit tests should cover both ingress and egress semantics in concrete shapers.

## Test Signals

Compile-time satisfaction by `tcShaper`, `unsupportedShaper`, and `FakeShaper` is the main direct signal.
