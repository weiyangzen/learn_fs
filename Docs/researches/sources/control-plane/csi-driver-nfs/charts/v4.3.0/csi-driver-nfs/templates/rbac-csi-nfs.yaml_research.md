# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates v4.3.0 service accounts and external-provisioner RBAC, with snapshot permissions added only when the external snapshotter is enabled.

## Important APIs, Types, and Functions
It emits derived service account names `csi-{{ .Values.rbac.name }}-controller-sa` and `csi-{{ .Values.rbac.name }}-node-sa`. The provisioner `ClusterRole` covers PV/PVC/storageclass/events/CSINode/node/lease/secret access and conditionally adds snapshot class/snapshot/content/status reads and updates.

## Control Flow, State, and Persistence
Service account creation and RBAC creation are independently gated. Snapshot RBAC is gated by `externalSnapshotter.enabled`, unlike v4.13.x where snapshot rules are always present in the provisioner role. Persistent authorization state is cluster-scoped.

## Dependencies and Integration Points
The default derived service account names match the controller and node templates only under default `rbac.name: nfs`. The optional snapshot permissions support the controller's `csi-snapshotter` sidecar.

## Risks and Test Signals
Risks include service account name drift on custom values, no resizer RBAC, conditional snapshot permissions hiding forbidden errors only when the sidecar is enabled, and broad cluster permissions. Signals include rendered name checks, `kubectl auth can-i`, PVC lifecycle, and snapshot tests with the feature toggled.
