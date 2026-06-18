# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin.yaml

Purpose: static NVMe-oF nodeplugin DaemonSet.

Important APIs/types/functions: privileged `csi-nvmeofplugin --nodeserver=true`, node id composed as `$(NODE_ID)::nqn.2025-08.io.ceph:$(NODE_ID)`, CSI-Addons endpoint, registrar, host network/PID, OpenShift storage-node toleration, hostPaths for `/dev`, `/sys`, `/run/mount`, modules, kubelet plugins/pods, SELinux, projected KMS token, and host log directory.

Control flow: runs on eligible nodes, registers `nvmeof.csi.ceph.com`, performs NVMe-oF node operations with host devices/modules, and writes plugin logs to a hostPath.

State and persistence behavior: host plugin socket, kubelet mounts, and `/var/lib/cephcsi/csi-nvmeofplugin` logs persist on node; keys are memory-backed.

Dependencies and integration points: kubelet, NVMe tooling/kernel modules, CSI-Addons, OpenShift SCC/RBAC, logrotate config volume reference, and cluster config.

Risks: references `nvmeof.csi.ceph.com-logrotate-config` volume but no mount appears in the container section in this file, which may indicate incomplete logrotate integration. Hardcoded NQN format and storage-node toleration are environment-specific.

Test signals: DaemonSet rollout, registrar registration, NVMe-oF attach/mount e2e, and log path validation.
