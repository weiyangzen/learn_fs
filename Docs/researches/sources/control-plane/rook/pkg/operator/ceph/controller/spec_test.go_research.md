# sources/control-plane/rook/pkg/operator/ceph/controller/spec_test.go

## Purpose
`spec_test.go` validates representative shared pod-spec and endpoint construction behavior from `spec.go`.

## Important APIs, Types, and Functions
Tests cover `PodVolumes`, volume/mount matching for Ceph and Rook mounts, `CheckPodMemory`, daemon socket path/command builders, `GenerateLivenessProbeExecDaemon`, `DaemonFlags`, `NetworkBindingFlags`, `extractMgrIP`, `ConfigureExternalMetricsEndpoint`, `LogCollectorContainer`, `GetContainerImagePullPolicy`, `ApplyNetworkEnv`, and `GetDaemonsToSkipReconcile`.

## Control Flow, State, and Persistence
Most tests build Kubernetes structs in memory. External metrics tests use fake Kubernetes clients and mock Ceph command output for `mgr dump`, then assert EndpointSlice creation/update. Log collector tests compare generated bash script text. Skip-reconcile tests create fake Deployments and list them by label selector.

## Dependencies and Integration Points
The tests depend on fake clientsets, fake Rook clientsets, mock executors, Ceph version helpers, Kubernetes core/apps/discovery types, resource quantities, and Rook test volume helpers.

## Risks
Generated shell scripts are asserted as exact strings, which catches drift but can make harmless formatting edits noisy. Some tests rely on package-level `namespace` constants. External metrics tests use fake clients and do not model server-side EndpointSlice defaults. The network flag test has a guard that can skip mismatches when either side is empty, reducing failure sensitivity for empty-output regressions.

## Test Signals
Signals are strong for common daemon flags, network env encoding, logrotate script conversion, and external metrics endpoint IP selection. Missing signals include security contexts, minimal ceph.conf generation, PVC data volumes, subpath mutation, labels, TCP/rpcinfo probes, and error branches in endpoint creation.
