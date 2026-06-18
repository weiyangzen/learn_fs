# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template provides RBAC for the optional 4.13.0 external snapshot controller.

## APIs, Control Flow, and State
It conditionally emits the snapshot-controller service account, cluster role, cluster role binding, namespaced leader-election role, and role binding. Verbs cover PV/PVC reads and PVC updates, events, snapshot class/content/snapshot lifecycle and status updates, leases, and optional Node reads for distributed snapshotting.

## Dependencies and Integration Points
It is consumed by `csi-snapshot-controller.yaml` and relies on CRDs from `crd-csi-snapshot.yaml`. It is unchanged from 4.12.x while default snapshot-controller image advances to `v8.4.0`.

## Risks and Test Signals
RBAC may need validation against the newer snapshot-controller image. Test authorization, lease creation, snapshot status updates, deletion policy handling, and optional distributed snapshotting rendering.
