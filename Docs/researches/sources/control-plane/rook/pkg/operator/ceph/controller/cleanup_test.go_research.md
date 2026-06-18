# sources/control-plane/rook/pkg/operator/ceph/controller/cleanup_test.go

## Purpose
`cleanup_test.go` provides focused unit tests for cleanup Job template construction and force-delete annotation parsing.

## Important APIs, Types, and Functions
`TestJobTemplateSpec` creates a `CephCluster`, a `CephFilesystemSubVolumeGroup` with TypeMeta Kind, and a two-entry config map, then asserts the cleanup command uses the resource kind and that five env vars are present. `TestForceDeleteRequested` toggles `rook.io/force-deletion` and checks the boolean result.

## Control Flow, State, and Persistence
The tests instantiate pod template objects in memory only; no Kubernetes Job is submitted. The env count implicitly confirms three host-path-related env vars plus two resource-specific entries when `DataDirHostPath` is set.

## Dependencies and Integration Points
The tests depend on Ceph CR structs, metav1 object metadata, and the cleanup constants from `cleanup.go`.

## Risks
The env count assertion is brittle if common cleanup env vars change. The test does not assert container image, security context, volume definitions, restart policy, service account, resource requests, priority class, or behavior when `DataDirHostPath` is empty. It also covers only lowercase `"true"` despite production using case-insensitive parsing.

## Test Signals
Signals are basic command-kind plumbing and annotation enablement. Important missing signals are job submission/replacement behavior, privileged settings, cleanup resources, and failure propagation.
