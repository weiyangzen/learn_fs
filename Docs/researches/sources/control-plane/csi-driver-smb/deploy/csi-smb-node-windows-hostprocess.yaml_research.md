<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows-hostprocess.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows-hostprocess.yaml

- Purpose: current Windows HostProcess node DaemonSet for SMB CSI. It runs the plugin directly on Windows hosts without CSI proxy pipe mounts, using HostProcess privileges as `NT AUTHORITY\SYSTEM`.
- Important APIs/types/functions: emits `apps/v1` `DaemonSet`; images include gcr.io/k8s-staging-sig-storage/smbplugin:canary-windows-hp, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.16.0. It has an init container creating `C:\var\lib\kubelet\plugins\smb.csi.k8s.io`, node-driver-registrar with `--plugin-registration-path`, and `smbplugin.exe` with host-process and SMB mapping cleanup flags.
- Control flow: the init container prepares the plugin directory, registrar registers the kubelet socket path, then `smbplugin.exe` serves node CSI RPCs from the host plugin directory using the Windows node name from `spec.nodeName`.
- State and persistence behavior: plugin socket and registration files live under the Windows kubelet tree. Volume data persists on remote SMB shares; host-local state is mounts and Windows SMB mappings.
- Dependencies/integration points: Windows HostProcess support, kubelet plugin registry, node ServiceAccount, system-node-critical priority, and the Windows SMB plugin image variant.
- Risks: high host privilege, HostProcess cluster prerequisites, missing plugin directory creation, and use of canary images in the current deploy file.
- Test signals: DaemonSet rollout on Windows nodes, plugin registration, successful Windows PVC mount, and absence of stale SMB mappings after unmount.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows-hostprocess.yaml -->
