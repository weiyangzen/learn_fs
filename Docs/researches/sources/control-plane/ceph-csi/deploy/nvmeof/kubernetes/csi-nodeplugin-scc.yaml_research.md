# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-scc.yaml

Purpose: OpenShift `SecurityContextConstraints` for the NVMe-oF nodeplugin.

Important APIs/types/functions: allows privileged containers, `SYS_ADMIN`, hostDir volumes, host IPC/network/PID, hostPath/configMap/projected/emptyDir volumes, runAsAny, seLinux RunAsAny, and grants to `system:serviceaccount:default:ceph-nvmeof-nodeplugin`.

Control flow: OpenShift admission uses this SCC to permit the privileged DaemonSet that loads NVMe/kernel functionality and mounts volumes.

State and persistence behavior: cluster security policy object.

Dependencies and integration points: tied to the nodeplugin service account and OpenShift SCC admission.

Risks: high privilege policy with default namespace baked in. The comment says "ssc" but means SCC. Must be carefully scoped in multi-tenant clusters.

Test signals: OpenShift pod admission and NVMe-oF nodeplugin rollout.
