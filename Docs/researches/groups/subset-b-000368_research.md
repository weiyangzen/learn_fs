# Research Group: subset-b-000368

Source-tree-aligned research sections for the CSI SMB driver files in this group. Each section preserves the source path for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-controller.yaml

- Purpose: Helm template for the v1.6.0 controller Deployment. It renders the Linux-only `csi-smb-controller` control-plane pod with the external provisioner, liveness probe, and `smb` CSI controller container wired to a shared `/csi/csi.sock` socket.
- Important APIs/types/functions: emits `apps/v1` `Deployment`; consumes `.Values.controller`, `.Values.image`, `.Values.serviceAccount.controller`, `.Values.driver.name`, pod labels/annotations, pull secrets, affinity, tolerations, and optional security context. The generated containers use `csi-provisioner`, `liveness-probe`, and `smb` images from chart values.
- Control flow: Helm renders values into container args, then Kubernetes starts the sidecars. The provisioner talks to the driver over `/csi/csi.sock`, uses leader election in the release namespace, and creates metadata; the SMB container runs `--endpoint=$(CSI_ENDPOINT)`, exports metrics, and serves health checks.
- State and persistence behavior: controller state is limited to an `emptyDir` CSI socket volume. Provisioned volumes persist in Kubernetes PV/PVC objects and remote SMB shares, not in this pod. `workingMountDir` defaults to `/tmp` and is used only for temporary controller-side share mounts.
- Dependencies/integration points: Kubernetes scheduling, Helm release namespace, CSI external-provisioner, CSI liveness probe, the SMB plugin image, RBAC from the companion chart template, and optional image pull secrets. Metrics integrate through the configured controller metrics port.
- Risks: the `smb` container is privileged, leader-election RBAC must match the namespace, and incorrect image repository prefix handling can render non-pullable images. Controller DNS policy, master/control-plane node selectors, and tolerations can accidentally pin the pod to unsuitable nodes.
- Test signals: validate with `helm template` plus `kubectl apply --dry-run=server`; runtime health is visible via `/healthz`, controller metrics, and provisioner events during PVC creation.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-driver.yaml

- Purpose: Helm template for the v1.6.0 `CSIDriver` object named from `.Values.driver.name`, normally `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` and sets `attachRequired: false` because SMB volumes are network filesystem mounts and do not need a Kubernetes attach/detach controller.
- Control flow: this object is applied before or alongside controller/node manifests so Kubernetes knows driver-level capabilities while external provisioner and kubelet registration handle volume lifecycle operations.
- State and persistence behavior: the object persists only CSI driver metadata in the Kubernetes API; it stores no SMB credentials, mount state, or volume data.
- Dependencies/integration points: must match the driver name passed to controller/node pods and the provisioner name used in StorageClasses, PVs, inline volumes, and examples.
- Risks: a name mismatch makes PVC provisioning or pod mounts fail; clusters too old for `storage.k8s.io/v1` need historical manifests instead.
- Test signals: server-side dry-run and `kubectl get csidriver smb.csi.k8s.io`; successful PVC provisioning confirms the object lines up with the running plugin.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

- Purpose: Helm template for the v1.6.0 Windows node DaemonSet. It installs the SMB CSI node plugin on Windows workers using node-driver-registrar, liveness-probe, and CSI proxy pipe mounts.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.windows.enabled` is true. It consumes `.Values.windows.kubelet`, `.Values.windows.removeSMBMappingDuringUnmount`, `.Values.node`, `.Values.driver.name`, and image settings for the registrar, liveness probe, and SMB plugin.
- Control flow: the liveness probe checks the Windows CSI socket, node-driver-registrar registers the plugin path under the kubelet plugin registry, and the `smb` process runs with `--endpoint`, `--nodeid`, `--metrics-address`, `--enable-get-volume-stats`, and the Windows unmount cleanup flag.
- State and persistence behavior: the DaemonSet binds the Windows kubelet directory, plugin directory, registration directory, and CSI proxy named pipes. Persistent data lives on the SMB share; local state is sockets, plugin registration files, and transient mount mappings.
- Dependencies/integration points: requires Windows nodes, kubelet host paths, CSI proxy filesystem and SMB APIs, Kubernetes fieldRef for `spec.nodeName`, and the node ServiceAccount/RBAC from the chart. It also carries beta CSI proxy pipe compatibility in these versions.
- Risks: incorrect Windows path escaping can break registration, missing CSI proxy pipes prevents mount/unmount calls, and stale SMB mappings can survive unmount if the cleanup flag is disabled or unsupported. HostPath and named-pipe access are high-trust integrations.
- Test signals: verify via `helm template` on a Windows-enabled values file, node-driver-registrar liveness, kubelet plugin registration, and an SMB PVC mounted by a Windows workload.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node.yaml

- Purpose: Helm template for the v1.6.0 Linux node DaemonSet. It installs the SMB CSI node service on every Linux node and exposes the CSI socket to kubelet registration.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.linux.enabled` is true. Key values are `.Values.linux.kubelet`, `.Values.node.maxUnavailable`, `.Values.feature.enableGetVolumeStats`, `.Values.driver.name`, image tags, tolerations, affinity, and node selectors.
- Control flow: Kubernetes schedules one pod per Linux node; liveness-probe monitors `/csi/csi.sock`, node-driver-registrar registers the socket under `${kubelet}/plugins_registry`, and the `smb` container starts with node ID from `spec.nodeName` and metrics/stat flags.
- State and persistence behavior: hostPath volumes create/use `${kubelet}/plugins/<driver>`, `${kubelet}/plugins_registry`, and the kubelet root with bidirectional mount propagation. SMB volume content persists remotely; local state is mounts and registration sockets.
- Dependencies/integration points: kubelet CSI plugin registry, Linux mount propagation, privileged SMB plugin container, CSI liveness and registrar sidecars, node ServiceAccount, and RBAC permitting node secret reads when used with secrets.
- Risks: privileged hostPath mount access is required; wrong kubelet path or driver name breaks registration; mount propagation must be bidirectional; enabling stats may add filesystem stat load on nodes.
- Test signals: `helm template` rendering, DaemonSet rollout, registrar health, kubelet `CSINode` driver entry, and a Linux pod mounting an SMB PVC are the main validation signals.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

- Purpose: Helm RBAC template for v1.6.0; it creates CSI SMB service accounts and ClusterRole/ClusterRoleBinding resources when `.Values.serviceAccount.create` and `.Values.rbac.create` are enabled.
- Important APIs/types/functions: emits `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC/StorageClass/Event/CSINode/Node/Lease access plus read access to Secrets; later template shape includes a separate node ServiceAccount.
- Control flow: Helm renders names from `.Values.serviceAccount.*` and `.Values.rbac.name`; controller sidecars use the controller ServiceAccount for provisioning and leader election, while node pods use the node ServiceAccount when the chart creates it.
- State and persistence behavior: all state is Kubernetes RBAC and identity objects. No application data is stored, but these grants control which secrets and storage objects the CSI components can read or mutate.
- Dependencies/integration points: consumed by controller Deployment, Linux/Windows DaemonSets, CSI external-provisioner leader election, and secret-backed SMB credentials referenced by StorageClasses/PVs.
- Risks: cluster-wide Secret `get` is sensitive; insufficient Lease/Event/PV verbs cause provisioning failures; disabling RBAC creation requires equivalent pre-existing roles.
- Test signals: `helm template`/server-side dry-run plus a PVC provisioning attempt; RBAC denial messages in provisioner logs are the primary failure signal.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/values.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/values.yaml

- Purpose: default values for the v1.6.0 Helm chart. They define image repositories/tags, driver name, feature flags, service accounts, RBAC naming, controller/node scheduling, kubelet paths, resource requests, metrics, liveness ports, and Windows/Linux enablement.
- Important APIs/types/functions: key values include `driver.name=smb.csi.k8s.io`, `image.baseRepo=registry.k8s.io/sig-storage`, image tags `v1.6.0, v3.1.0, v2.5.0, v2.4.0`, controller metrics `29644`, node metrics `29645`, Linux kubelet `/var/lib/kubelet`, and Windows kubelet `C:\var\lib\kubelet`. `feature.enableGetVolumeStats` is `false`.
- Control flow: the chart templates read this file to decide which DaemonSets render, what sidecar versions run, how pods are scheduled, what driver name is registered, and what flags are passed to `smbplugin`.
- State and persistence behavior: values do not store runtime state, but they select host paths and resource settings that determine where sockets, plugin registration, mount points, and temporary controller mounts are created.
- Dependencies/integration points: tightly coupled to all chart templates in the same version, Kubernetes node labels/tolerations, CSI sidecar image compatibility, SMB plugin image tags, and optional user-provided security context/pod metadata.
- Risks: stale sidecar tags, disabled Windows by default, wrong kubelet root, or a custom driver name not reflected in StorageClasses/PVs can make the deployment unusable. Resource limits are low and may need tuning in large clusters.
- Test signals: `helm template` with default and Windows-enabled overrides; compare rendered image tags and flags with the intended release before installing.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/Chart.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/Chart.yaml

- Purpose: Helm chart metadata for `csi-driver-smb` v1.7.0. It declares the package name, description, chart API version, chart version `v1.7.0`, and application version `v1.7.0`.
- Important APIs/types/functions: this is Helm `Chart.yaml` metadata, not a Kubernetes object. Helm uses it for chart packaging, dependency/index generation, and release identity.
- Control flow: packaging and install commands read this file before rendering templates; the chart version should track the directory and image defaults in `values.yaml`.
- State and persistence behavior: no runtime state; it is release metadata persisted only in chart archives and Helm release records.
- Dependencies/integration points: chart repository index, OCI/chart publishing workflows, `values.yaml`, and template labels that may surface chart/app versions.
- Risks: version drift between `Chart.yaml`, `values.yaml` image tags, and packaged tarballs can publish misleading install artifacts.
- Test signals: `helm lint`, `helm package`, and comparing chart index entries against this metadata.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-controller.yaml

- Purpose: Helm template for the v1.7.0 controller Deployment. It renders the Linux-only `csi-smb-controller` control-plane pod with the external provisioner, liveness probe, and `smb` CSI controller container wired to a shared `/csi/csi.sock` socket.
- Important APIs/types/functions: emits `apps/v1` `Deployment`; consumes `.Values.controller`, `.Values.image`, `.Values.serviceAccount.controller`, `.Values.driver.name`, pod labels/annotations, pull secrets, affinity, tolerations, and optional security context. The generated containers use `csi-provisioner`, `liveness-probe`, and `smb` images from chart values.
- Control flow: Helm renders values into container args, then Kubernetes starts the sidecars. The provisioner talks to the driver over `/csi/csi.sock`, uses leader election in the release namespace, and creates metadata; the SMB container runs `--endpoint=$(CSI_ENDPOINT)`, exports metrics, and serves health checks.
- State and persistence behavior: controller state is limited to an `emptyDir` CSI socket volume. Provisioned volumes persist in Kubernetes PV/PVC objects and remote SMB shares, not in this pod. `workingMountDir` defaults to `/tmp` and is used only for temporary controller-side share mounts.
- Dependencies/integration points: Kubernetes scheduling, Helm release namespace, CSI external-provisioner, CSI liveness probe, the SMB plugin image, RBAC from the companion chart template, and optional image pull secrets. Metrics integrate through the configured controller metrics port.
- Risks: the `smb` container is privileged, leader-election RBAC must match the namespace, and incorrect image repository prefix handling can render non-pullable images. Controller DNS policy, master/control-plane node selectors, and tolerations can accidentally pin the pod to unsuitable nodes.
- Test signals: validate with `helm template` plus `kubectl apply --dry-run=server`; runtime health is visible via `/healthz`, controller metrics, and provisioner events during PVC creation.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-driver.yaml

- Purpose: Helm template for the v1.7.0 `CSIDriver` object named from `.Values.driver.name`, normally `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` and sets `attachRequired: false` because SMB volumes are network filesystem mounts and do not need a Kubernetes attach/detach controller.
- Control flow: this object is applied before or alongside controller/node manifests so Kubernetes knows driver-level capabilities while external provisioner and kubelet registration handle volume lifecycle operations.
- State and persistence behavior: the object persists only CSI driver metadata in the Kubernetes API; it stores no SMB credentials, mount state, or volume data.
- Dependencies/integration points: must match the driver name passed to controller/node pods and the provisioner name used in StorageClasses, PVs, inline volumes, and examples.
- Risks: a name mismatch makes PVC provisioning or pod mounts fail; clusters too old for `storage.k8s.io/v1` need historical manifests instead.
- Test signals: server-side dry-run and `kubectl get csidriver smb.csi.k8s.io`; successful PVC provisioning confirms the object lines up with the running plugin.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

- Purpose: Helm template for the v1.7.0 Windows node DaemonSet. It installs the SMB CSI node plugin on Windows workers using node-driver-registrar, liveness-probe, and CSI proxy pipe mounts.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.windows.enabled` is true. It consumes `.Values.windows.kubelet`, `.Values.windows.removeSMBMappingDuringUnmount`, `.Values.node`, `.Values.driver.name`, and image settings for the registrar, liveness probe, and SMB plugin.
- Control flow: the liveness probe checks the Windows CSI socket, node-driver-registrar registers the plugin path under the kubelet plugin registry, and the `smb` process runs with `--endpoint`, `--nodeid`, `--metrics-address`, `--enable-get-volume-stats`, and the Windows unmount cleanup flag.
- State and persistence behavior: the DaemonSet binds the Windows kubelet directory, plugin directory, registration directory, and CSI proxy named pipes. Persistent data lives on the SMB share; local state is sockets, plugin registration files, and transient mount mappings.
- Dependencies/integration points: requires Windows nodes, kubelet host paths, CSI proxy filesystem and SMB APIs, Kubernetes fieldRef for `spec.nodeName`, and the node ServiceAccount/RBAC from the chart. It also carries beta CSI proxy pipe compatibility in these versions.
- Risks: incorrect Windows path escaping can break registration, missing CSI proxy pipes prevents mount/unmount calls, and stale SMB mappings can survive unmount if the cleanup flag is disabled or unsupported. HostPath and named-pipe access are high-trust integrations.
- Test signals: verify via `helm template` on a Windows-enabled values file, node-driver-registrar liveness, kubelet plugin registration, and an SMB PVC mounted by a Windows workload.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-node.yaml

- Purpose: Helm template for the v1.7.0 Linux node DaemonSet. It installs the SMB CSI node service on every Linux node and exposes the CSI socket to kubelet registration.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.linux.enabled` is true. Key values are `.Values.linux.kubelet`, `.Values.node.maxUnavailable`, `.Values.feature.enableGetVolumeStats`, `.Values.driver.name`, image tags, tolerations, affinity, and node selectors.
- Control flow: Kubernetes schedules one pod per Linux node; liveness-probe monitors `/csi/csi.sock`, node-driver-registrar registers the socket under `${kubelet}/plugins_registry`, and the `smb` container starts with node ID from `spec.nodeName` and metrics/stat flags.
- State and persistence behavior: hostPath volumes create/use `${kubelet}/plugins/<driver>`, `${kubelet}/plugins_registry`, and the kubelet root with bidirectional mount propagation. SMB volume content persists remotely; local state is mounts and registration sockets.
- Dependencies/integration points: kubelet CSI plugin registry, Linux mount propagation, privileged SMB plugin container, CSI liveness and registrar sidecars, node ServiceAccount, and RBAC permitting node secret reads when used with secrets.
- Risks: privileged hostPath mount access is required; wrong kubelet path or driver name breaks registration; mount propagation must be bidirectional; enabling stats may add filesystem stat load on nodes.
- Test signals: `helm template` rendering, DaemonSet rollout, registrar health, kubelet `CSINode` driver entry, and a Linux pod mounting an SMB PVC are the main validation signals.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/rbac-csi-smb.yaml

- Purpose: Helm RBAC template for v1.7.0; it creates CSI SMB service accounts and ClusterRole/ClusterRoleBinding resources when `.Values.serviceAccount.create` and `.Values.rbac.create` are enabled.
- Important APIs/types/functions: emits `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC/StorageClass/Event/CSINode/Node/Lease access plus read access to Secrets; later template shape includes a separate node ServiceAccount.
- Control flow: Helm renders names from `.Values.serviceAccount.*` and `.Values.rbac.name`; controller sidecars use the controller ServiceAccount for provisioning and leader election, while node pods use the node ServiceAccount when the chart creates it.
- State and persistence behavior: all state is Kubernetes RBAC and identity objects. No application data is stored, but these grants control which secrets and storage objects the CSI components can read or mutate.
- Dependencies/integration points: consumed by controller Deployment, Linux/Windows DaemonSets, CSI external-provisioner leader election, and secret-backed SMB credentials referenced by StorageClasses/PVs.
- Risks: cluster-wide Secret `get` is sensitive; insufficient Lease/Event/PV verbs cause provisioning failures; disabling RBAC creation requires equivalent pre-existing roles.
- Test signals: `helm template`/server-side dry-run plus a PVC provisioning attempt; RBAC denial messages in provisioner logs are the primary failure signal.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/values.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/values.yaml

- Purpose: default values for the v1.7.0 Helm chart. They define image repositories/tags, driver name, feature flags, service accounts, RBAC naming, controller/node scheduling, kubelet paths, resource requests, metrics, liveness ports, and Windows/Linux enablement.
- Important APIs/types/functions: key values include `driver.name=smb.csi.k8s.io`, `image.baseRepo=registry.k8s.io/sig-storage`, image tags `v1.7.0, v3.1.0, v2.6.0, v2.5.0`, controller metrics `29644`, node metrics `29645`, Linux kubelet `/var/lib/kubelet`, and Windows kubelet `C:\var\lib\kubelet`. `feature.enableGetVolumeStats` is `false`.
- Control flow: the chart templates read this file to decide which DaemonSets render, what sidecar versions run, how pods are scheduled, what driver name is registered, and what flags are passed to `smbplugin`.
- State and persistence behavior: values do not store runtime state, but they select host paths and resource settings that determine where sockets, plugin registration, mount points, and temporary controller mounts are created.
- Dependencies/integration points: tightly coupled to all chart templates in the same version, Kubernetes node labels/tolerations, CSI sidecar image compatibility, SMB plugin image tags, and optional user-provided security context/pod metadata.
- Risks: stale sidecar tags, disabled Windows by default, wrong kubelet root, or a custom driver name not reflected in StorageClasses/PVs can make the deployment unusable. Resource limits are low and may need tuning in large clusters.
- Test signals: `helm template` with default and Windows-enabled overrides; compare rendered image tags and flags with the intended release before installing.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/Chart.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/Chart.yaml

- Purpose: Helm chart metadata for `csi-driver-smb` v1.8.0. It declares the package name, description, chart API version, chart version `v1.8.0`, and application version `v1.8.0`.
- Important APIs/types/functions: this is Helm `Chart.yaml` metadata, not a Kubernetes object. Helm uses it for chart packaging, dependency/index generation, and release identity.
- Control flow: packaging and install commands read this file before rendering templates; the chart version should track the directory and image defaults in `values.yaml`.
- State and persistence behavior: no runtime state; it is release metadata persisted only in chart archives and Helm release records.
- Dependencies/integration points: chart repository index, OCI/chart publishing workflows, `values.yaml`, and template labels that may surface chart/app versions.
- Risks: version drift between `Chart.yaml`, `values.yaml` image tags, and packaged tarballs can publish misleading install artifacts.
- Test signals: `helm lint`, `helm package`, and comparing chart index entries against this metadata.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-controller.yaml

- Purpose: Helm template for the v1.8.0 controller Deployment. It renders the Linux-only `csi-smb-controller` control-plane pod with the external provisioner, liveness probe, and `smb` CSI controller container wired to a shared `/csi/csi.sock` socket.
- Important APIs/types/functions: emits `apps/v1` `Deployment`; consumes `.Values.controller`, `.Values.image`, `.Values.serviceAccount.controller`, `.Values.driver.name`, pod labels/annotations, pull secrets, affinity, tolerations, and optional security context. The generated containers use `csi-provisioner`, `liveness-probe`, and `smb` images from chart values.
- Control flow: Helm renders values into container args, then Kubernetes starts the sidecars. The provisioner talks to the driver over `/csi/csi.sock`, uses leader election in the release namespace, and creates metadata; the SMB container runs `--endpoint=$(CSI_ENDPOINT)`, exports metrics, and serves health checks.
- State and persistence behavior: controller state is limited to an `emptyDir` CSI socket volume. Provisioned volumes persist in Kubernetes PV/PVC objects and remote SMB shares, not in this pod. `workingMountDir` defaults to `/tmp` and is used only for temporary controller-side share mounts.
- Dependencies/integration points: Kubernetes scheduling, Helm release namespace, CSI external-provisioner, CSI liveness probe, the SMB plugin image, RBAC from the companion chart template, and optional image pull secrets. Metrics integrate through the configured controller metrics port.
- Risks: the `smb` container is privileged, leader-election RBAC must match the namespace, and incorrect image repository prefix handling can render non-pullable images. Controller DNS policy, master/control-plane node selectors, and tolerations can accidentally pin the pod to unsuitable nodes.
- Test signals: validate with `helm template` plus `kubectl apply --dry-run=server`; runtime health is visible via `/healthz`, controller metrics, and provisioner events during PVC creation.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-driver.yaml

- Purpose: Helm template for the v1.8.0 `CSIDriver` object named from `.Values.driver.name`, normally `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` and sets `attachRequired: false` because SMB volumes are network filesystem mounts and do not need a Kubernetes attach/detach controller.
- Control flow: this object is applied before or alongside controller/node manifests so Kubernetes knows driver-level capabilities while external provisioner and kubelet registration handle volume lifecycle operations.
- State and persistence behavior: the object persists only CSI driver metadata in the Kubernetes API; it stores no SMB credentials, mount state, or volume data.
- Dependencies/integration points: must match the driver name passed to controller/node pods and the provisioner name used in StorageClasses, PVs, inline volumes, and examples.
- Risks: a name mismatch makes PVC provisioning or pod mounts fail; clusters too old for `storage.k8s.io/v1` need historical manifests instead.
- Test signals: server-side dry-run and `kubectl get csidriver smb.csi.k8s.io`; successful PVC provisioning confirms the object lines up with the running plugin.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

- Purpose: Helm template for the v1.8.0 Windows node DaemonSet. It installs the SMB CSI node plugin on Windows workers using node-driver-registrar, liveness-probe, and CSI proxy pipe mounts.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.windows.enabled` is true. It consumes `.Values.windows.kubelet`, `.Values.windows.removeSMBMappingDuringUnmount`, `.Values.node`, `.Values.driver.name`, and image settings for the registrar, liveness probe, and SMB plugin.
- Control flow: the liveness probe checks the Windows CSI socket, node-driver-registrar registers the plugin path under the kubelet plugin registry, and the `smb` process runs with `--endpoint`, `--nodeid`, `--metrics-address`, `--enable-get-volume-stats`, and the Windows unmount cleanup flag.
- State and persistence behavior: the DaemonSet binds the Windows kubelet directory, plugin directory, registration directory, and CSI proxy named pipes. Persistent data lives on the SMB share; local state is sockets, plugin registration files, and transient mount mappings.
- Dependencies/integration points: requires Windows nodes, kubelet host paths, CSI proxy filesystem and SMB APIs, Kubernetes fieldRef for `spec.nodeName`, and the node ServiceAccount/RBAC from the chart. It also carries beta CSI proxy pipe compatibility in these versions.
- Risks: incorrect Windows path escaping can break registration, missing CSI proxy pipes prevents mount/unmount calls, and stale SMB mappings can survive unmount if the cleanup flag is disabled or unsupported. HostPath and named-pipe access are high-trust integrations.
- Test signals: verify via `helm template` on a Windows-enabled values file, node-driver-registrar liveness, kubelet plugin registration, and an SMB PVC mounted by a Windows workload.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node.yaml

- Purpose: Helm template for the v1.8.0 Linux node DaemonSet. It installs the SMB CSI node service on every Linux node and exposes the CSI socket to kubelet registration.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.linux.enabled` is true. Key values are `.Values.linux.kubelet`, `.Values.node.maxUnavailable`, `.Values.feature.enableGetVolumeStats`, `.Values.driver.name`, image tags, tolerations, affinity, and node selectors.
- Control flow: Kubernetes schedules one pod per Linux node; liveness-probe monitors `/csi/csi.sock`, node-driver-registrar registers the socket under `${kubelet}/plugins_registry`, and the `smb` container starts with node ID from `spec.nodeName` and metrics/stat flags.
- State and persistence behavior: hostPath volumes create/use `${kubelet}/plugins/<driver>`, `${kubelet}/plugins_registry`, and the kubelet root with bidirectional mount propagation. SMB volume content persists remotely; local state is mounts and registration sockets.
- Dependencies/integration points: kubelet CSI plugin registry, Linux mount propagation, privileged SMB plugin container, CSI liveness and registrar sidecars, node ServiceAccount, and RBAC permitting node secret reads when used with secrets.
- Risks: privileged hostPath mount access is required; wrong kubelet path or driver name breaks registration; mount propagation must be bidirectional; enabling stats may add filesystem stat load on nodes.
- Test signals: `helm template` rendering, DaemonSet rollout, registrar health, kubelet `CSINode` driver entry, and a Linux pod mounting an SMB PVC are the main validation signals.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/rbac-csi-smb.yaml

- Purpose: Helm RBAC template for v1.8.0; it creates CSI SMB service accounts and ClusterRole/ClusterRoleBinding resources when `.Values.serviceAccount.create` and `.Values.rbac.create` are enabled.
- Important APIs/types/functions: emits `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC/StorageClass/Event/CSINode/Node/Lease access plus read access to Secrets; later template shape includes a separate node ServiceAccount.
- Control flow: Helm renders names from `.Values.serviceAccount.*` and `.Values.rbac.name`; controller sidecars use the controller ServiceAccount for provisioning and leader election, while node pods use the node ServiceAccount when the chart creates it.
- State and persistence behavior: all state is Kubernetes RBAC and identity objects. No application data is stored, but these grants control which secrets and storage objects the CSI components can read or mutate.
- Dependencies/integration points: consumed by controller Deployment, Linux/Windows DaemonSets, CSI external-provisioner leader election, and secret-backed SMB credentials referenced by StorageClasses/PVs.
- Risks: cluster-wide Secret `get` is sensitive; insufficient Lease/Event/PV verbs cause provisioning failures; disabling RBAC creation requires equivalent pre-existing roles.
- Test signals: `helm template`/server-side dry-run plus a PVC provisioning attempt; RBAC denial messages in provisioner logs are the primary failure signal.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/values.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/values.yaml

- Purpose: default values for the v1.8.0 Helm chart. They define image repositories/tags, driver name, feature flags, service accounts, RBAC naming, controller/node scheduling, kubelet paths, resource requests, metrics, liveness ports, and Windows/Linux enablement.
- Important APIs/types/functions: key values include `driver.name=smb.csi.k8s.io`, `image.baseRepo=registry.k8s.io/sig-storage`, image tags `v1.8.0, v3.2.0, v2.7.0, v2.5.1`, controller metrics `29644`, node metrics `29645`, Linux kubelet `/var/lib/kubelet`, and Windows kubelet `C:\var\lib\kubelet`. `feature.enableGetVolumeStats` is `true`.
- Control flow: the chart templates read this file to decide which DaemonSets render, what sidecar versions run, how pods are scheduled, what driver name is registered, and what flags are passed to `smbplugin`.
- State and persistence behavior: values do not store runtime state, but they select host paths and resource settings that determine where sockets, plugin registration, mount points, and temporary controller mounts are created.
- Dependencies/integration points: tightly coupled to all chart templates in the same version, Kubernetes node labels/tolerations, CSI sidecar image compatibility, SMB plugin image tags, and optional user-provided security context/pod metadata.
- Risks: stale sidecar tags, disabled Windows by default, wrong kubelet root, or a custom driver name not reflected in StorageClasses/PVs can make the deployment unusable. Resource limits are low and may need tuning in large clusters.
- Test signals: `helm template` with default and Windows-enabled overrides; compare rendered image tags and flags with the intended release before installing.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.8.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/Chart.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/Chart.yaml

- Purpose: Helm chart metadata for `csi-driver-smb` v1.9.0. It declares the package name, description, chart API version, chart version `v1.9.0`, and application version `v1.9.0`.
- Important APIs/types/functions: this is Helm `Chart.yaml` metadata, not a Kubernetes object. Helm uses it for chart packaging, dependency/index generation, and release identity.
- Control flow: packaging and install commands read this file before rendering templates; the chart version should track the directory and image defaults in `values.yaml`.
- State and persistence behavior: no runtime state; it is release metadata persisted only in chart archives and Helm release records.
- Dependencies/integration points: chart repository index, OCI/chart publishing workflows, `values.yaml`, and template labels that may surface chart/app versions.
- Risks: version drift between `Chart.yaml`, `values.yaml` image tags, and packaged tarballs can publish misleading install artifacts.
- Test signals: `helm lint`, `helm package`, and comparing chart index entries against this metadata.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-controller.yaml

- Purpose: Helm template for the v1.9.0 controller Deployment. It renders the Linux-only `csi-smb-controller` control-plane pod with the external provisioner, liveness probe, and `smb` CSI controller container wired to a shared `/csi/csi.sock` socket.
- Important APIs/types/functions: emits `apps/v1` `Deployment`; consumes `.Values.controller`, `.Values.image`, `.Values.serviceAccount.controller`, `.Values.driver.name`, pod labels/annotations, pull secrets, affinity, tolerations, and optional security context. The generated containers use `csi-provisioner`, `liveness-probe`, and `smb` images from chart values.
- Control flow: Helm renders values into container args, then Kubernetes starts the sidecars. The provisioner talks to the driver over `/csi/csi.sock`, uses leader election in the release namespace, and creates metadata; the SMB container runs `--endpoint=$(CSI_ENDPOINT)`, exports metrics, and serves health checks.
- State and persistence behavior: controller state is limited to an `emptyDir` CSI socket volume. Provisioned volumes persist in Kubernetes PV/PVC objects and remote SMB shares, not in this pod. `workingMountDir` defaults to `/tmp` and is used only for temporary controller-side share mounts.
- Dependencies/integration points: Kubernetes scheduling, Helm release namespace, CSI external-provisioner, CSI liveness probe, the SMB plugin image, RBAC from the companion chart template, and optional image pull secrets. Metrics integrate through the configured controller metrics port.
- Risks: the `smb` container is privileged, leader-election RBAC must match the namespace, and incorrect image repository prefix handling can render non-pullable images. Controller DNS policy, master/control-plane node selectors, and tolerations can accidentally pin the pod to unsuitable nodes.
- Test signals: validate with `helm template` plus `kubectl apply --dry-run=server`; runtime health is visible via `/healthz`, controller metrics, and provisioner events during PVC creation.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-driver.yaml

- Purpose: Helm template for the v1.9.0 `CSIDriver` object named from `.Values.driver.name`, normally `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` and sets `attachRequired: false` because SMB volumes are network filesystem mounts and do not need a Kubernetes attach/detach controller.
- Control flow: this object is applied before or alongside controller/node manifests so Kubernetes knows driver-level capabilities while external provisioner and kubelet registration handle volume lifecycle operations.
- State and persistence behavior: the object persists only CSI driver metadata in the Kubernetes API; it stores no SMB credentials, mount state, or volume data.
- Dependencies/integration points: must match the driver name passed to controller/node pods and the provisioner name used in StorageClasses, PVs, inline volumes, and examples.
- Risks: a name mismatch makes PVC provisioning or pod mounts fail; clusters too old for `storage.k8s.io/v1` need historical manifests instead.
- Test signals: server-side dry-run and `kubectl get csidriver smb.csi.k8s.io`; successful PVC provisioning confirms the object lines up with the running plugin.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

- Purpose: Helm template for the v1.9.0 Windows node DaemonSet. It installs the SMB CSI node plugin on Windows workers using node-driver-registrar, liveness-probe, and CSI proxy pipe mounts.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.windows.enabled` is true. It consumes `.Values.windows.kubelet`, `.Values.windows.removeSMBMappingDuringUnmount`, `.Values.node`, `.Values.driver.name`, and image settings for the registrar, liveness probe, and SMB plugin.
- Control flow: the liveness probe checks the Windows CSI socket, node-driver-registrar registers the plugin path under the kubelet plugin registry, and the `smb` process runs with `--endpoint`, `--nodeid`, `--metrics-address`, `--enable-get-volume-stats`, and the Windows unmount cleanup flag.
- State and persistence behavior: the DaemonSet binds the Windows kubelet directory, plugin directory, registration directory, and CSI proxy named pipes. Persistent data lives on the SMB share; local state is sockets, plugin registration files, and transient mount mappings.
- Dependencies/integration points: requires Windows nodes, kubelet host paths, CSI proxy filesystem and SMB APIs, Kubernetes fieldRef for `spec.nodeName`, and the node ServiceAccount/RBAC from the chart. It also carries beta CSI proxy pipe compatibility in these versions.
- Risks: incorrect Windows path escaping can break registration, missing CSI proxy pipes prevents mount/unmount calls, and stale SMB mappings can survive unmount if the cleanup flag is disabled or unsupported. HostPath and named-pipe access are high-trust integrations.
- Test signals: verify via `helm template` on a Windows-enabled values file, node-driver-registrar liveness, kubelet plugin registration, and an SMB PVC mounted by a Windows workload.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-node.yaml

- Purpose: Helm template for the v1.9.0 Linux node DaemonSet. It installs the SMB CSI node service on every Linux node and exposes the CSI socket to kubelet registration.
- Important APIs/types/functions: emits an `apps/v1` `DaemonSet` when `.Values.linux.enabled` is true. Key values are `.Values.linux.kubelet`, `.Values.node.maxUnavailable`, `.Values.feature.enableGetVolumeStats`, `.Values.driver.name`, image tags, tolerations, affinity, and node selectors.
- Control flow: Kubernetes schedules one pod per Linux node; liveness-probe monitors `/csi/csi.sock`, node-driver-registrar registers the socket under `${kubelet}/plugins_registry`, and the `smb` container starts with node ID from `spec.nodeName` and metrics/stat flags.
- State and persistence behavior: hostPath volumes create/use `${kubelet}/plugins/<driver>`, `${kubelet}/plugins_registry`, and the kubelet root with bidirectional mount propagation. SMB volume content persists remotely; local state is mounts and registration sockets.
- Dependencies/integration points: kubelet CSI plugin registry, Linux mount propagation, privileged SMB plugin container, CSI liveness and registrar sidecars, node ServiceAccount, and RBAC permitting node secret reads when used with secrets.
- Risks: privileged hostPath mount access is required; wrong kubelet path or driver name breaks registration; mount propagation must be bidirectional; enabling stats may add filesystem stat load on nodes.
- Test signals: `helm template` rendering, DaemonSet rollout, registrar health, kubelet `CSINode` driver entry, and a Linux pod mounting an SMB PVC are the main validation signals.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/rbac-csi-smb.yaml

- Purpose: Helm RBAC template for v1.9.0; it creates CSI SMB service accounts and ClusterRole/ClusterRoleBinding resources when `.Values.serviceAccount.create` and `.Values.rbac.create` are enabled.
- Important APIs/types/functions: emits `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC/StorageClass/Event/CSINode/Node/Lease access plus read access to Secrets; later template shape includes a separate node ServiceAccount.
- Control flow: Helm renders names from `.Values.serviceAccount.*` and `.Values.rbac.name`; controller sidecars use the controller ServiceAccount for provisioning and leader election, while node pods use the node ServiceAccount when the chart creates it.
- State and persistence behavior: all state is Kubernetes RBAC and identity objects. No application data is stored, but these grants control which secrets and storage objects the CSI components can read or mutate.
- Dependencies/integration points: consumed by controller Deployment, Linux/Windows DaemonSets, CSI external-provisioner leader election, and secret-backed SMB credentials referenced by StorageClasses/PVs.
- Risks: cluster-wide Secret `get` is sensitive; insufficient Lease/Event/PV verbs cause provisioning failures; disabling RBAC creation requires equivalent pre-existing roles.
- Test signals: `helm template`/server-side dry-run plus a PVC provisioning attempt; RBAC denial messages in provisioner logs are the primary failure signal.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.9.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cloudbuild.yaml -->
# Research: sources/control-plane/csi-driver-smb/cloudbuild.yaml

- Purpose: Google Cloud Build configuration for multi-architecture CSI SMB image building in Kubernetes staging infrastructure.
- Important APIs/types/functions: uses Cloud Build `timeout: 7200s`, `ALLOW_LOOSE` substitutions, a `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud` builder, and runs `./.cloudbuild.sh` with `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME` environment variables.
- Control flow: Cloud Build injects substitutions, starts the builder image, and delegates all repo-specific build/push behavior to `.cloudbuild.sh`; this file mainly wires the release-tools contract to Kubernetes image promotion staging.
- State and persistence behavior: no repo runtime state; build outputs are container images pushed to the configured staging registry, with tags derived from `_GIT_TAG`/branch context.
- Dependencies/integration points: Kubernetes test-infra image-pushing jobs, csi-release-tools conventions, `.cloudbuild.sh`, Dockerfiles accepting a `binary` build argument, and `k8s-staging-sig-storage` registry permissions.
- Risks: loose substitutions can mask unset variables, builder image drift can break builds, and incorrect staging project or tag values push images to the wrong location.
- Test signals: Cloud Build status, image presence in staging registry, and successful downstream promotion jobs.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/Dockerfile -->
# Research: sources/control-plane/csi-driver-smb/cmd/smbplugin/Dockerfile

- Purpose: Linux container image recipe for the SMB CSI driver executable.
- Important APIs/types/functions: starts from `registry.k8s.io/build-image/debian-base:bookworm-v1.0.8`, installs `ca-certificates`, `cifs-utils`, `util-linux`, `e2fsprogs`, `mount`, `udev`, and `xfsprogs`, accepts `ARCH` and `binary` build args, copies the compiled `smbplugin` to `/smbplugin`, writes a Kerberos cache default to `/etc/krb5.conf`, and sets `/smbplugin` as entrypoint.
- Control flow: release tooling builds the Go binary for an architecture, passes it as `binary`, and Docker packages it with SMB/CIFS mount utilities needed by node and controller operations.
- State and persistence behavior: image build state is immutable layers. Runtime persistence comes from mounted kubelet/CSI paths and remote SMB shares, not the container filesystem.
- Dependencies/integration points: Debian base image, package repositories, release build output layout `_output/${ARCH}/smbplugin`, Kerberos cache directory expectations, and Kubernetes manifests that run this image privileged on nodes/controllers.
- Risks: package upgrades during build reduce reproducibility, base image CVEs require rebuilds, and missing CIFS/Kerberos utilities would break mount modes used by StorageClasses.
- Test signals: image build success, vulnerability scans, and node mount tests including Kerberos-backed mounts.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/main.go -->
# Research: sources/control-plane/csi-driver-smb/cmd/smbplugin/main.go

- Purpose: command entrypoint for `smbplugin`, the CSI SMB driver process used by controller and node manifests.
- Important APIs/types/functions: defines flags for CSI endpoint, node ID, driver name, version output, metrics address, kubeconfig, volume stats, Windows SMB mapping cleanup, working mount dir, stats cache expiration, Kerberos cache directory/prefix, default delete policy, archived-volume cleanup, and Windows HostProcess mode. `handle()` builds `smb.DriverOptions`, calls `smb.NewDriver`, and runs `driver.Run`; `exportMetrics()`, `serveMetrics()`, and `trapClosedConnErr()` implement Prometheus metrics serving.
- Control flow: `main()` parses flags; `-ver` prints `smb.GetVersionYAML`; otherwise it warns on empty node ID, starts metrics if configured, creates the driver, and blocks in CSI serving. Metrics are served asynchronously on `/metrics` through the legacy registry.
- State and persistence behavior: process state is flag-derived configuration and metrics listener state. Durable volume state is delegated to `pkg/smb`; this entrypoint only passes cache directories, mount working directory, and delete/cleanup policies.
- Dependencies/integration points: `github.com/kubernetes-csi/csi-driver-smb/pkg/smb`, Kubernetes component-base metrics, `klog`, net/http, CSI endpoints from manifests, Kerberos defaults from image config, and kubeconfig for out-of-cluster use.
- Risks: metrics listener failures only warn and continue; `nodeid` is allowed empty for controller but dangerous for node mode; `trapClosedConnErr` relies on error string matching; privileged mount behavior is hidden in the driver package.
- Test signals: `main_test.go` covers version-path exit behavior and closed-listener error filtering; broader coverage requires integration/e2e CSI tests for flag combinations and node/controller modes.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/main_test.go -->
# Research: sources/control-plane/csi-driver-smb/cmd/smbplugin/main_test.go

- Purpose: unit tests for selected behavior in the `smbplugin` command entrypoint.
- Important APIs/types/functions: `TestMain` mutates `os.Args` to pass `-ver`, captures stdout with an `os.Pipe`, replaces the package-level `exit` function, invokes `main()`, and asserts exit code 0. `TestTrapClosedConnErr` checks that `net.ErrClosed` and nil map to nil while an arbitrary error is preserved.
- Control flow: tests exercise the version-output branch without terminating the test process and directly call the listener-error normalization helper.
- State and persistence behavior: modifies global process state (`os.Args`, `os.Stdout`, and `exit`) and restores it after the call. It creates no persistent files or Kubernetes resources.
- Dependencies/integration points: relies on `smb.GetVersionYAML` succeeding for the default driver name and Go standard library `testing`, `net`, `os`, and `reflect`.
- Risks: global state mutation can leak if assertions panic before restoration; test does not assert stdout content; `reflect.DeepEqual` on separately formatted errors is brittle for richer error types.
- Test signals: provides a basic command smoke test and helper coverage, but does not test `handle()`, metrics serving success, flag-to-DriverOptions mapping, or CSI driver startup.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/cmd/smbplugin/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-controller.yaml

- Purpose: current static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, `smb` controller service, and in current manifests also the CSI resizer.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v6.2.0, registry.k8s.io/sig-storage/csi-resizer:v2.1.0, registry.k8s.io/sig-storage/livenessprobe:v2.18.0, gcr.io/k8s-staging-sig-storage/smbplugin:canary. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-driver.yaml

- Purpose: current static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-driver.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows.yaml

- Purpose: current Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.16.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0, gcr.io/k8s-staging-sig-storage/smbplugin:canary. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/csi-smb-node.yaml

- Purpose: current Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.18.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.16.0, gcr.io/k8s-staging-sig-storage/smbplugin:canary. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/cloning/nginx-pod-restored-cloning.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/cloning/nginx-pod-restored-cloning.yaml

- Purpose: pod workload example mounting an SMB PVC and continuously appending timestamps to validate read/write behavior.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `Pod`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.17.3-alpine`; names include `nginx-smb-restored-cloning`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Continuous write loop is only a smoke test and can grow remote data; it assumes PVC, StorageClass, and credentials are already present.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/cloning/nginx-pod-restored-cloning.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/cloning/pvc-smb-cloning.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/cloning/pvc-smb-cloning.yaml

- Purpose: PVC clone example that requests a new SMB-backed PVC from source PVC `pvc-smb`.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `PersistentVolumeClaim`; notable images `none`; names include `pvc-smb-cloning, pvc-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: PVC cloning requires CSI snapshot/clone support and same-namespace source access; source PVC data consistency depends on workload quiescence.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/cloning/pvc-smb-cloning.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/daemonset-ephemeral.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/daemonset-ephemeral.yaml

- Purpose: Linux DaemonSet example using an ephemeral volumeClaimTemplate backed by StorageClass `smb` on each node.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `DaemonSet`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.19.5`; names include `daemonset-smb-ephemeral`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Creates per-pod PVCs and writes continuously; cleanup depends on ephemeral volume lifecycle and StorageClass reclaim behavior.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/daemonset-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/deployment.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/deployment.yaml

- Purpose: Linux Deployment example with an inline PVC definition and a pod that writes timestamps into `/mnt/smb/outfile`.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `PersistentVolumeClaim, Deployment`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.19.5`; names include `pvc-smb, deployment-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Continuous write loop can grow data indefinitely; deployment assumes the `smb` StorageClass and credentials already exist.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/metrics/csi-smb-controller-svc.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/metrics/csi-smb-controller-svc.yaml

- Purpose: Service example exposing the controller metrics port `29644` through a LoadBalancer in kube-system.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `Service`; notable images `none`; names include `csi-smb-controller`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: LoadBalancer can expose operational metrics outside the cluster; selector must match the controller labels and network policy should be considered.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/metrics/csi-smb-controller-svc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb-inline-volume.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb-inline-volume.yaml

- Purpose: pod example using an inline CSI volume with direct SMB `source`, secret name, and mount options instead of a PVC.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `Pod`; notable images `mcr.microsoft.com/mirror/docker/library/nginx:1.23`; names include `nginx-smb-inline-volume, nginx-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Inline volume settings couple credentials and source to the pod spec; secret namespace defaults to the pod namespace; unsuitable for reusable storage policy.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb-inline-volume.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb.yaml

- Purpose: pod workload example mounting an SMB PVC and continuously appending timestamps to validate read/write behavior.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `Pod`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.17.3-alpine`; names include `nginx-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Continuous write loop is only a smoke test and can grow remote data; it assumes PVC, StorageClass, and credentials are already present.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/nginx-pod-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/pv-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/pv-smb.yaml

- Purpose: static PersistentVolume example for an SMB share, including CSI volumeHandle/source and node-stage secret reference.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `PersistentVolume`; notable images `none`; names include `pv-smb, smbcreds`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: `volumeHandle` must be globally unique; static PVs rely on correct secret namespace and manual lifecycle; mount option mistakes affect all bound pods.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/pv-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/pvc-smb-static.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/pvc-smb-static.yaml

- Purpose: PVC example that binds explicitly to the static `pv-smb` volume with `ReadWriteMany` access.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `PersistentVolumeClaim`; notable images `none`; names include `pvc-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Hard binding to `pv-smb` fails if the PV is absent, already bound, or has incompatible capacity/access modes.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/pvc-smb-static.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/pvc-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/pvc-smb.yaml

- Purpose: basic dynamic PVC example using StorageClass `smb` and `ReadWriteMany` access.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `PersistentVolumeClaim`; notable images `none`; names include `pvc-smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Provisioning depends on the StorageClass and secrets being installed first; default namespace coupling is implicit.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/pvc-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/pv-smb-csi.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/pv-smb-csi.yaml

- Purpose: static PersistentVolume example for an SMB share, including CSI volumeHandle/source and node-stage secret reference.
- Important APIs/types/functions: Kubernetes APIs `v1`; kinds `PersistentVolume`; notable images `none`; names include `pv-smb, smbcreds`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: `volumeHandle` must be globally unique; static PVs rely on correct secret namespace and manual lifecycle; mount option mistakes affect all bound pods.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/pv-smb-csi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-lb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-lb.yaml

- Purpose: example SMB server Service/Deployment exposed through a LoadBalancer on port 445 for demos or external clients.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `Service, Deployment`; notable images `andyzhangx/samba:win-fix`; names include `smb-server, smbcreds, data-volume`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Exposes SMB publicly if the cloud provider provisions an external load balancer; demo image and hostPath storage are not hardened for production.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-lb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-networkdisk.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-networkdisk.yaml

- Purpose: example SMB server backed by a PVC named `pvc-networkdisk-smbshare`, demonstrating a share hosted on another storage provider.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `Service, PersistentVolumeClaim, Deployment`; notable images `dperson/samba`; names include `smb-server, pvc-networkdisk-smbshare, smbcreds, data-volume`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Builds an SMB service on top of another persistent disk, so failures/debugging span two storage layers; demo credentials and image are not production controls.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server-networkdisk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server.yaml

- Purpose: in-cluster demo SMB server using a ClusterIP Service and a Linux Deployment backed by hostPath storage.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `Service, Deployment`; notable images `andyzhangx/samba:win-fix`; names include `smb-server, smbcreds, data-volume`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: HostPath ties data to one node and uses demo credentials/image; scheduling movement can lose access to the expected data path.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/smb-provisioner/smb-server.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/statefulset-nonroot.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/statefulset-nonroot.yaml

- Purpose: Linux StatefulSet example proving SMB mounts can be consumed by a non-root pod security context using fsGroup/user/group 10001.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `StatefulSet`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.19.5`; names include `statefulset-smb-nonroot, persistent-storage`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Non-root access depends on mount uid/gid/permission options in the StorageClass; write loop grows remote data.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/statefulset-nonroot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/statefulset.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/statefulset.yaml

- Purpose: StatefulSet example that creates an SMB-backed claim from `volumeClaimTemplates` and mounts it into an nginx container.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `StatefulSet`; notable images `mcr.microsoft.com/oss/nginx/nginx:1.19.5`; names include `statefulset-smb, persistent-storage`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: StatefulSet claim retention and SMB share subdirectory cleanup must be understood before deletion; write loop grows data.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb-krb5.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb-krb5.yaml

- Purpose: Kerberos-enabled StorageClass example for dynamically provisioning SMB volumes with `sec=krb5`, sealed SMB traffic, and Kerberos credential secrets.
- Important APIs/types/functions: Kubernetes APIs `storage.k8s.io/v1`; kinds `StorageClass`; notable images `none`; names include `smb-krb5`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Kerberos options require node keytab/cache setup and correct secret material; `nosuid`/`noexec` are security hardening choices but may break workloads; wrong `cruid` or cache path causes mount failures.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb-krb5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb.yaml

- Purpose: standard StorageClass example for dynamic SMB provisioning using `smb.csi.k8s.io`, `smbcreds`, and SMB mount options.
- Important APIs/types/functions: Kubernetes APIs `storage.k8s.io/v1`; kinds `StorageClass`; notable images `none`; names include `smb`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Credentials are namespace-bound secrets; the source host comment warns that Windows CSI proxy may not resolve wildcard service DNS; missing `noserverino` can risk corruption per the manifest comment.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/storageclass-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/csi-proxy.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/windows/csi-proxy.yaml

- Purpose: Windows CSI proxy HostProcess DaemonSet example used by Windows SMB node plugins that still use CSI proxy APIs.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `DaemonSet`; notable images `ghcr.io/kubernetes-sigs/sig-windows/csi-proxy:v1.1.2`; names include `csi-proxy`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Runs as `NT AUTHORITY\SYSTEM` with host networking; CSI proxy version must match driver expectations and Windows support matrix.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/csi-proxy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/deployment.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/windows/deployment.yaml

- Purpose: Windows workload example consuming an SMB PVC with a Server Core container and PowerShell write loop.
- Important APIs/types/functions: Kubernetes APIs `v1, apps/v1`; kinds `PersistentVolumeClaim, Deployment`; notable images `mcr.microsoft.com/windows/servercore:ltsc2022`; names include `pvc-smb, busybox-smb, busybox`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Requires Windows node scheduling, compatible image/host version, and SMB subPath handling; shell loop is a smoke test, not production workload logic.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/statefulset.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/example/windows/statefulset.yaml

- Purpose: Windows workload example consuming an SMB PVC with a Server Core container and PowerShell write loop.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kinds `StatefulSet`; notable images `mcr.microsoft.com/windows/servercore:ltsc2022`; names include `busybox-smb, persistent-storage`.
- Control flow: after apply, Kubernetes creates the declared storage or workload objects; workloads mount the SMB-backed volume and most examples append timestamps to prove the share is writable.
- State and persistence behavior: workload state is stored on the SMB share or provisioned PVC/PV; demo SMB servers may store data in hostPath or a backing PVC. The manifests themselves keep only Kubernetes desired state.
- Dependencies/integration points: running SMB CSI driver, `smb` StorageClass or static PV, `smbcreds`/Kerberos secrets where referenced, OS-specific node selectors, and demo server service DNS names.
- Risks: Requires Windows node scheduling, compatible image/host version, and SMB subPath handling; shell loop is a smoke test, not production workload logic.
- Test signals: successful `kubectl apply`, PVC Bound status, pod readiness, and observing timestamp writes under the mounted path; cleanup should verify PVC/PV and remote share behavior.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/example/windows/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/install-driver.sh -->
# Research: sources/control-plane/csi-driver-smb/deploy/install-driver.sh

- Purpose: shell helper that installs SMB CSI driver manifests for a requested version from GitHub raw URLs or local deploy files, with a selectable Windows mode.
- Important APIs/types/functions: Bash with `set -euo pipefail`; accepts version `$1` defaulting to `master`, optional `$2` containing `local` and/or `hostprocess`; applies RBAC, CSIDriver, controller, Linux node, and either Windows CSI-proxy or HostProcess node manifest.
- Control flow: compute deploy repository path, append version for non-master, apply resources in dependency order with `kubectl apply`, then select Windows manifest based on `windowsMode`.
- State and persistence behavior: creates Kubernetes resources and may cause node pods to create host plugin directories/sockets. It does not create StorageClasses, Secrets, or SMB server state.
- Dependencies/integration points: kubectl, current cluster context, raw.githubusercontent.com access unless local mode is requested, deploy file naming conventions, and Windows mode compatibility with the cluster.
- Risks: applying remote `master` is mutable; local mode depends on cwd; the hostprocess mode requires supported Windows nodes; install applies both Linux and Windows node manifests even in single-OS clusters.
- Test signals: command exit code, resource rollout in kube-system, CSIDriver existence, and a smoke PVC mount.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/install-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/rbac-csi-smb.yaml

- Purpose: current RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccounts, ClusterRoles, and ClusterRoleBindings. The provisioner role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease and Secret reads; current manifests also include resizer permissions and a node Secret-read role.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/uninstall-driver.sh -->
# Research: sources/control-plane/csi-driver-smb/deploy/uninstall-driver.sh

- Purpose: shell helper that removes SMB CSI manifests for a requested version from either GitHub raw URLs or the local `./deploy` tree.
- Important APIs/types/functions: Bash with `set -euo pipefail`; accepts version as `$1`, optional local mode as `$2`, computes `repo`, appends version subdirectory for non-master, and runs `kubectl delete --ignore-not-found` for controller, node, Windows node, CSIDriver, and RBAC manifests.
- Control flow: resolve version/repo, print uninstall status, delete resources in dependency-tolerant order, and exit on unexpected command errors.
- State and persistence behavior: deletes Kubernetes API objects but does not clean remote SMB data, PV reclaim artifacts, Secrets, or host mount residue beyond what Kubernetes finalizers/DaemonSet teardown handle.
- Dependencies/integration points: requires kubectl context, network access for raw GitHub unless local mode is used, and file names matching the deploy tree for the requested version.
- Risks: hostprocess Windows manifest is not deleted explicitly; deleting manifests can leave PVs, mounts, or external SMB subdirectories depending on reclaim policy and workload state.
- Test signals: run against a test cluster and confirm target resources disappear with `kubectl get`; `--ignore-not-found` makes repeated runs idempotent for listed files.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/uninstall-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-driver.yaml

- Purpose: v0.1.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-node-windows.yaml

- Purpose: v0.1.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/k8s/csi/smb-csi:v0.1.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-node.yaml

- Purpose: v0.1.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.1.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.1.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-controller.yaml

- Purpose: v0.2.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include mcr.microsoft.com/oss/kubernetes-csi/csi-provisioner:v1.4.0, mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.2.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-driver.yaml

- Purpose: v0.2.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node-windows.yaml

- Purpose: v0.2.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/k8s/csi/smb-csi:v0.2.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node.yaml

- Purpose: v0.2.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.2.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.2.0/rbac-csi-smb-controller.yaml

- Purpose: v0.2.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.2.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-controller.yaml

- Purpose: v0.3.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include mcr.microsoft.com/oss/kubernetes-csi/csi-provisioner:v1.4.0, mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.3.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-driver.yaml

- Purpose: v0.3.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-node-windows.yaml

- Purpose: v0.3.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/k8s/csi/smb-csi:v0.3.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-node.yaml

- Purpose: v0.3.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.3.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.3.0/rbac-csi-smb-controller.yaml

- Purpose: v0.3.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-controller.yaml

- Purpose: v0.4.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include mcr.microsoft.com/oss/kubernetes-csi/csi-provisioner:v1.4.0, mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.4.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-driver.yaml

- Purpose: v0.4.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-node-windows.yaml

- Purpose: v0.4.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/k8s/csi/smb-csi:v0.4.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-node.yaml

- Purpose: v0.4.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.4.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.4.0/rbac-csi-smb-controller.yaml

- Purpose: v0.4.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.4.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-controller.yaml

- Purpose: v0.5.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v2.0.4, registry.k8s.io/sig-storage/livenessprobe:v2.1.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.5.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-driver.yaml

- Purpose: v0.5.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-node-windows.yaml

- Purpose: v0.5.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v1.2.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/k8s/csi/smb-csi:v0.5.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-node.yaml

- Purpose: v0.5.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.1.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.0.1, mcr.microsoft.com/k8s/csi/smb-csi:v0.5.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.5.0/rbac-csi-smb-controller.yaml

- Purpose: v0.5.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.5.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-controller.yaml

- Purpose: v0.6.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v2.0.4, registry.k8s.io/sig-storage/livenessprobe:v2.1.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.6.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-driver.yaml

- Purpose: v0.6.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-node-windows.yaml

- Purpose: v0.6.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.0.1-alpha.1-windows-1809-amd64, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.0.1, mcr.microsoft.com/k8s/csi/smb-csi:v0.6.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-node.yaml

- Purpose: v0.6.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.1.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.0.1, mcr.microsoft.com/k8s/csi/smb-csi:v0.6.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.6.0/rbac-csi-smb-controller.yaml

- Purpose: v0.6.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.6.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-controller.yaml

- Purpose: v1.0.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v2.1.0, registry.k8s.io/sig-storage/livenessprobe:v2.3.0, mcr.microsoft.com/k8s/csi/smb-csi:v1.0.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-driver.yaml

- Purpose: v1.0.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1beta1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-node-windows.yaml

- Purpose: v1.0.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.3.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v1.0.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-node.yaml

- Purpose: v1.0.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.3.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v1.0.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.0.0/rbac-csi-smb-controller.yaml

- Purpose: v1.0.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.0.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-controller.yaml

- Purpose: v1.1.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v2.1.0, registry.k8s.io/sig-storage/livenessprobe:v2.3.0, mcr.microsoft.com/k8s/csi/smb-csi:v1.1.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-driver.yaml

- Purpose: v1.1.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-node-windows.yaml

- Purpose: v1.1.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.3.0, mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v1.1.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-node.yaml

- Purpose: v1.1.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.3.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.2.0, mcr.microsoft.com/k8s/csi/smb-csi:v1.1.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/rbac-csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.1.0/rbac-csi-smb-controller.yaml

- Purpose: v1.1.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.1.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-controller.yaml

- Purpose: v1.10.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v3.3.0, registry.k8s.io/sig-storage/livenessprobe:v2.8.0, registry.k8s.io/sig-storage/smbplugin:v1.10.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-driver.yaml

- Purpose: v1.10.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-node-windows.yaml

- Purpose: v1.10.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.8.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.6.2, registry.k8s.io/sig-storage/smbplugin:v1.10.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-node.yaml

- Purpose: v1.10.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.8.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.6.2, registry.k8s.io/sig-storage/smbplugin:v1.10.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.10.0/rbac-csi-smb.yaml

- Purpose: v1.10.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.10.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-controller.yaml

- Purpose: v1.11.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v3.5.0, registry.k8s.io/sig-storage/livenessprobe:v2.10.0, registry.k8s.io/sig-storage/smbplugin:v1.11.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-driver.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-driver.yaml

- Purpose: v1.11.0 static `CSIDriver` manifest for `smb.csi.k8s.io`.
- Important APIs/types/functions: emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, advertising that Kubernetes attach/detach is unnecessary for SMB network filesystem volumes.
- Control flow: applied once at install time so kubelet and storage controllers understand driver-level behavior while controller and node pods perform actual CSI RPC handling.
- State and persistence behavior: only driver metadata is persisted in the Kubernetes API; no volume data, credentials, or mount state are stored here.
- Dependencies/integration points: StorageClasses, PVs, inline CSI volumes, controller/node manifests, and the driver name passed to `smbplugin` must all match this name.
- Risks: older `storage.k8s.io/v1beta1` manifests are unsuitable for newer clusters where beta APIs were removed; name drift breaks provisioning and mounting.
- Test signals: `kubectl get csidriver smb.csi.k8s.io` and successful PVC lifecycle tests.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-node-windows.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-node-windows.yaml

- Purpose: v1.11.0 Windows node DaemonSet for SMB CSI using CSI proxy. It installs liveness, node-driver-registrar, and SMB plugin containers on Windows nodes.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.10.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.8.0, registry.k8s.io/sig-storage/smbplugin:v1.11.0. It passes `--endpoint`, `--nodeid`, registrar `--kubelet-registration-path`, metrics/health flags, and in later versions `--remove-smb-mapping-during-unmount=true`.
- Control flow: the liveness probe monitors the Windows CSI socket, registrar publishes the driver socket to kubelet, and the SMB plugin calls CSI proxy named pipes for filesystem and SMB operations.
- State and persistence behavior: uses Windows hostPaths for kubelet, plugin, and registration directories plus named-pipe hostPaths. Durable data remains on the SMB server; local state is plugin sockets, registration files, and mount/mapping state.
- Dependencies/integration points: Windows nodes, CSI proxy versions, kubelet plugin registry, ServiceAccount/RBAC, driver name `smb.csi.k8s.io`, and compatible Windows container images.
- Risks: CSI proxy version/path mismatch, Windows path escaping errors, stale SMB mappings, image OS-version compatibility, and privileged host integration through pipes and kubelet directories.
- Test signals: DaemonSet rollout, registrar liveness/registration, Windows pod mounting a PVC, and unmount cleanup checks.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-node.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-node.yaml

- Purpose: v1.11.0 Linux node DaemonSet for SMB CSI. It deploys liveness, node-driver-registrar, and the SMB node plugin on Linux workers.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; images include registry.k8s.io/sig-storage/livenessprobe:v2.10.0, registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.8.0, registry.k8s.io/sig-storage/smbplugin:v1.11.0. It binds `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `/var/lib/kubelet`, and `/var/lib/kubelet/plugins_registry`, then passes `--endpoint`, `--nodeid`, and registration flags.
- Control flow: one pod runs per Linux node. Registrar creates kubelet plugin registration; liveness checks the CSI socket; the privileged SMB plugin handles NodeStage/NodePublish and other node-side CSI calls through Linux mount operations.
- State and persistence behavior: hostPath volumes hold CSI sockets, registration files, and mountpoints with bidirectional propagation. Actual volume data is on the remote SMB share.
- Dependencies/integration points: Linux kubelet path, mount propagation support, privileged container permissions, node ServiceAccount/RBAC for secrets in newer manifests, and controller-side provisioning.
- Risks: hostPath privilege, wrong kubelet path, missing mount propagation, sidecar version skew, and stale plugin sockets during upgrades. Historical versions also use older liveness flags and image registries.
- Test signals: DaemonSet ready count, kubelet plugin registration, liveness health, and a Linux workload writing to an SMB PVC.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/rbac-csi-smb.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.11.0/rbac-csi-smb.yaml

- Purpose: v1.11.0 RBAC manifest for SMB CSI controller and node identities.
- Important APIs/types/functions: creates ServiceAccount, ClusterRole, and ClusterRoleBinding for the external provisioner. The role covers PV/PVC/StorageClass/Event/CSINode/Node/Lease access and Secret reads as required by the provisioner.
- Control flow: install scripts apply RBAC before controller and node workloads. CSI sidecars authenticate with these service accounts while reconciling volumes, leader-election Leases, Events, and secret-backed credentials.
- State and persistence behavior: persists Kubernetes identity and authorization rules only; it controls access to storage API objects and credential Secrets but stores no driver runtime data.
- Dependencies/integration points: consumed by `csi-smb-controller`, Linux/Windows node DaemonSets, external-provisioner, resizer where present, and StorageClass/PV secret references.
- Risks: broad Secret read and cluster-wide storage permissions are sensitive; missing resizer or node-secret rules cause runtime failures; historical controller-only RBAC does not cover newer node ServiceAccount patterns.
- Test signals: `kubectl auth can-i` for provisioner verbs, provisioning/resize attempts, and checking sidecar logs for RBAC denial events.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/rbac-csi-smb.yaml -->
