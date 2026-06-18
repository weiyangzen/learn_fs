# sources/control-plane/ceph-csi/examples/nfs/rook-nfs.yaml

Purpose: example Rook `CephNFS` custom resource for deploying a Ceph-managed NFS server.

Important fields and flow: creates `CephNFS` `my-nfs`, configures RADOS pool `.nfs`, namespace `my-nfs`, and one active NFS server.

State, dependencies, and integration: consumed by Rook to create NFS-Ganesha resources used by the NFS CSI StorageClass `nfsCluster` and `server` parameters.

Risks and test signals: requires Rook Ceph CRDs/operator and version-specific RADOS behavior. A ready NFS server and export creation validate it.
