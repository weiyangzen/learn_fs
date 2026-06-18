# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/status.go

## Purpose
`status.go` manages OSD provisioning status ConfigMaps and coordinates the transition from prepare jobs to OSD deployment creation and update. Prepare jobs write JSON `OrchestrationStatus` payloads into per-node/PVC ConfigMaps; the operator lists and watches those ConfigMaps, creates OSD deployments from completed statuses, records failures, and cleans up processed status maps.

## Important APIs, Types, and Functions
Important pieces are `provisionConfig`, `Cluster.newProvisionConfig()`, `provisionErrors`, `UpdateNodeOrPVCStatus()`, `parseOrchestrationStatus()`, `Cluster.updateAndCreateOSDs()`, `Cluster.updateAndCreateOSDsLoop()`, `Cluster.createOSDsForStatusMap()`, `statusConfigMapName()`, `statusConfigMapLabels()`, `statusConfigMapSelector()`, `isAddOrModifyEvent()`, `eventObjectName()`, `deleteStatusConfigMap()`, and `deleteAllStatusConfigMaps()`.

## Control Flow, State, and Persistence
`UpdateNodeOrPVCStatus()` serializes `OrchestrationStatus` as JSON under the `status` key in a labeled ConfigMap named `rook-ceph-osd-<node-or-pvc>-status`. `updateAndCreateOSDs()` repeatedly calls the loop until no watcher restart is needed. Each loop lists existing status maps, processes any already-completed items, starts a watch from the list resourceVersion, and then multiplexes watch events, opportunistic update ticks, minute progress ticks, and context cancellation. Completed statuses call `createConfig.createNewOSDsFromStatus()` and delete the status map. Failed statuses mark the item done, add a provision error, and delete the status map.

## Dependencies and Integration Points
This file depends on Kubernetes ConfigMap list/watch APIs, `k8sutil.ConfigMapKVStore`, OSD creation/update configs from other OSD files, cluster context cancellation, and Rook logging. It is the handshake between prepare jobs produced by `provision_spec.go` and deployments produced by `spec.go`.

## Risks
The watch loop is sensitive to Kubernetes watch closure and resourceVersion behavior. It intentionally restarts if the watch channel closes, ignores delete/bookmark/error events, and aborts after 20 minutes without progress. Status update failures are logged but non-fatal, which prevents provisioning from stopping on ConfigMap write errors but can leave the operator waiting. `eventObjectName()` is defensive for non-metadata objects; incorrect event object types are logged and skipped rather than fatal. Progress is based on create/update counters, so bugs in those counters can affect timeout behavior.

## Test Signals
`status_test.go` verifies ConfigMap write/read/parse behavior. `osd_test.go` drives the real watch path by manually modifying fake watcher events and validates successful deployment creation, failed job handling, and cleanup of dangling status maps.
