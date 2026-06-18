# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/labels.go

## Purpose
This file defines the Kubernetes labels used to identify OSD PVCs and OSD Deployments, and provides helpers to construct PVC labels, OSD daemon labels, and topology-location labels derived from CRUSH location strings.

## Important APIs, Types, and Functions
Constants include `CephDeviceSetLabelKey`, `CephSetIndexLabelKey`, `CephDeviceSetPVCIDLabelKey`, `OSDOverPVCLabelKey`, `TopologyLocationLabel`, `CephImageLabelKey`, and `RookImageLabelKey`. These keys are used by device-set PVC reconciliation, PVC-backed OSD Deployment filtering, key-rotation filtering, and status/reporting.

`makeStorageClassDeviceSetPVCLabel()` returns the base label set for PVCs created from storage class device sets: device set name, set index, device set PVC ID, Ceph image-at-creation, and Rook image-at-creation. `Cluster.getOSDLabels()` starts with standard Ceph daemon app labels, adds OSD ID, failure domain, portability, device class, store type, optional device type, and topology-location labels. `getOSDTopologyLocationLabels()` parses a space-separated CRUSH location string like `root=default host=node zone=zone-a` into labels named with `topology-location-<key>`.

## Control Flow
The helpers are deterministic mappers. `getOSDLabels()` overlays topology labels after base daemon labels. `getOSDTopologyLocationLabels()` ignores malformed tokens that do not split into exactly two `key=value` parts.

## State and Persistence
Labels generated here persist on PVCs and Deployments. They are used later as selectors for existing PVC detection, OSD Deployment lookup, key rotation CronJob owner targeting, health deletion, migration detection, storage status, and topology visibility. Because labels persist across upgrades, key names and values are compatibility-sensitive.

## Dependencies and Integration Points
The file depends on Rook controller label helpers and Ceph config constants. It is used by `deviceSet.go`, `osd.go`, `key_rotation.go`, migration logic, and tests. It also indirectly feeds Kubernetes selectors in health and key rotation paths.

## Risks and Edge Cases
Changing label keys can orphan existing resources from reconciliation. Label values sourced from CRUSH location can include topology dimensions only if the location string is well-formed. Device class and store labels may be empty but are still added by `getOSDLabels()`, which downstream code should tolerate. PVC image labels are sanitized in `deviceSet.go`, not here.

## Test Signals
`labels_test.go` validates topology label extraction for root, host, region, and zone entries. `deviceset_test.go` and other tests indirectly verify PVC label keys and image label presence.
