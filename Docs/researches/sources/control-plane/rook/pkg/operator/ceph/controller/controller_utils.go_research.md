# sources/control-plane/rook/pkg/operator/ceph/controller/controller_utils.go

## Purpose
`controller_utils.go` contains shared controller configuration, retry results, readiness gates, global operator setting parsers, panic recovery, and small naming helpers used across Ceph CR reconcilers.

## Important APIs, Types, and Functions
`OperatorConfig` describes operator namespace, image, service account, and watched namespace. `ClusterHealth` carries a cancelable health-check context. Requeue constants encode common retry timing. `DiscoveryDaemonEnabled()`, `SetCephCommandsTimeout()`, `SetAllowLoopDevices()`, `SetEnforceHostNetwork()`, `SetRevisionHistoryLimit()`, and `SetObcAllowAdditionalConfigFields()` read operator settings/env and update package/global state. Accessors expose loop-device allowance, host-network enforcement, revision history, and OBC key allowlist. `canIgnoreHealthErrStatusInReconcile()` allows known health errors (`MDS_ALL_DOWN`, `MGR_MODULE_ERROR`). `IsReadyToReconcile()` checks for a usable CephCluster and health state. `ClusterOwnerRef()`, `ClusterResource`, `RecoverAndLogException()`, and `NsName()` provide common metadata helpers.

## Control Flow, State, and Persistence
Most functions mutate in-process state rather than Kubernetes state. `exec.CephCommandsTimeout`, `loopDevicesAllowed`, global host-network enforcement, `revisionHistoryLimit`, and OBC allowlist are updated from settings. `IsReadyToReconcile()` lists CephClusters in the namespace, treats a deleting cluster with destructive cleanup policy as absent, and gates on health status before allowing controllers to run Ceph commands.

## Dependencies and Integration Points
This file integrates operator settings from `k8sutil`, Ceph API status and cleanup policy semantics, controller-runtime clients and reconcile results, `pkg/util/exec`, global Ceph API host-network enforcement, and logging helpers. Nearly every Ceph controller uses the readiness and retry constants.

## Risks
Global mutable state can leak between tests and between reconciles if settings change frequently. `IsReadyToReconcile()` takes the first CephCluster returned by list and does not select by name; single-cluster-per-namespace policy elsewhere makes this acceptable but important. Health gating depends on status details being populated consistently. Panics are logged but not surfaced as reconcile errors.

## Test Signals
`controller_utils_test.go` covers health-error allowlisting, timeout parsing, loop devices, host network parsing, revision history, readiness behavior for several CephCluster states, and OBC allowlist behavior. It does not cover panic recovery or multiple clusters in this helper.
