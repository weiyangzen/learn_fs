## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-snapshot-controller.yaml

Purpose: Grants the standalone snapshot controller permissions to reconcile CSI snapshot custom resources and to run leader election in `kube-system`. This RBAC file is paired with the v8.4.0 snapshot-controller deployment in the v4.13.x bundles.

Important APIs and types: Defines ServiceAccount `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding. The cluster role reads PVs, reads/updates PVCs, writes events, reads `VolumeSnapshotClass`, fully manages `VolumeSnapshotContent`, patches content status, gets/lists/watches/updates/patches/creates `VolumeSnapshot`, and updates/patches `VolumeSnapshot` status. The namespaced role grants full lease lifecycle verbs required for leader election.

Control flow: The deployment uses this ServiceAccount. Snapshot controller informers watch snapshot resources and storage dependencies, reconcile `VolumeSnapshot` to `VolumeSnapshotContent` binding, publish status, and coordinate active leadership with `coordination.k8s.io/leases` in `kube-system`.

State and persistence behavior: The file persists authorization policy only. The controller uses granted verbs to update Kubernetes snapshot objects and leader-election leases. It does not create local state, but privilege changes can immediately stop reconciliation or permit/deny snapshot object mutations.

Dependencies and integration points: Requires the CRDs in `crd-csi-snapshot.yaml`, the `snapshot-controller` deployment, and the CSI snapshotter sidecar/RBAC in the NFS controller. The extra `create` permission on `volumesnapshots` compared with v4.3.0 matches newer external-snapshotter controller expectations.

Risks: ClusterRole permissions are broad over all namespaces, which is necessary for cluster snapshot reconciliation but should be reviewed in multi-tenant clusters. Removing status or content verbs causes snapshots to hang. Leader-election Role is namespaced to `kube-system`; changing the deployment namespace or `--leader-election-namespace` requires matching RBAC edits.

Test signals: Use `kubectl auth can-i --as=system:serviceaccount:kube-system:snapshot-controller` for snapshot classes, contents, snapshots/status, PVCs, events, and leases. With two replicas, confirm a single lease holder and successful snapshot create/delete flows.
