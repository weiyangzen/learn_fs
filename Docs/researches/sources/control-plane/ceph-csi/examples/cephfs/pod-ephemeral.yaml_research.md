# sources/control-plane/ceph-csi/examples/cephfs/pod-ephemeral.yaml

Purpose: example pod using Kubernetes generic ephemeral volumes backed by the CephFS StorageClass.

Important fields and flow: Pod `csi-cephfs-demo-ephemeral-pod` defines an inline `ephemeral.volumeClaimTemplate` requesting `1Gi` from `csi-cephfs-sc` and mounts it at `/myspace`.

State, dependencies, and integration: the kubelet/controller creates a temporary PVC for the pod lifetime. It depends on generic ephemeral volume support and the CephFS StorageClass.

Risks and test signals: storage is deleted with the pod, so this is not for persistence. Success validates dynamic provisioning through ephemeral PVC templates.
