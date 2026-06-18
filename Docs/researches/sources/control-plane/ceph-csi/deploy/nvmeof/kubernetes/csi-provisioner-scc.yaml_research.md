# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-scc.yaml

Purpose: OpenShift SCC for the NVMe-oF provisioner.

Important APIs/types/functions: allows configMap/projected/emptyDir volumes, runAsAny, seLinux RunAsAny, not read-only root filesystem, drops all capabilities, and grants the `default:nvmeof-csi-provisioner` service account.

Control flow: OpenShift admission uses it for provisioner pods that do not require the nodeplugin's host privileges.

State and persistence behavior: cluster security policy state.

Dependencies and integration points: tied to `nvmeof-csi-provisioner` service account and OpenShift.

Risks: default namespace hardcoding. The SCC is permissive for user/SELinux but far less privileged than the nodeplugin SCC.

Test signals: OpenShift provisioner pod admission and rollout.
