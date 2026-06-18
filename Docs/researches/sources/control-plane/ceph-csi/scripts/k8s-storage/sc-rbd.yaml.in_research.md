<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-rbd.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/sc-rbd.yaml.in

Purpose: RBD StorageClass template for external storage e2e tests.

Content: provisioner `rbd.csi.ceph.com`, cluster ID placeholder, pool `replicapool`, imageFeatures `layering`, Rook provisioner/expand/node-stage secret references, fstype ext4, `Delete` reclaim policy, expansion enabled, and `discard` mount option.

State and dependencies: materialized by `create-storageclasses.sh`; depends on Rook pool and secrets.

Integration points: referenced by `driver-rbd.yaml`.

Risks: hardcoded pool and secret names tie it to Rook sample deployment. `discard` mount option can affect performance/behavior and should match test expectations.

Test signals: validated by e2e provisioning/expansion/snapshot tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-rbd.yaml.in -->
