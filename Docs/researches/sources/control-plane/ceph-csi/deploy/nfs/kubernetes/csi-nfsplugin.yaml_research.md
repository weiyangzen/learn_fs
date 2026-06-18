# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin.yaml

Purpose: static NFS nodeplugin DaemonSet.

Important APIs/types/functions: privileged `csi-nfsplugin --nodeserver=true`, driver registrar, host network/PID, kubelet plugin and pod mount hostPaths with bidirectional propagation, `/dev`, `/sys`, `/run/mount`, SELinux, modules, Ceph config, Ceph-CSI config, and memory key dir.

Control flow: runs on each node, registers `nfs.csi.ceph.com` with kubelet, and performs node-stage/publish mounts through the CSI socket.

State and persistence behavior: host plugin sockets and pod mounts persist on node; key dir is ephemeral.

Dependencies and integration points: kubelet registration, NFS client tooling in image, config maps, nodeplugin RBAC, and host mount namespace.

Risks: privileged host access is broad. Hardcoded `/var/lib/kubelet` and default namespace assumptions may need customization.

Test signals: kubelet CSI registration and NFS volume mount e2e tests.
