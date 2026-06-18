<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.15.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.11.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.15.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-node.yaml -->
