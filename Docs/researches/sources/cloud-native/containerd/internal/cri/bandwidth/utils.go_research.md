# sources/cloud-native/containerd/internal/cri/bandwidth/utils.go

## Purpose

`utils.go` parses Kubernetes pod bandwidth annotations into validated ingress and egress resource quantities.

## Important APIs, Types, and Functions

- `minRsrc` and `maxRsrc` bound acceptable bandwidth values to `1k` through `1P`.
- `validateBandwidthIsReasonable` rejects values below/above those bounds.
- `ExtractPodBandwidthResources` reads `kubernetes.io/ingress-bandwidth` and `kubernetes.io/egress-bandwidth` annotations and returns parsed `resource.Quantity` pointers.

## Control Flow

If annotations are nil, the function returns nil quantities. For each supported key present, it parses the quantity string, validates bounds, and stores a pointer to the parsed value. Any parse or validation error aborts the function.

## State and Persistence Behavior

No state is stored. Returned quantities are new local values escaped to heap through pointers.

## Dependencies and Integration Points

It depends on Kubernetes `resource.ParseQuantity` and the annotation keys used by Kubernetes network bandwidth policy conventions. Callers feed these quantities into `Shaper` implementations.

## Risks and Edge Cases

Quantities are checked via `.Value()`, so unit interpretation must match bits-per-second expectations. Unknown annotations are ignored. Extremely small or large valid Kubernetes quantities are rejected by policy.

## Test Signals

No direct test is in this subset. Expected coverage comes from CRI networking tests that parse pod annotations and apply shaping.
