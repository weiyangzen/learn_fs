## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-csi-nfs.yaml

Purpose: Creates ServiceAccounts and controller-side RBAC for the v4.13.x NFS CSI deployment. Compared with earlier versions, this file supports the provisioner, snapshotter, and resizer sidecars.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`; ClusterRole `nfs-external-provisioner-role` with PV get/list/watch/create/patch/delete, PVC get/list/watch/update, StorageClass watch, snapshot class/snapshot read, snapshot content update/patch/status, event writes, CSINode/Node reads, lease management, and secret get; binding `nfs-csi-provisioner-binding`; ClusterRole `nfs-external-resizer-role` with PV get/list/watch/update/patch, PVC read, PVC status update/patch, event writes, and lease management; and binding `nfs-csi-resizer-role`.

Control flow: The controller pod runs all sidecars under `csi-nfs-controller-sa`. The external provisioner watches PVCs and creates/patches/deletes PVs. The resizer watches expansion requests and updates PV/PVC status. The snapshotter watches snapshot APIs and updates snapshot content/status while invoking CSI calls on the NFS driver socket. Each sidecar uses leases for leader election.

State and persistence behavior: RBAC resources persist authorization policy and allow sidecars to mutate durable Kubernetes storage objects. The file does not create volumes, snapshots, or local state directly. Because all sidecars share the ServiceAccount, permission changes affect multiple controllers at once.

Dependencies and integration points: Paired with v4.13.x `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, `storageclass.yaml`, and `snapshotclass.yaml`. The secret read permission supports optional StorageClass provisioner secrets for DeleteVolume mount options.

Risks: Cluster-wide secret `get` is broad and should be reviewed for tenant boundaries. Missing `patch` on PVs or status verbs on PVCs would break modern provisioner/resizer behavior; this file includes them. Applying it without snapshot CRDs is allowed, but snapshot sidecars still cannot reconcile until the APIs exist. Shared ServiceAccount increases least-privilege surface.

Test signals: Use `kubectl auth can-i` as `system:serviceaccount:kube-system:csi-nfs-controller-sa` for PV patch/delete, PVC status patch, snapshot content status patch, events patch, leases create/update, and secrets get. Exercise provision, snapshot, resize, and delete flows and confirm events and status fields update.
