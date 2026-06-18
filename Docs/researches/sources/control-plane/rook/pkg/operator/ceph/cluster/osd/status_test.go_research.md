# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/status_test.go

## Purpose
`status_test.go` validates the OSD orchestration status ConfigMap contract and provides shared helpers for asynchronous OSD orchestration tests. It ensures status writes create parseable ConfigMaps and supplies fake watcher utilities used by broader reconcile tests.

## Important APIs, Types, and Functions
The test directly covers `UpdateNodeOrPVCStatus()` and `parseOrchestrationStatus()`. Helper `mockNodeOrchestrationCompletion()` waits until a node status ConfigMap reaches `starting`, writes a `completed` status with one raw OSD, and sends a fake watcher modify event. Helper `waitForOrchestrationCompletion()` polls until the reconcile goroutine finishes while logging current status.

## Control Flow, State, and Persistence
`TestOrchestrationStatus` starts with an empty fake Kubernetes namespace, creates a `ConfigMapKVStore`, writes `OrchestrationStatus{Status: orchestrating, Message: "doing work"}`, retrieves the generated ConfigMap, and asserts a round-trip JSON parse. The helpers coordinate goroutines by polling ConfigMaps and fake watcher events, modeling the real prepare job to operator handoff without running a pod.

## Dependencies and Integration Points
The test uses fake Kubernetes clients, `k8sutil.NewConfigMapKVStore`, Rook `ClusterInfo`, and `watch.RaceFreeFakeWatcher`. The helper status payload contains fields consumed by OSD creation, including OSD ID, UUID, cluster, CV mode, block path, and completed status.

## Risks
The polling helpers can hang if the reconcile path never writes `starting` or if the fake watcher is not registered. They assume node-based storage exists; if storage nodes are empty, completion mocking returns immediately. The fake watcher requires both a manual ConfigMap data update and a `Modify()` event because fake client updates alone do not trigger watch events.

## Test Signals
Core signal is ConfigMap status round-trip correctness. Secondary signal comes from reuse in `osd_test.go`, where the helpers prove that status `completed` events are enough to unblock `Start()` and create OSD deployments.
