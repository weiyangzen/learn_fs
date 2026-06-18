# sources/control-plane/ceph-csi/examples/nfs/pvc.yaml

Purpose: baseline dynamically provisioned NFS CSI PVC.

Important fields and flow: PVC `cephcsi-nfs-pvc` requests `1Gi`, `ReadWriteMany`, and StorageClass `csi-nfs-sc`.

State, dependencies, and integration: creates a Ceph-backed NFS export via the NFS CSI provisioner.

Risks and test signals: requires valid NFS StorageClass, CephFS backing config, and NFS server. Bound PVC and pod mount validate provisioning.
