# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin.yaml

Purpose: static CephFS nodeplugin DaemonSet and metrics Service.

Important APIs/types/functions: privileged `csi-cephfsplugin --nodeserver=true`, driver registrar, liveness sidecar on 8681, host network/PID, kubelet plugin/pod hostPaths with bidirectional mount propagation, SELinux, modules, `/dev`, `/run/mount`, config/KMS mounts, and CephFS mountinfo hostPath.

Control flow: runs on every node, registers `cephfs.csi.ceph.com` with kubelet, mounts CephFS volumes using kernel or fuse mounters, and exposes liveness metrics.

State and persistence behavior: host plugin sockets, mount points, and mountinfo persist on nodes; keys are memory-backed.

Dependencies and integration points: kubelet plugin registry, Ceph config, cluster config, service account/RBAC, CephFS client tools, SELinux support, and metrics Service.

Risks: privileged host access and mount propagation are sensitive. Hardcoded `/var/lib/kubelet` and default namespace assumptions may not fit all clusters.

Test signals: DaemonSet readiness, kubelet registration, CephFS pod mount/unmount e2e, and metrics endpoints.
