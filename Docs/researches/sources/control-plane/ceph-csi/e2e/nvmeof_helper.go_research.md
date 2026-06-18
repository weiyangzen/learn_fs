# sources/control-plane/ceph-csi/e2e/nvmeof_helper.go

## Purpose
`nvmeof_helper.go` contains e2e helpers for stressing NVMe-oF pod attach/detach behavior, especially the NodeServer GroupLock path. It deliberately separates ControllerServer PVC provisioning/deletion from NodeServer pod create/delete operations so tests can exercise concurrent `NodeStage` and `NodeUnstage` activity without mixing in provisioning concurrency.

## Important APIs, Types, And Functions
`concurrentPodsResult` records a generated pod-name prefix, operation count, per-index errors, and failure count. Its `String`, `HasErrors`, and `LogErrors` methods provide compact result inspection and framework logging.

`createConcurrentPods(totalCount, pvcBaseName, pvcStartIndex, appPath, f)` loads a pod template with `loadApp`, sets the namespace, deep-copies the pod per goroutine, assigns a unique pod name, points the first volume at an existing PVC, and calls `createApp`.

`deleteConcurrentPods(result, f)` mirrors creation by deleting generated pod names in parallel with `deletePod`.

`mixedCreateDeletePodsOnly(totalCount, batchSize, pvcPath, appPath, storageClassName, f)` is the higher-level scenario. It creates all PVCs sequentially, creates the first pod batch, then for each later batch concurrently creates the next batch while deleting the previous one, validates running state, deletes the final batch, and finally deletes all PVCs.

## Control Flow
The top-level helper validates `batchSize > 0` and exact divisibility, then loads and configures the PVC template once. All PVCs are provisioned one by one with unique names and `createPVCAndvalidatePV`. A cleanup closure deletes any active pod batch and then attempts every PVC deletion to reduce leaked cluster state on early failures.

The initial pod batch is created with `createConcurrentPods` and each pod is checked with `waitForPodInRunningState`. Later iterations run two goroutines under a `sync.WaitGroup`: one creates the new batch against the next PVC offset, and one deletes the previous batch. Errors from both sides are collected, but the flow still validates the current batch's running pods before advancing `previousResult`. After the loop, the last pod batch is deleted and all PVCs are removed sequentially.

## State, Persistence, And Dependencies
The helper persists no process-local state beyond stack variables and per-call slices. Cluster state is the real state under test: PVCs, PVs, pods, volume attachments, and CSI side effects. Unique names come from `github.com/google/uuid`. Kubernetes integration is through `framework.Framework`, `f.ClientSet`, `loadPVC`, `loadApp`, `createPVCAndvalidatePV`, `deletePVCAndValidatePV`, `createApp`, `deletePod`, and `waitForPodInRunningState`.

## Integration Points
This file is intended for Ceph-CSI e2e specs that need deterministic NVMe-oF attach/detach pressure. It uses YAML templates owned elsewhere in the e2e suite and the common `deployTimeout`, `poll`, and framework logging conventions. The explicit "pods only" concurrency makes it a focused integration point for nodeplugin locking behavior rather than storage-class or controller provisioning behavior.

## Risks
`createConcurrentPods` assumes the loaded pod template has `Spec.Volumes[0].PersistentVolumeClaim` populated; malformed templates can panic rather than return an error. The concurrent create/delete loop writes `createResult` and `deleteResult` from goroutines and reads them after `Wait`, which is safe for visibility after synchronization but would be fragile if later logic read them before the wait. If current-batch creation has failures, the code still references `createResult.uniqueName` during running-state validation; a completely failed create result still has a name, but follow-on errors can obscure the original failure set. Cleanup ignores deletion errors by design, so leaked resources are possible when the API server or CSI cleanup path is unhealthy.

## Test Signals
Strong signals are validation of invalid `batchSize` and non-divisible totals, successful multi-batch create/delete interleaving, injected pod-create and pod-delete failures with logged per-index errors, cleanup after initial batch failure, and resource-leak checks after failures. Tests should also include templates with multiple volumes or missing volume claims if this helper is reused outside its current NVMe-oF fixtures.
