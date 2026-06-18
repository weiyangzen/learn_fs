# sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.7.0, csi-node-driver-registrar v2.5.1, and nfsplugin v4.1.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
