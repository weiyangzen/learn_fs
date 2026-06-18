# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/storageclass.yaml

Purpose: optionally renders the RBD `StorageClass`.

Important APIs/types/functions: gated by `.Values.storageClass.create`; emits provisioner driver name, `clusterID`, image features, optional pool/dataPool, mounter, mkfs options, encryption, KMS ID, topology-constrained pools, map/unmap options, striping/object size, CSI secret references, fstype, reclaim policy, expansion, and mount options.

Control flow: Kubernetes dynamic provisioning uses this class; external-provisioner passes parameters to the RBD CSI controller and nodeplugin later stages with matching secret refs.

State and persistence behavior: StorageClass is cluster state; provisioned PVCs become PVs and Ceph RBD images in the configured pool.

Dependencies and integration points: requires `ceph-csi-config` cluster ID, Ceph pool, Ceph auth Secret, RBD image feature compatibility, and sidecar/controller deployment.

Risks: invalid image features or mounter options fail on specific nodes. Secret namespace defaults to release namespace, which may not match workloads. Topology pools require exact label/domain config.

Test signals: RBD PVC provisioning, mount, expansion, topology, encryption, and reclaim tests.
