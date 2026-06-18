# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csidriver.yaml

Purpose: `CSIDriver` object for NVMe-oF.

Important APIs/types/functions: name `nvmeof.csi.ceph.com`; sets `attachRequired`, `podInfoOnMount`, `seLinuxMount`, and `fsGroupPolicy: File`.

Control flow: Kubernetes uses it to discover the NVMe-oF CSI driver's attach and mount behavior.

State and persistence behavior: cluster-scoped Kubernetes object only.

Dependencies and integration points: must match NVMe-oF driver flags and StorageClass provisioner.

Risks: driver name mismatch breaks provisioning and kubelet registration.

Test signals: Kubernetes CSI discovery, attachment, and node publish tests.
