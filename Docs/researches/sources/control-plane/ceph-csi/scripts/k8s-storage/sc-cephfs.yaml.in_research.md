<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-cephfs.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/sc-cephfs.yaml.in

Purpose: CephFS StorageClass template for external storage e2e tests.

Content: provisioner `cephfs.csi.ceph.com`, cluster ID placeholder, fsName `myfs`, Rook CephFS provisioner/node secret references, `Delete` reclaim policy, and volume expansion enabled.

State and dependencies: materialized by `create-storageclasses.sh` after replacing `@@CLUSTER_ID@@`; depends on Rook-created secrets and CephFS `myfs`.

Integration points: referenced by `driver-cephfs.yaml`.

Risks: hardcoded secret names/namespaces and fsName assume Rook test deployment defaults. No mount options or topology parameters.

Test signals: validated by e2e provisioning and expansion tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-cephfs.yaml.in -->
