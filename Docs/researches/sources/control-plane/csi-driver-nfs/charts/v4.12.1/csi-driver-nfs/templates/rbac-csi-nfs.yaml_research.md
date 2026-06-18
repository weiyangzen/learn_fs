# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This 4.12.1 template creates service accounts and cluster RBAC for NFS CSI controller/node operation.

## APIs, Control Flow, and State
Conditionals are driven by `serviceAccount.create` and `rbac.create`. The service accounts live in the release namespace. The external provisioner role covers PV/PVC/StorageClass/snapshot reads and updates, Node/CSINode reads, event writes, lease writes, and secret reads. The external resizer role covers PV and PVC status updates, event writes, and lease writes. Bindings attach both roles to the controller service account.

## Dependencies and Integration Points
The controller Deployment uses the bound service account for sidecars. The node service account is created here but does not receive additional cluster role bindings in this template. Snapshot permissions support controller-side snapshotter integration.

## Risks and Test Signals
Missing RBAC appears as sidecar reconciliation errors; excessive RBAC increases cluster-level privilege. Test `kubectl auth can-i`, PVC lifecycle, resize, snapshot operations, and lease creation. This template is unchanged from 4.12.0.
