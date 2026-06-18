<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node-windows-hostprocess.yaml

Purpose: Windows HostProcess node-plugin DaemonSet for SMB CSI v1.18.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `init`, `node-driver-registrar`, `smb`. Images: `init` `registry.k8s.io/sig-storage/smbplugin:v1.18.0-windows-hp`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.13.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.18.0-windows-hp`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. This HostProcess variant omits the liveness sidecar and uses an init container to create `C:\var\lib\kubelet\plugins\smb.csi.k8s.io` before starting host-process registrar and SMB containers.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, HostProcess support, host networking, and direct host filesystem access rather than CSI Proxy pipe mounts. Host paths/pipes include: none declared, because this HostProcess manifest relies on host namespace access and explicit plugin directory initialization.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node-windows-hostprocess.yaml -->
