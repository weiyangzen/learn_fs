<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/nvmeof-pool.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/nvmeof-pool.yaml

Purpose: creates the Ceph block pool backing NVMe-oF CSI volumes.
Important APIs/types/functions: `CephBlockPool` `nvmeof`, namespace `rook-ceph`, `failureDomain: host`, and replicated `size: 3`.
Control flow: Rook operator reconciles the pool CR into a Ceph RADOS pool; the NVMe-oF StorageClass references this pool for image allocation. State is persisted in the CephBlockPool CR and Ceph pool metadata/data. Dependencies are a healthy CephCluster with at least enough OSD failure domains for replica size 3. Risks: insufficient hosts/OSDs block or degrade pool creation, and pool name must match `storageclass.yaml`. Test signals: CephBlockPool Ready, Ceph reports pool `nvmeof`, and PVC provisioning allocates images there.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/nvmeof-pool.yaml -->
