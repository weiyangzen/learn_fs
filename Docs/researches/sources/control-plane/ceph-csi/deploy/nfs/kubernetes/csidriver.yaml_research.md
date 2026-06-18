# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csidriver.yaml

Purpose: generated `CSIDriver` object for NFS.

Important APIs/types/functions: name `nfs.csi.ceph.com`; `attachRequired`, `podInfoOnMount`, `fsGroupPolicy: File`, `seLinuxMount: true`, and `volumeLifecycleModes: Persistent`.

Control flow: Kubernetes discovers NFS CSI capabilities and uses pod-info/fsgroup settings during mounts.

State and persistence behavior: cluster-scoped Kubernetes object only.

Dependencies and integration points: must match NFS driver flags and StorageClass provisioner.

Risks: direct edits are overwritten by yamlgen. Lifecycle modes limit the object to persistent volumes.

Test signals: NFS CSI discovery and mount tests.
