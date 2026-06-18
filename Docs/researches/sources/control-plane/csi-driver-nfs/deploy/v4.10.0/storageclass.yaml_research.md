# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/storageclass.yaml

Purpose: defines the default example dynamic provisioning class for the NFS CSI driver.

Important APIs/types/functions: the object is a `storage.k8s.io/v1` `StorageClass` named `nfs-csi`, with provisioner `nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`.

Control flow: PVCs that name `storageClassName: nfs-csi` trigger the external provisioner in the controller deployment. The driver receives the server/share attributes, creates or selects an NFS subdirectory, and returns a CSI volume handle used by PVs and node publish calls.

State and persistence: the StorageClass is persistent cluster configuration. Provisioned PVs, PVCs, and NFS directories survive independently according to reclaim policy and driver delete behavior.

Dependencies and integration points: depends on the controller deployment, RBAC, `CSIDriver`, node DaemonSet, and a resolvable NFS service matching the `server` value. The optional commented secret parameters integrate with controller secret RBAC for delete-time mount options.

Risks: this sample hard-codes the demo NFS service DNS name and share root. `Immediate` binding can provision before a consumer pod's node constraints are known. `Delete` reclaim can remove backend subdirectories when PVCs are deleted, so it is risky for manual testing against valuable data.

Test signals: create `pvc-nfs-csi-dynamic.yaml`, wait for a bound PV, mount it with `nginx-pod-nfs.yaml`, test expansion, and confirm NFSv4.1 mount options on the node.
