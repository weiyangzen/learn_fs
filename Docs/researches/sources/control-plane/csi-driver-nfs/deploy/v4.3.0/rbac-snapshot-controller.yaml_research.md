## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-snapshot-controller.yaml

Purpose: Grants the standalone snapshot controller permissions to reconcile CSI snapshot custom resources and to run leader election in `kube-system`. This RBAC file is paired with `csi-snapshot-controller.yaml` for v4.3.0.

Important APIs and types: Defines ServiceAccount `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and RoleBinding of the same name. The cluster role can read PVs, read/update PVCs, write events, read `VolumeSnapshotClass`, create/get/list/watch/update/delete/patch `VolumeSnapshotContent`, patch content status, get/list/watch/update/patch `VolumeSnapshot`, and update/patch `VolumeSnapshot` status. The namespaced role grants lease get/watch/list/delete/update/create for leader election.

Control flow: The snapshot-controller pod runs under this ServiceAccount. Informers watch PVC/PV and snapshot resources, then controller reconciliation updates snapshot objects and content objects according to binding and protection state. Lease permissions support the two-replica deployment's leader election so only the active controller mutates snapshot state.

State and persistence behavior: The RBAC resources persist authorization policy in the Kubernetes API. They do not store snapshot state themselves. They permit the controller to mutate snapshot CR status/content and leader-election `Lease` objects, so changes affect future reconciliation and high availability behavior.

Dependencies and integration points: Requires snapshot CRDs and the `snapshot-controller` Deployment. It also complements `rbac-csi-nfs.yaml`, which grants the CSI snapshotter sidecar driver-facing snapshot content permissions. Both layers are needed for full snapshot lifecycle.

Risks: The v4.3.0 role lacks `create` on `volumesnapshots`, unlike later v4.13.x manifests, so controller features that need creating snapshot objects would be blocked. Cluster-wide content permissions are broad but expected for this controller. Removing lease permissions can result in active/passive confusion or no leader. Namespace mismatches between the ServiceAccount, RoleBinding, and deployment break startup.

Test signals: Run `kubectl auth can-i` as `system:serviceaccount:kube-system:snapshot-controller` for each listed verb/resource, especially leases and snapshot status. Deploy two replicas and confirm one leader. Create, update, and delete snapshots while watching controller events and content/status writes.
