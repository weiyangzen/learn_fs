# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin.yaml

Purpose: static RBD nodeplugin DaemonSet and metrics Service.

Important APIs/types/functions: privileged `csi-rbdplugin --nodeserver=true`, kubelet plugin/staging paths, CSI-Addons endpoint, registrar, liveness sidecar on 8680, host network/PID, `/dev`, `/sys`, `/run/mount`, SELinux, modules, kubelet plugin/pod hostPaths, Ceph log hostPath, KMS config, and projected OIDC token.

Control flow: registers `rbd.csi.ceph.com` with kubelet, maps/unmaps RBD devices, stages/publishes volumes with mount propagation, and exposes metrics.

State and persistence behavior: host plugin socket, mapped devices, mountpoints, and Ceph logs persist on node; keys are memory-backed.

Dependencies and integration points: kubelet, Ceph kernel/rbd-nbd tooling, KMS, config maps, node RBAC, and CSI-Addons.

Risks: privileged host access is required and high risk. Hardcoded kubelet path/default namespace may not fit all installs. Read-affinity/topology options are commented and require careful label alignment.

Test signals: RBD node mount/unmount, encryption, CSI registration, read affinity, and metrics tests.
