# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/create.go

## Purpose
This file owns the creation side of OSD reconciliation. It starts OSD prepare Jobs for node-backed and PVC-backed OSDs, tracks which status ConfigMaps are expected from those Jobs, and creates OSD Deployments from completed orchestration status. It is the bridge between storage specification parsing, provisioning Jobs, and daemon Deployment creation.

## Important APIs, Types, and Functions
`createConfig` stores the current reconcile's provisioning config, expected status ConfigMaps, completed status ConfigMaps, and existing OSD deployments. `newCreateConfig()`, `progress()`, and `doneCreating()` are lightweight lifecycle helpers. `createNewOSDsFromStatus()` is the key callback for status ConfigMap results. It ignores stale or already processed ConfigMaps, skips OSD IDs whose Deployments already exist, initializes first-deploy cephx status with `keyring.UpdatedCephxStatus()`, and dispatches to node or PVC daemon creation.

`startProvisioningOverPVCs()` prepares `StorageClassDeviceSet` PVCs, skips PVCs with existing OSD Deployments, handles migration re-preparation, creates dmcrypt keys and KMS secrets for encrypted PVC OSDs, writes starting orchestration status, and launches prepare Jobs. `startProvisioningOverNodes()` resolves valid nodes, enforces `dataDirHostPath`, derives node storage settings and device class, writes starting status, and launches prepare Jobs. `runPrepareJob()` delegates Job construction to `makeJob()` and runs it with `k8sutil.RunReplaceableJob()`. `createDaemonOnPVC()` and `createDaemonOnNode()` build and create OSD Deployments, update CephCluster progressing status, and perform a second Deployment update when multicluster service export requires external IP arguments.

## Control Flow
The file is used from `Cluster.Start()`: PVC provisioning runs first, node provisioning runs second, both return sets of status ConfigMap names, and `createConfig` processes watcher results through `updateAndCreateOSDs()`. Prepare Job failures are accumulated as `provisionErrors` without necessarily halting all provisioning. Context cancellation during loops returns immediately to stop reconcile.

## State and Persistence
State is persisted in Kubernetes objects: PVC-backed encryption material is stored through the configured KMS using the PVC claim name as key; orchestration progress is stored in status ConfigMaps; prepare Jobs are Kubernetes Jobs; successful OSDs become Deployments. `createConfig.finishedStatusConfigMaps` is in-memory per reconcile and prevents duplicate processing of a status object.

## Dependencies and Integration Points
The code depends on Ceph CRD storage specs, `deviceSet.go` for PVC source synthesis, `osd.go` for Deployment builders, KMS support from `pkg/daemon/ceph/osd/kms`, Kubernetes helper utilities, and Cephx keyring status helpers. It integrates with condition updates through the overridable `updateConditionFunc`, which is stubbed in tests.

## Risks and Edge Cases
Important risks are stale status ConfigMaps from old reconciles, accidental encryption key overwrite, partial provisioning when one node or PVC fails, device-class conflicts on nodes, and multicluster service requiring Deployment mutation after initial create. PVC migration uses a substring match against `migrateOSD.BlockPath`, which is pragmatic but depends on stable block-path naming. Node provisioning mutates `c.spec.Storage.Nodes` when `UseAllNodes` is set, so callers should treat the cluster instance as reconcile-scoped.

## Test Signals
`create_test.go` covers stale and duplicate status handling, skipping existing OSD IDs, error aggregation, PVC provisioning with missing templates, node provisioning with empty `dataDirHostPath`, `UseAllNodes`, individual node selection, prepare Job failure, and device-class resolution from node labels. `integration_test.go` exercises this file through repeated full `Cluster.Start()` reconciles, cancellation, failures, and cleanup.
