<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-cluster-on-pvc-encrypted.yaml -->
# sources/control-plane/rook/tests/manifests/test-cluster-on-pvc-encrypted.yaml

Purpose: test `CephCluster` manifest for a PVC-backed encrypted OSD deployment. It is a compact cluster spec used by storage/encryption integration paths.

Important structure and control flow: the manifest defines `CephCluster/rook-ceph` in namespace `rook-ceph`, one monitor with a `manual` StorageClass PVC template, Ceph image `quay.io/ceph/ceph:v20.2.1` with unsupported versions allowed, dashboard disabled, host networking off, crash collector disabled, and one non-portable `storageClassDeviceSet` named `set1` with `encrypted: true` and a 10Gi block-mode data PVC.

State, persistence, and integration: creates Ceph cluster control-plane and OSD data state backed by Kubernetes PVCs and `/var/lib/rook`. Dependencies include Rook CRDs, a `manual` StorageClass, block PVs, and the specified Ceph image. Risks include single-replica/single-mon test topology, fixed image version, and destructive encrypted OSD state if reused outside disposable tests. Test signals are cluster readiness, encrypted PVC key Secret creation, and key rotation checks from related scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-cluster-on-pvc-encrypted.yaml -->
