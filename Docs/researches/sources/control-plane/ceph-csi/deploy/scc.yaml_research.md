# sources/control-plane/ceph-csi/deploy/scc.yaml

Purpose: generated OpenShift `SecurityContextConstraints` for Ceph-CSI service accounts.

Important APIs/types/functions: SCC `ceph-csi` allows privileged containers, host network/PID/IPC, hostPath volumes, host ports, `SYS_ADMIN`, non-read-only root FS, runAsAny, seLinux RunAsAny, fsGroup/supplementalGroups RunAsAny, and configMap/projected/emptyDir/hostPath volumes. It grants RBD, CephFS, NFS, and NVMe-oF node/provisioner service accounts in `ceph-csi` namespace.

Control flow: OpenShift admission uses this SCC to permit CSI pods that require host access.

State and persistence behavior: cluster security policy state.

Dependencies and integration points: service account names/namespaces must match deployed manifests.

Risks: highly privileged policy. Namespace/service account mismatch prevents pod admission, while overbroad grants increase cluster risk.

Test signals: OpenShift deployment admission and CSI pod rollout.
