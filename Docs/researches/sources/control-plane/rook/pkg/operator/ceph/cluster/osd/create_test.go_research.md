# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create_test.go

## Purpose
This test file validates the OSD creation and prepare-job launch paths in `create.go`. It focuses on deterministic behavior around status ConfigMaps, node/PVC provisioning gates, prepare Job failures, and device-class selection.

## Important APIs, Types, and Helpers
`Test_createNewOSDsFromStatus` overrides `createDaemonOnNodeFunc` and `createDaemonOnPVCFunc` to record requested OSD IDs and inject failures. It constructs a `createConfig` with expected status ConfigMaps and an `existenceList` representing existing Deployments. `Test_startProvisioningOverPVCs` uses a complex fake clientset with generated-name support to verify PVC prepare orchestration and status ConfigMap creation. `Test_startProvisioningOverNodes` uses fake nodes and Kubernetes reactors to simulate successful and failed Job creation. `Test_startProvisioningOverNodes_deviceClassNodeLabel` creates nodes with `osd.rook.io/device-class` labels to validate conflict and fallback rules. `newDummyPVC()` creates block-mode PVC templates for storage class device set tests.

## Control Flow Covered
The tests drive `createNewOSDsFromStatus()` through node-backed and PVC-backed branches. They assert that only ConfigMaps created for the current reconcile are processed, already existing OSD IDs are skipped, failed daemon creation is recorded while later OSDs still get attempted, and completed status ConfigMaps are marked finished. PVC provisioning tests verify no-op behavior with empty specs or zero counts, successful status ConfigMap creation for two PVCs, idempotent repeat reconcile before daemon creation, and error reporting for missing volume claim templates. Node tests verify no-op storage specs, hard failure accumulation for missing `dataDirHostPath`, expansion of `UseAllNodes`, warning-compatible behavior when `UseAllNodes` and explicit nodes coexist, individual node selection, no-node behavior, and per-node Job creation failure isolation.

## State and Persistence Behavior
The test state is entirely fake Kubernetes API state: ConfigMaps represent orchestration status, Jobs represent prepare work, fake nodes drive valid-node selection, and fake PVCs are generated for storage class device sets. Global function variables are restored with defers, which is important because package-level overrides affect other tests.

## Dependencies and Integration Points
The tests depend on Rook test helpers (`test.New`, `test.NewComplexClientset`), fake Kubernetes reactors, `cephclient.ClusterInfo`, and Ceph version fixtures. They indirectly exercise `makeJob()`, status ConfigMap helpers, and node validation helpers even though those helpers live outside this file.

## Risks and Gaps
The tests are strong for control-flow branching but do not deeply inspect generated Job pod specs in the main provisioning cases; there is an inline TODO noting this. KMS/encryption setup in `startProvisioningOverPVCs()` is not covered here. Since tests mutate package-level function variables, missing restoration would cause cross-test contamination, but defers handle the current overrides.

## Test Signals
The file itself is the signal for create-path behavior. It provides regression coverage for idempotency, stale ConfigMap filtering, partial failures, and new node-label device-class behavior, which are high-risk areas in OSD reconciliation.
