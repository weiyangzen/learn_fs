# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csidriver.yaml

Purpose: generated `CSIDriver` object for CephFS.

Important APIs/types/functions: name `cephfs.csi.ceph.com`; `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy: File`, `seLinuxMount: true`.

Control flow: Kubernetes uses it to advertise driver capabilities and pod-info requirements to kubelet/CSI.

State and persistence behavior: cluster-scoped API object only.

Dependencies and integration points: must match CephFS StorageClasses and driver flags.

Risks: direct edits are overwritten by yamlgen. Driver-name mismatch prevents provisioning/mounts from resolving.

Test signals: Kubernetes CSI discovery and CephFS e2e mounts.
