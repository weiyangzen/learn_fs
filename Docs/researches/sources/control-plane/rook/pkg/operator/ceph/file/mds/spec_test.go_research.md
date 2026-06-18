# sources/control-plane/rook/pkg/operator/ceph/file/mds/spec_test.go

## Purpose
This test file validates generated MDS Deployment specs for pod networking and host networking, including labels, resources, priority class, service account, liveness probe override, and `--public-addr` behavior.

## Important APIs, Types, and Functions
`testDeploymentObject` builds a representative `CephFilesystem`, cluster spec, `Cluster`, and `mdsConfig`, then calls `makeDeployment`. `TestPodSpecs` validates the non-host-network Deployment with Rook's pod template tester. `TestHostNetwork` validates host-network-specific fields and absence of `--public-addr`.

## Control Flow, State, and Persistence
The helper sets MDS resources, priority class, image, data dir path, and a custom liveness probe initial delay of `900`. It asserts that the generated container carries the overridden liveness probe while preserving an exec handler. The tests then inspect the returned Deployment object in memory; no Kubernetes API state is created.

## Dependencies and Integration Points
The tests depend on Rook operator test utilities for label and pod template validation, fake clientsets, Ceph version constants, Kubernetes resource quantities, and controller daemon flag helpers. They cover the integration between `spec.go` and common Rook pod spec conventions.

## Risks
The helper contains assertions inside a subtest and then returns another deployment from a second `makeDeployment` call, which can obscure whether both calls are expected. Coverage is limited to host and default pod networking, not Multus or log collector sidecars. It does not exercise delete/scale helper functions.

## Test Signals
Signals include required Ceph labels, restart policy, service account, CPU/memory request and limit propagation, priority class, public address flag for pod networking, DNS policy for host networking, and liveness probe customization.
