# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/integration_test.go

## Purpose
This file is an end-to-end unit integration test for OSD create and update reconciliation. It drives `Cluster.Start()` through initial provisioning, no-op updates, scale-up, cancellation and resume, status failures, Deployment update failures, Deployment creation failures, malformed device sets, and dangling ConfigMap cleanup.

## Important APIs, Types, and Helpers
`TestOSDIntegration` wraps `testOSDIntegration()` in a timeout and shortens OSD update ticker durations. `testOSDIntegration()` builds a fake Kubernetes environment with ready nodes, complex Job reactors, ConfigMap watch reactors, Deployment reactors, fake CephCluster runtime object, controller-runtime fake client, and a mock Ceph executor. The test stubs `updateConditionFunc` because the fake environment does not include the full Rook client path.

`osdIntegrationTestExecutor()` handles Ceph commands used by the reconcile path: auth key creation, `osd ok-to-stop`, `osd ls`, `osd tree`, device class lookups, device class list, `osd df`, and `versions`. `osdIDGenerator` provides deterministic OSD IDs per named status resource. `newDummyStorageClassDeviceSet()` creates simple PVC-backed device sets. `waitForNumConfigMaps()`, `setStatusConfigMapToCompleted()`, `setStatusConfigMapToFailed()`, and `updateStatusConfigmap()` simulate prepare Job result updates.

## Control Flow Covered
The test starts with a spec that creates six node OSDs, six portable PVC OSDs, and three non-portable PVC OSDs. It then reconciles with no spec changes, increases node and PVC OSD counts, cancels mid-reconcile after some status ConfigMaps complete, resumes, injects failed status ConfigMaps, recovers, injects Deployment update failures, recovers, injects Deployment creation failures, recovers, adds a malformed device set, fixes it, and finally verifies dangling status ConfigMaps are removed.

## State and Persistence Behavior
State is represented by fake Kubernetes ConfigMaps, PVCs, Jobs, Deployments, watches, and CephCluster status updates. Deployment reactors mark Deployments ready immediately and record create/update counts. Status ConfigMaps hold serialized `OrchestrationStatus` JSON and are the synchronization point between prepare Jobs and daemon creation. The fake Ceph executor derives some command outputs from current fake Deployment state.

## Dependencies and Integration Points
The test crosses `create.go`, `deviceSet.go`, `osd.go`, update logic in neighboring files, status ConfigMap helpers, Deployment generation, and Ceph command wrappers. It also relies on Kubernetes fake reactors to simulate apiserver behavior that ordinary fake clients do not provide.

## Risks and Edge Cases
The test is intentionally timing-sensitive, with goroutines, watch events, and a timeout wrapper. It reduces ticker durations to keep runtime small. Because fake Deployments are marked ready immediately, it does not validate real rollout timing. The TODO near the top notes strategic merge patch noise in unit tests around missing merge keys.

## Test Signals
This is the strongest broad regression signal for the OSD reconcile lifecycle. It proves idempotent repeated reconciles, partial failure recovery, cancellation recovery, update/create interplay, and cleanup of stale orchestration artifacts.
