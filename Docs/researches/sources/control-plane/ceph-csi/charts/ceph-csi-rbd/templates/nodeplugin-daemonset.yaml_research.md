# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-daemonset.yaml

Purpose: renders the privileged RBD nodeplugin DaemonSet that serves node-stage/node-publish operations on every node.

Important APIs/types/functions: main `csi-rbdplugin` container runs `--type=rbd --nodeserver=true`, kubelet plugin/staging paths, CSI-Addons endpoint, topology/read-affinity/fencing flags, and slow-op logging. Sidecars include `driver-registrar` and optional `liveness-prometheus`.

Control flow: the pod runs on host network/PID, creates the CSI socket under the kubelet plugin directory, registers with kubelet through the registrar, maps/unmaps RBD devices, mounts volumes into kubelet pod paths, and exposes liveness metrics when enabled.

State and persistence behavior: hostPath state includes kubelet plugin sockets, pod mount propagation, `/dev`, `/run/mount`, `/sys`, `/lib/modules`, Ceph logs, and optional SELinux config. Keys are in memory-backed `emptyDir`; KMS tokens are projected.

Dependencies and integration points: requires privileged host access, Ceph config/KMS ConfigMaps, Kubernetes service account/RBAC, kubelet plugin registry, Ceph kernel modules or rbd-nbd, and CSI-Addons consumers.

Risks: high privilege and broad hostPath access are required but sensitive. Incorrect `kubeletDir`, registration path, or SELinux mounts can break registration/mounts. Read-affinity labels must match Ceph CRUSH locations.

Test signals: nodeplugin DaemonSet rollout, kubelet CSI registration, pod mount e2e tests, encryption tests, and metrics scraping.
