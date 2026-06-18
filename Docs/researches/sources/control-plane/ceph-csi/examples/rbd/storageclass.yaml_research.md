## sources/control-plane/ceph-csi/examples/rbd/storageclass.yaml

Purpose: Comprehensive example `StorageClass` for dynamically provisioned RBD volumes.

Important API surface: `provisioner: rbd.csi.ceph.com`, required `clusterID` and `pool`, optional data pool, image features, mkfs options, mounter selection, map/unmap options, logging, encryption, topology constrained pools, striping parameters, `allowVolumeExpansion: true`, `reclaimPolicy: Delete`, mount option `discard`, and all relevant CSI secret references including provisioner, node stage, controller expand/publish/modify, and node publish.

Control flow and state: Kubernetes external-provisioner sends parameters to the RBD CSI controller to create images and PVs. Node-side calls use secret references and fstype/mount options to map and mount images. Expansion and VolumeAttributesClass modification are enabled by the secret references and `allowVolumeExpansion`.

Dependencies and integration: Requires `ceph-csi-config` with the cluster ID, `secret.yaml`, a real RBD pool, and deployed RBD controller/node plugin. Integrates with clone, snapshot, block, ephemeral, RWOP, encryption, topology, rbd-nbd, krbd QoS, and cgroup VAC examples.

Risks and test signals: Most values are placeholders or commented documentation; production use needs careful feature compatibility, especially RBD feature dependencies, mounter support, encryption KMS, topology JSON, and discard behavior. Test by provisioning filesystem and block PVCs, expansion, snapshot/restore, clone, and optional encryption/QoS flows.
