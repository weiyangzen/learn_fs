# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/values.yaml

## Purpose
This `v1.19.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context and commented `storageClasses` examples.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, csiResizer, livenessProbe, nodeDriverRegistrar, csiproxy. Feature gates present here are: enableGetVolumeStats, enableInlineVolume. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths, Kerberos cache settings.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.19.0` and matching CSI sidecars. This version configures default-enabled Windows support with HostProcess containers. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
