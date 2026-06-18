# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose

This v4.6.0 template creates service accounts and cluster RBAC for the NFS CSI driver controller path.

## APIs, control flow, and state

Service accounts render when `.Values.serviceAccount.create` is true, using configurable controller and node names. Cluster RBAC renders when `.Values.rbac.create` is true. The cluster role grants PV create/delete/list/watch, PVC get/list/watch/update, StorageClass reads, snapshot class/snapshot/content reads and content status updates, events writes, CSINode and Node reads, lease CRUD/update/patch for leader election, and Secret get. The binding attaches that role to the controller service account.

The file is functionally the same as v4.5.0 for the requested scope: snapshot permissions are always included rather than gated by external snapshot-controller enablement.

## Dependencies and integration points

The controller deployment depends on this role for the external provisioner and snapshotter sidecars. The role also supports leader election and event recording. Snapshot permissions integrate with CRDs that may be installed by this chart or by the cluster platform.

## Risks and test signals

The RBAC is broad and cluster-scoped; the Secret read and snapshot mutation/status permissions should be reviewed for least privilege. Test `kubectl auth can-i` for each sidecar behavior, disabled RBAC scenarios, custom service account names, provisioning, snapshot workflows, and leader-election lease operations.
