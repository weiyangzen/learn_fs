# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

## Purpose
This template renders the Windows HostProcess SMB CSI node `DaemonSet` for chart `v1.19.0`. It is selected when `.Values.windows.enabled` and `.Values.windows.useHostProcessContainers` are both true, replacing the legacy CSI proxy pipe-mounted node pod with host-process containers.

## Important APIs, Types, And Functions
The resource is an `apps/v1/DaemonSet` with pod-level `windowsOptions.hostProcess: true`, `runAsUserName: "NT AUTHORITY\SYSTEM"`, `hostNetwork: true`, and `seccompProfile: RuntimeDefault`. An init container runs PowerShell to create the kubelet plugin directory. Runtime containers are `node-driver-registrar` and `smb`, using Windows executables and `CSI_ENDPOINT` values under `.Values.windows.kubelet\plugins\.Values.driver.name\csi.sock`.

## Control Flow
Helm gates the whole file on the HostProcess feature switch, applies Windows node selector/tolerations/affinity, adds pull secrets, and composes `-windows-hp` SMB image tags. The SMB plugin receives volume stats, SMB mapping cleanup, and `--enable-windows-host-process=true` flags.

## State And Persistence Behavior
HostProcess containers run directly against host networking and host filesystem context. The persistent state is the kubelet plugin and registry directories on the Windows node plus any SMB mappings created by the driver.

## Dependencies And Integration Points
This requires Kubernetes Windows HostProcess support, a compatible SMB plugin image with `-windows-hp` tag, registrar support for `--plugin-registration-path`, the node service account, and an exact driver-name match with the `CSIDriver` object.

## Risks And Test Signals
Risk is high because HostProcess grants host-level Windows privileges. Path escaping, missing plugin directory creation, unsupported cluster versions, and image tag mismatches can block registration. Test with `helm template`, Windows DaemonSet rollout, kubelet registration logs, and SMB PVC mount/unmount on HostProcess-capable nodes.
