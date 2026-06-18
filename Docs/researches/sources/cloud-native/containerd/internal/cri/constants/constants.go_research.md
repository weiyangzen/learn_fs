# sources/cloud-native/containerd/internal/cri/constants/constants.go

## Purpose

`constants.go` defines shared CRI constants for the containerd namespace and supported CRI API version.

## Important APIs, Types, and Functions

- `K8sContainerdNamespace = "k8s.io"` is the namespace used for containerd operations from CRI.
- `CRIVersion = "v1"` is the latest CRI version supported by the plugin.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The constants are compile-time values and do not persist state directly.

## Dependencies and Integration Points

These constants integrate CRI code with containerd namespaces and CRI version reporting.

## Risks and Edge Cases

Changing either constant is a compatibility-affecting API behavior change for Kubernetes integration and containerd object lookup.

## Test Signals

Coverage is indirect through CRI version responses and namespace-scoped integration tests.
