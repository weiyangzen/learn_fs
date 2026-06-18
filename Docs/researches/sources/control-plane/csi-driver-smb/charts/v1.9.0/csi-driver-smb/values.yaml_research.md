<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/values.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/values.yaml

- Purpose: default values for the v1.9.0 Helm chart. They define image repositories/tags, driver name, feature flags, service accounts, RBAC naming, controller/node scheduling, kubelet paths, resource requests, metrics, liveness ports, and Windows/Linux enablement.
- Important APIs/types/functions: key values include `driver.name=smb.csi.k8s.io`, `image.baseRepo=registry.k8s.io/sig-storage`, image tags `v1.9.0, v3.2.0, v2.7.0, v2.5.1`, controller metrics `29644`, node metrics `29645`, Linux kubelet `/var/lib/kubelet`, and Windows kubelet `C:\var\lib\kubelet`. `feature.enableGetVolumeStats` is `true`.
- Control flow: the chart templates read this file to decide which DaemonSets render, what sidecar versions run, how pods are scheduled, what driver name is registered, and what flags are passed to `smbplugin`.
- State and persistence behavior: values do not store runtime state, but they select host paths and resource settings that determine where sockets, plugin registration, mount points, and temporary controller mounts are created.
- Dependencies/integration points: tightly coupled to all chart templates in the same version, Kubernetes node labels/tolerations, CSI sidecar image compatibility, SMB plugin image tags, and optional user-provided security context/pod metadata.
- Risks: stale sidecar tags, disabled Windows by default, wrong kubelet root, or a custom driver name not reflected in StorageClasses/PVs can make the deployment unusable. Resource limits are low and may need tuning in large clusters.
- Test signals: `helm template` with default and Windows-enabled overrides; compare rendered image tags and flags with the intended release before installing.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/values.yaml -->
