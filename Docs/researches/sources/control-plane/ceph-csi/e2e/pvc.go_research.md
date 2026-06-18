# sources/control-plane/ceph-csi/e2e/pvc.go

## Purpose
`pvc.go` provides PersistentVolumeClaim and PersistentVolume lifecycle helpers for Ceph-CSI e2e tests. It loads PVC templates, creates and deletes PVC/PV pairs, waits for binding or deletion, fetches bound resources, validates topology node affinity, and checks kubelet volume stats metrics for filesystem and block volumes.

## Important APIs, Types, And Functions
Template and create helpers are `loadPVC`, `createPVCAndvalidatePV`, `createPVCAndPV`, and `createPVC`. Lookup helpers are `getPersistentVolumeClaim`, `getPersistentVolume`, `getPVCAndPV`, and `getBoundPV`. Deletion helpers are `deletePVCAndPV`, `deletePVCAndValidatePV`, and `waitForPVToBeDeleted`.

Validation helpers are `checkPVSelectorValuesForPVC`, `getMetricsForPVC`, `parseVolumeStatsMetrics`, and `validateVolumeStatsMetrics`. They cover topology labels and kubelet `kubelet_volume_stats_*` metrics.

## Control Flow
`createPVCAndvalidatePV` creates a PVC, returns immediately if timeout is zero, then polls until the PVC has a `Spec.VolumeName`, fetches the PV, and delegates final binding checks to Kubernetes e2e `WaitOnPVandPVC`. While waiting for a volume name, it logs PVC events to make provisioning failures visible in test output.

`deletePVCAndPV` deletes both objects explicitly, then polls for PVC deletion and PV deletion. `deletePVCAndValidatePV` fetches the live PVC and backing PV before deleting only the claim, then polls until both the PVC and dynamically provisioned PV disappear. `getPersistentVolumeClaim` and `getPersistentVolume` wrap API gets in retry polling.

Topology validation fetches the bound PV and inspects the first required node-selector term, requiring exactly the expected region and zone keys/values and rejecting duplicate or unexpected keys. Metrics validation discovers a kubelet IP, curls its read-only metrics endpoint from the toolbox pod, extracts metrics for the PVC, and validates required capacity/used/available/inode relationships depending on volume mode.

## State, Persistence, And Dependencies
State is stored in Kubernetes resources and kubelet metrics, not in this helper. The helpers depend on Kubernetes core API clients, Kubernetes e2e PV waiting utilities, Ceph-CSI e2e polling/timeouts, toolbox pod command execution from `pod.go`, topology constants (`nodeCSIRegionLabel`, `nodeCSIZoneLabel`, `regionValue`, `zoneValue`), `getKubeletIP`, and local retryable API error classification.

## Integration Points
These helpers are used throughout Ceph-CSI e2e specs and by `nvmeof_helper.go` and `pod.go`. They provide the common contract that a created PVC is actually bound to a PV before a pod uses it, and that deletion waits for CSI/Kubernetes cleanup before the next test step. Metrics helpers integrate Kubernetes PVC state with node-level kubelet metrics exposed through the rook toolbox pod.

## Risks
`deletePVCAndValidatePV` logs `oldPV.Status` when a retryable error occurs after `oldPV` may be nil, which can panic on some API error paths. `waitForPVToBeDeleted` logs `pv.Status.String()` before checking `err`, so a failed get can also panic. `checkPVSelectorValuesForPVC` assumes `NodeAffinity`, `Required`, at least one selector term, and non-empty expression values; missing affinity structure can panic instead of returning an error. `createPVCAndPV` creates the PVC before the PV, which is fine for static tests but can briefly expose an unbound claim if PV creation fails. `getMetricsForPVC` relies on kubelet read-only port `10255`, so it will fail in clusters where that endpoint is disabled. `parseVolumeStatsMetrics` is intentionally simple and may not handle unusual Prometheus line formats beyond the expected kubelet metric lines.

## Test Signals
Tests should cover successful dynamic binding, provisioning events on delayed binding, timeout-zero create behavior, explicit PVC/PV create/delete, deletion with transient API errors, missing PVs, topology affinity success and malformed affinity structures, metric parsing with labels in different orders, filesystem versus block validation requirements, invalid metric values, and kubelet endpoint unavailability. Regression tests for nil-pointer paths in deletion polling would be particularly valuable.
