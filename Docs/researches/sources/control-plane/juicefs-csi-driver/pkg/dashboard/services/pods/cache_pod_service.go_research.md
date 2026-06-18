# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/cache_pod_service.go

## Purpose
`CachePodService` provides cached, enriched listing for app and system pods and maintains pod indexes for dashboard manager mode.

## Important APIs, Types, And Functions
It defines `CachePodService`, filter helpers for PV/mount pod/CSI node filters, `ListAppPods`, `ListSysPods`, `ListBatchPods`, `Reconcile`, and `SetupWithManager`.

## Control Flow
`ListAppPods` iterates app pod indexes in requested order, filters by name/namespace and app/PVC-using classification, enriches each pod with PVCs, PVs, mount pods, CSI node, and node, applies relation filters and sort fields, then paginates. `ListSysPods` does similar for system pods with node/CSI-node enrichment. `ListBatchPods` loads pods by batch config names. `Reconcile` fetches the pod, removes missing/deleting entries, classifies app vs system pods, tracks CSI node pod names by node, and indexes by creation time. Setup installs a field index on `spec.nodeName` and watches all pod events.

## State And Persistence
In-memory state includes `csiNodeIndex`, app and system `TimeOrderedIndexes`, and unused pair fields. Persistent pod state is read from Kubernetes and not mutated by this service.

## Dependencies And Integration Points
It builds on `podService` helpers, `dashboard/utils` pod classifiers and index type, controller-runtime manager/cache, and config global `CSIPod` initialization.

## Risks
`filterCSINodeOfPod` dereferences `pod.CsiNode.Name` when a filter is set and `CsiNode` is nil, risking panic after a failed CSI-node lookup. Delete handling for not-found uses an empty `pod` object to check `utils.IsCsiNode`, so CSI-node index cleanup may miss deleted pods. Enrichment calls can be expensive because each listed pod triggers additional Kubernetes reads.

## Test Signals
No direct tests are present. Tests should cover nil CSI node filtering, index updates/deletes, pagination after relation filters, and startup classification for app pods that only use JuiceFS PVCs.
