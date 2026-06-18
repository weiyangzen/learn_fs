# subset-b-000367 Research

Grouped research for the requested SMB CSI Driver Helm chart files. Each section is source-tree aligned and can be split into the mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.18.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and `spec.volumeLifecycleModes`. It always advertises `Persistent` volumes and conditionally adds `Ephemeral` when `.Values.feature.enableInlineVolume` is true.

## Control Flow
Rendering is unconditional. The inline volume mode is the only feature branch in this template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver`, on node-driver-registrar publishing the same driver name, and on inline-volume RBAC matching the advertised `Ephemeral` lifecycle mode when enabled.

## Risks And Test Signals
Risk centers on name drift and enabling ephemeral mode without matching node secret access. Validate with `helm template`, `kubectl get csidriver`, rendered `volumeLifecycleModes`, and a smoke PVC or inline CSI volume that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

## Purpose
This template renders the Windows HostProcess SMB CSI node `DaemonSet` for chart `v1.18.0`. It is selected when `.Values.windows.enabled` and `.Values.windows.useHostProcessContainers` are both true, replacing the legacy CSI proxy pipe-mounted node pod with host-process containers.

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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.18.0`. It is active when `.Values.windows.enabled` and `not .Values.windows.useHostProcessContainers`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file. It uses `.Values.serviceAccount.node` in modern charts.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.18.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts. It conditionally mounts a Kerberos cache hostPath when `.Values.linux.krb5CacheDirectory` is non-empty and passes `--krb5-prefix` to the driver.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/rbac-csi-smb.yaml

## Purpose
This modern `v1.18.0` RBAC template provisions authorization for both the SMB CSI controller and node paths. It covers provisioning, expansion, leader election, controller secret lookup, and optional node secret lookup for inline ephemeral volumes.

## Important APIs, Types, And Functions
The template can render two `ServiceAccount` objects (`.Values.serviceAccount.controller` and `.Values.serviceAccount.node`), an external provisioner `ClusterRole`/`ClusterRoleBinding`, an external resizer `ClusterRole`/`ClusterRoleBinding`, and a conditional node secret role/binding when `.Values.feature.enableInlineVolume` is true. Helm gates are `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Values.feature.enableInlineVolume`.

## Control Flow
Service accounts are emitted first when enabled. RBAC creation then binds the controller service account to provisioning and resizing permissions. The inline-volume block adds `secrets get` for the node service account only when ephemeral volume support is advertised by the CSIDriver.

## State And Persistence Behavior
These cluster-scoped roles and bindings are persistent security state. They do not hold SMB data, but incorrect role updates can immediately break provisioning, expansion, or inline volume mount flows.

## Dependencies And Integration Points
The controller Deployment uses the controller account; Linux and Windows node DaemonSets use the node account. Provisioner/resizer sidecars need PV/PVC/Event/Lease permissions. Node secret access aligns with `podInfoOnMount` and inline CSI volumes that reference secrets.

## Risks And Test Signals
The main risk is excessive or missing Secret access. A disabled inline-volume feature should omit node secret RBAC; an enabled feature should render it. Test with `helm template --set feature.enableInlineVolume=false/true`, `kubectl auth can-i`, PVC provisioning, expansion, and inline-volume mount checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/values.yaml

## Purpose
This `v1.18.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, csiResizer, livenessProbe, nodeDriverRegistrar, csiproxy. Feature gates present here are: enableGetVolumeStats, enableInlineVolume. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths, Kerberos cache settings.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.18.0` and matching CSI sidecars. This version configures default-enabled Windows support with HostProcess containers. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.19.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `1.19.0` with app version `1.19.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.19.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-proxy-windows.yaml

## Purpose
This template renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart `v1.19.0` when `.Values.windows.csiproxy.enabled` is true. It can install the Windows CSI proxy alongside the SMB CSI driver for clusters that do not manage CSI proxy separately.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. The pod uses `windowsOptions.hostProcess: true`, `runAsUserName` from `.Values.windows.csiproxy.username`, host networking, Windows node selectors from `.Values.windows.csiproxy.nodeSelector`, and the `csi-proxy` image from `.Values.image.csiproxy`. It follows the same rolling update `maxUnavailable` value as node workloads.

## Control Flow
Rendering is entirely conditional on `.Values.windows.csiproxy.enabled`. Helm injects labels, tolerations, affinity, priority class, pull secrets, image repository composition, and pull policy. The template does not configure explicit command arguments, so the image entrypoint is responsible for exposing named pipes.

## State And Persistence Behavior
The DaemonSet does not declare persistent volumes in this template. Its practical state is host-level Windows CSI proxy processes and named pipes, which are consumed by the legacy Windows SMB node DaemonSet.

## Dependencies And Integration Points
It integrates with `csi-smb-node-windows.yaml` through the expected `\.\pipe\csi-proxy-filesystem-*` and `\.\pipe\csi-proxy-smb-*` endpoints. It depends on Windows HostProcess support and the configured service account/security policy allowing host-process pods.

## Risks And Test Signals
Risks include enabling it on clusters that already install CSI proxy, using an incompatible proxy image tag, or omitting required pipe exposure. Test with `helm template --set windows.csiproxy.enabled=true`, DaemonSet rollout on Windows nodes, and successful Windows PVC mount through the legacy node path.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.19.0`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, csi-resizer, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses configurable `.Values.controller.dnsPolicy`. It uses `Recreate` rollout strategy to avoid overlapping controller pods sharing mount state. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks. Newer sidecars use localhost HTTP liveness endpoints and drop Linux capabilities where possible.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.19.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and `spec.volumeLifecycleModes`. It always advertises `Persistent` volumes and conditionally adds `Ephemeral` when `.Values.feature.enableInlineVolume` is true.

## Control Flow
Rendering is unconditional. The inline volume mode is the only feature branch in this template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver`, on node-driver-registrar publishing the same driver name, and on inline-volume RBAC matching the advertised `Ephemeral` lifecycle mode when enabled.

## Risks And Test Signals
Risk centers on name drift and enabling ephemeral mode without matching node secret access. Validate with `helm template`, `kubectl get csidriver`, rendered `volumeLifecycleModes`, and a smoke PVC or inline CSI volume that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.19.0`. It is active when `.Values.windows.enabled` and `not .Values.windows.useHostProcessContainers`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file. It uses `.Values.serviceAccount.node` in modern charts.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.19.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts. It conditionally mounts a Kerberos cache hostPath when `.Values.linux.krb5CacheDirectory` is non-empty and passes `--krb5-prefix` to the driver.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/rbac-csi-smb.yaml

## Purpose
This modern `v1.19.0` RBAC template provisions authorization for both the SMB CSI controller and node paths. It covers provisioning, expansion, leader election, controller secret lookup, and optional node secret lookup for inline ephemeral volumes.

## Important APIs, Types, And Functions
The template can render two `ServiceAccount` objects (`.Values.serviceAccount.controller` and `.Values.serviceAccount.node`), an external provisioner `ClusterRole`/`ClusterRoleBinding`, an external resizer `ClusterRole`/`ClusterRoleBinding`, and a conditional node secret role/binding when `.Values.feature.enableInlineVolume` is true. Helm gates are `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Values.feature.enableInlineVolume`.

## Control Flow
Service accounts are emitted first when enabled. RBAC creation then binds the controller service account to provisioning and resizing permissions. The inline-volume block adds `secrets get` for the node service account only when ephemeral volume support is advertised by the CSIDriver.

## State And Persistence Behavior
These cluster-scoped roles and bindings are persistent security state. They do not hold SMB data, but incorrect role updates can immediately break provisioning, expansion, or inline volume mount flows.

## Dependencies And Integration Points
The controller Deployment uses the controller account; Linux and Windows node DaemonSets use the node account. Provisioner/resizer sidecars need PV/PVC/Event/Lease permissions. Node secret access aligns with `podInfoOnMount` and inline CSI volumes that reference secrets.

## Risks And Test Signals
The main risk is excessive or missing Secret access. A disabled inline-volume feature should omit node secret RBAC; an enabled feature should render it. Test with `helm template --set feature.enableInlineVolume=false/true`, `kubectl auth can-i`, PVC provisioning, expansion, and inline-volume mount checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/storageclass.yaml

## Purpose
This template renders zero or more SMB `StorageClass` objects for chart `v1.19.0` from `.Values.storageClasses`. It lets chart users ship provisioner-ready classes with SMB share parameters instead of applying separate manifests.

## Important APIs, Types, And Functions
The Kubernetes API is `storage.k8s.io/v1/StorageClass`. Helm loops over `.Values.storageClasses`, emits `metadata.name`, common SMB labels, optional annotations, optional `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and optional `mountOptions`. The provisioner is always `$.Values.driver.name`.

## Control Flow
The whole file is skipped when `.Values.storageClasses` is unset or empty. Within each item, `reclaimPolicy` defaults to `Delete`, `volumeBindingMode` defaults to `Immediate`, and `allowVolumeExpansion` defaults to true unless the key is explicitly present.

## State And Persistence Behavior
Rendered StorageClasses are persistent cluster objects. They do not hold SMB credentials directly unless users place secret references in `parameters`; PVCs created later bind to these classes and inherit mount options such as `noserverino`.

## Dependencies And Integration Points
The class must match the `CSIDriver`/controller provisioner name and the controller RBAC must allow StorageClass reads plus secret access for provisioner and node-stage secrets. Parameters integrate with external SMB shares and Kubernetes Secrets.

## Risks And Test Signals
Risks include exposing incorrect secret namespaces, omitting required SMB mount options, or accidentally making the class default through annotations. Test by templating example `storageClasses`, creating PVCs against each class, checking PV parameters, testing expansion, and validating mount options on Linux/Windows nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/values.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.19.1`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `1.19.1` with app version `1.19.1`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.19.1` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-proxy-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-proxy-windows.yaml

## Purpose
This template renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart `v1.19.1` when `.Values.windows.csiproxy.enabled` is true. It can install the Windows CSI proxy alongside the SMB CSI driver for clusters that do not manage CSI proxy separately.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. The pod uses `windowsOptions.hostProcess: true`, `runAsUserName` from `.Values.windows.csiproxy.username`, host networking, Windows node selectors from `.Values.windows.csiproxy.nodeSelector`, and the `csi-proxy` image from `.Values.image.csiproxy`. It follows the same rolling update `maxUnavailable` value as node workloads.

## Control Flow
Rendering is entirely conditional on `.Values.windows.csiproxy.enabled`. Helm injects labels, tolerations, affinity, priority class, pull secrets, image repository composition, and pull policy. The template does not configure explicit command arguments, so the image entrypoint is responsible for exposing named pipes.

## State And Persistence Behavior
The DaemonSet does not declare persistent volumes in this template. Its practical state is host-level Windows CSI proxy processes and named pipes, which are consumed by the legacy Windows SMB node DaemonSet.

## Dependencies And Integration Points
It integrates with `csi-smb-node-windows.yaml` through the expected `\.\pipe\csi-proxy-filesystem-*` and `\.\pipe\csi-proxy-smb-*` endpoints. It depends on Windows HostProcess support and the configured service account/security policy allowing host-process pods.

## Risks And Test Signals
Risks include enabling it on clusters that already install CSI proxy, using an incompatible proxy image tag, or omitting required pipe exposure. Test with `helm template --set windows.csiproxy.enabled=true`, DaemonSet rollout on Windows nodes, and successful Windows PVC mount through the legacy node path.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.19.1`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, csi-resizer, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses configurable `.Values.controller.dnsPolicy`. It uses `Recreate` rollout strategy to avoid overlapping controller pods sharing mount state. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks. Newer sidecars use localhost HTTP liveness endpoints and drop Linux capabilities where possible.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.19.1`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and `spec.volumeLifecycleModes`. It always advertises `Persistent` volumes and conditionally adds `Ephemeral` when `.Values.feature.enableInlineVolume` is true.

## Control Flow
Rendering is unconditional. The inline volume mode is the only feature branch in this template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver`, on node-driver-registrar publishing the same driver name, and on inline-volume RBAC matching the advertised `Ephemeral` lifecycle mode when enabled.

## Risks And Test Signals
Risk centers on name drift and enabling ephemeral mode without matching node secret access. Validate with `helm template`, `kubectl get csidriver`, rendered `volumeLifecycleModes`, and a smoke PVC or inline CSI volume that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

## Purpose
This template renders the Windows HostProcess SMB CSI node `DaemonSet` for chart `v1.19.1`. It is selected when `.Values.windows.enabled` and `.Values.windows.useHostProcessContainers` are both true, replacing the legacy CSI proxy pipe-mounted node pod with host-process containers.

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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.19.1`. It is active when `.Values.windows.enabled` and `not .Values.windows.useHostProcessContainers`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file. It uses `.Values.serviceAccount.node` in modern charts.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.19.1` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts. It conditionally mounts a Kerberos cache hostPath when `.Values.linux.krb5CacheDirectory` is non-empty and passes `--krb5-prefix` to the driver.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/rbac-csi-smb.yaml

## Purpose
This modern `v1.19.1` RBAC template provisions authorization for both the SMB CSI controller and node paths. It covers provisioning, expansion, leader election, controller secret lookup, and optional node secret lookup for inline ephemeral volumes.

## Important APIs, Types, And Functions
The template can render two `ServiceAccount` objects (`.Values.serviceAccount.controller` and `.Values.serviceAccount.node`), an external provisioner `ClusterRole`/`ClusterRoleBinding`, an external resizer `ClusterRole`/`ClusterRoleBinding`, and a conditional node secret role/binding when `.Values.feature.enableInlineVolume` is true. Helm gates are `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Values.feature.enableInlineVolume`.

## Control Flow
Service accounts are emitted first when enabled. RBAC creation then binds the controller service account to provisioning and resizing permissions. The inline-volume block adds `secrets get` for the node service account only when ephemeral volume support is advertised by the CSIDriver.

## State And Persistence Behavior
These cluster-scoped roles and bindings are persistent security state. They do not hold SMB data, but incorrect role updates can immediately break provisioning, expansion, or inline volume mount flows.

## Dependencies And Integration Points
The controller Deployment uses the controller account; Linux and Windows node DaemonSets use the node account. Provisioner/resizer sidecars need PV/PVC/Event/Lease permissions. Node secret access aligns with `podInfoOnMount` and inline CSI volumes that reference secrets.

## Risks And Test Signals
The main risk is excessive or missing Secret access. A disabled inline-volume feature should omit node secret RBAC; an enabled feature should render it. Test with `helm template --set feature.enableInlineVolume=false/true`, `kubectl auth can-i`, PVC provisioning, expansion, and inline-volume mount checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/storageclass.yaml

## Purpose
This template renders zero or more SMB `StorageClass` objects for chart `v1.19.1` from `.Values.storageClasses`. It lets chart users ship provisioner-ready classes with SMB share parameters instead of applying separate manifests.

## Important APIs, Types, And Functions
The Kubernetes API is `storage.k8s.io/v1/StorageClass`. Helm loops over `.Values.storageClasses`, emits `metadata.name`, common SMB labels, optional annotations, optional `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and optional `mountOptions`. The provisioner is always `$.Values.driver.name`.

## Control Flow
The whole file is skipped when `.Values.storageClasses` is unset or empty. Within each item, `reclaimPolicy` defaults to `Delete`, `volumeBindingMode` defaults to `Immediate`, and `allowVolumeExpansion` defaults to true unless the key is explicitly present.

## State And Persistence Behavior
Rendered StorageClasses are persistent cluster objects. They do not hold SMB credentials directly unless users place secret references in `parameters`; PVCs created later bind to these classes and inherit mount options such as `noserverino`.

## Dependencies And Integration Points
The class must match the `CSIDriver`/controller provisioner name and the controller RBAC must allow StorageClass reads plus secret access for provisioner and node-stage secrets. Parameters integrate with external SMB shares and Kubernetes Secrets.

## Risks And Test Signals
Risks include exposing incorrect secret namespaces, omitting required SMB mount options, or accidentally making the class default through annotations. Test by templating example `storageClasses`, creating PVCs against each class, checking PV parameters, testing expansion, and validating mount options on Linux/Windows nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/values.yaml

## Purpose
This `v1.19.1` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context and commented `storageClasses` examples.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, csiResizer, livenessProbe, nodeDriverRegistrar, csiproxy. Feature gates present here are: enableGetVolumeStats, enableInlineVolume. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths, Kerberos cache settings.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.19.1` and matching CSI sidecars. This version configures default-enabled Windows support with HostProcess containers. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.2.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `v1.2.0` with app version `v1.2.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.2.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.2.0`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses hard-coded `ClusterFirstWithHostNet` DNS policy. It uses the default Deployment strategy. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.2.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false` and `spec.podInfoOnMount: true`. Unlike later chart versions, it does not render `spec.volumeLifecycleModes`, does not advertise inline `Ephemeral` volumes, and does not expose custom CSIDriver labels.

## Control Flow
Rendering is unconditional and has no feature-gated branches in this older template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver` and on node-driver-registrar publishing the same driver name. Inline ephemeral volume support is not declared by this template version.

## Risks And Test Signals
Risk centers on driver-name drift and assumptions that this older chart supports inline ephemeral CSI volumes. Validate with `helm template`, `kubectl get csidriver`, and a smoke PVC that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.2.0`. It is active when `.Values.windows.enabled`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.2.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.node.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled. One template risk in these early versions is that `.Values.node.affinity` appears under the `nodeSelector` block rather than as a sibling `affinity` field.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

## Purpose
This `v1.2.0` RBAC template creates the controller service account and the external-provisioner cluster permissions used by the SMB CSI controller Deployment. It is named `rbac-csi-smb-controller.yaml` in these earlier chart versions because node workloads do not receive a separate chart-managed service account here.

## Important APIs, Types, And Functions
The rendered APIs are `v1/ServiceAccount`, `rbac.authorization.k8s.io/v1/ClusterRole`, and `ClusterRoleBinding`. `.Values.serviceAccount.create` gates service account creation, while `.Values.rbac.create` gates the role and binding. The role can create/delete PVs, update PVCs, read StorageClasses, CSINodes, Nodes, Events, Leases, and Secrets; leader election uses `coordination.k8s.io/leases`.

## Control Flow
Helm emits the service account only when requested, then independently emits RBAC when requested. The binding references `.Values.serviceAccount.controller` in `.Release.Namespace`, so setting `serviceAccount.create: false` still expects a preexisting account with the same name.

## State And Persistence Behavior
The resources are cluster-persistent authorization state. They do not store volume data, but they govern whether dynamic provisioning, event recording, secret lookup, and leader election can proceed.

## Dependencies And Integration Points
The controller Deployment uses this account. The provisioner sidecar depends on the PV/PVC/StorageClass/secret permissions; lease verbs must match the sidecar's `--leader-election` settings.

## Risks And Test Signals
The role is broad enough to read Kubernetes Secrets, which is necessary for SMB credentials but security-sensitive. Test with `helm template` for both create flags, `kubectl auth can-i` as the controller account, and dynamic provisioning of a PVC backed by an SMB secret.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/values.yaml

## Purpose
This `v1.2.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, livenessProbe, nodeDriverRegistrar. Feature gates present here are: none in this version. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.2.0` and matching CSI sidecars. This version configures optional legacy Windows support. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.20.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `1.20.0` with app version `1.20.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.20.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-proxy-windows.yaml

## Purpose
This template renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart `v1.20.0` when `.Values.windows.csiproxy.enabled` is true. It can install the Windows CSI proxy alongside the SMB CSI driver for clusters that do not manage CSI proxy separately.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. The pod uses `windowsOptions.hostProcess: true`, `runAsUserName` from `.Values.windows.csiproxy.username`, host networking, Windows node selectors from `.Values.windows.csiproxy.nodeSelector`, and the `csi-proxy` image from `.Values.image.csiproxy`. It follows the same rolling update `maxUnavailable` value as node workloads.

## Control Flow
Rendering is entirely conditional on `.Values.windows.csiproxy.enabled`. Helm injects labels, tolerations, affinity, priority class, pull secrets, image repository composition, and pull policy. The template does not configure explicit command arguments, so the image entrypoint is responsible for exposing named pipes.

## State And Persistence Behavior
The DaemonSet does not declare persistent volumes in this template. Its practical state is host-level Windows CSI proxy processes and named pipes, which are consumed by the legacy Windows SMB node DaemonSet.

## Dependencies And Integration Points
It integrates with `csi-smb-node-windows.yaml` through the expected `\.\pipe\csi-proxy-filesystem-*` and `\.\pipe\csi-proxy-smb-*` endpoints. It depends on Windows HostProcess support and the configured service account/security policy allowing host-process pods.

## Risks And Test Signals
Risks include enabling it on clusters that already install CSI proxy, using an incompatible proxy image tag, or omitting required pipe exposure. Test with `helm template --set windows.csiproxy.enabled=true`, DaemonSet rollout on Windows nodes, and successful Windows PVC mount through the legacy node path.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.20.0`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, csi-resizer, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses configurable `.Values.controller.dnsPolicy`. It uses `Recreate` rollout strategy to avoid overlapping controller pods sharing mount state. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks. Newer sidecars use localhost HTTP liveness endpoints and drop Linux capabilities where possible.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.20.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and `spec.volumeLifecycleModes`. It always advertises `Persistent` volumes and conditionally adds `Ephemeral` when `.Values.feature.enableInlineVolume` is true. This version supports optional `.Values.driver.labels` metadata injection.

## Control Flow
Rendering is unconditional. The inline volume mode is the main feature branch, and versions with `.Values.driver.labels` also branch around optional metadata labels. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver`, on node-driver-registrar publishing the same driver name, and on inline-volume RBAC matching the advertised `Ephemeral` lifecycle mode when enabled.

## Risks And Test Signals
Risk centers on name drift and enabling ephemeral mode without matching node secret access. Validate with `helm template`, `kubectl get csidriver`, rendered `volumeLifecycleModes`, and a smoke PVC or inline CSI volume that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

## Purpose
This template renders the Windows HostProcess SMB CSI node `DaemonSet` for chart `v1.20.0`. It is selected when `.Values.windows.enabled` and `.Values.windows.useHostProcessContainers` are both true, replacing the legacy CSI proxy pipe-mounted node pod with host-process containers.

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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.20.0`. It is active when `.Values.windows.enabled` and `not .Values.windows.useHostProcessContainers`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file. It uses `.Values.serviceAccount.node` in modern charts.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.20.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts. It conditionally mounts a Kerberos cache hostPath when `.Values.linux.krb5CacheDirectory` is non-empty and passes `--krb5-prefix` to the driver.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/rbac-csi-smb.yaml

## Purpose
This modern `v1.20.0` RBAC template provisions authorization for both the SMB CSI controller and node paths. It covers provisioning, expansion, leader election, controller secret lookup, and optional node secret lookup for inline ephemeral volumes.

## Important APIs, Types, And Functions
The template can render two `ServiceAccount` objects (`.Values.serviceAccount.controller` and `.Values.serviceAccount.node`), an external provisioner `ClusterRole`/`ClusterRoleBinding`, an external resizer `ClusterRole`/`ClusterRoleBinding`, and a conditional node secret role/binding when `.Values.feature.enableInlineVolume` is true. Helm gates are `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Values.feature.enableInlineVolume`.

## Control Flow
Service accounts are emitted first when enabled. RBAC creation then binds the controller service account to provisioning and resizing permissions. The inline-volume block adds `secrets get` for the node service account only when ephemeral volume support is advertised by the CSIDriver.

## State And Persistence Behavior
These cluster-scoped roles and bindings are persistent security state. They do not hold SMB data, but incorrect role updates can immediately break provisioning, expansion, or inline volume mount flows.

## Dependencies And Integration Points
The controller Deployment uses the controller account; Linux and Windows node DaemonSets use the node account. Provisioner/resizer sidecars need PV/PVC/Event/Lease permissions. Node secret access aligns with `podInfoOnMount` and inline CSI volumes that reference secrets.

## Risks And Test Signals
The main risk is excessive or missing Secret access. A disabled inline-volume feature should omit node secret RBAC; an enabled feature should render it. Test with `helm template --set feature.enableInlineVolume=false/true`, `kubectl auth can-i`, PVC provisioning, expansion, and inline-volume mount checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/storageclass.yaml

## Purpose
This template renders zero or more SMB `StorageClass` objects for chart `v1.20.0` from `.Values.storageClasses`. It lets chart users ship provisioner-ready classes with SMB share parameters instead of applying separate manifests.

## Important APIs, Types, And Functions
The Kubernetes API is `storage.k8s.io/v1/StorageClass`. Helm loops over `.Values.storageClasses`, emits `metadata.name`, common SMB labels, optional annotations, optional `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and optional `mountOptions`. The provisioner is always `$.Values.driver.name`.

## Control Flow
The whole file is skipped when `.Values.storageClasses` is unset or empty. Within each item, `reclaimPolicy` defaults to `Delete`, `volumeBindingMode` defaults to `Immediate`, and `allowVolumeExpansion` defaults to true unless the key is explicitly present.

## State And Persistence Behavior
Rendered StorageClasses are persistent cluster objects. They do not hold SMB credentials directly unless users place secret references in `parameters`; PVCs created later bind to these classes and inherit mount options such as `noserverino`.

## Dependencies And Integration Points
The class must match the `CSIDriver`/controller provisioner name and the controller RBAC must allow StorageClass reads plus secret access for provisioner and node-stage secrets. Parameters integrate with external SMB shares and Kubernetes Secrets.

## Risks And Test Signals
Risks include exposing incorrect secret namespaces, omitting required SMB mount options, or accidentally making the class default through annotations. Test by templating example `storageClasses`, creating PVCs against each class, checking PV parameters, testing expansion, and validating mount options on Linux/Windows nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/values.yaml

## Purpose
This `v1.20.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context and commented `storageClasses` examples.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, csiResizer, livenessProbe, nodeDriverRegistrar, csiproxy. Feature gates present here are: enableGetVolumeStats, enableInlineVolume. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths, Kerberos cache settings.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.20.0` and matching CSI sidecars. This version configures default-enabled Windows support with HostProcess containers. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.20.1`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `1.20.1` with app version `1.20.1`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.20.1` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-proxy-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-proxy-windows.yaml

## Purpose
This template renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart `v1.20.1` when `.Values.windows.csiproxy.enabled` is true. It can install the Windows CSI proxy alongside the SMB CSI driver for clusters that do not manage CSI proxy separately.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. The pod uses `windowsOptions.hostProcess: true`, `runAsUserName` from `.Values.windows.csiproxy.username`, host networking, Windows node selectors from `.Values.windows.csiproxy.nodeSelector`, and the `csi-proxy` image from `.Values.image.csiproxy`. It follows the same rolling update `maxUnavailable` value as node workloads.

## Control Flow
Rendering is entirely conditional on `.Values.windows.csiproxy.enabled`. Helm injects labels, tolerations, affinity, priority class, pull secrets, image repository composition, and pull policy. The template does not configure explicit command arguments, so the image entrypoint is responsible for exposing named pipes.

## State And Persistence Behavior
The DaemonSet does not declare persistent volumes in this template. Its practical state is host-level Windows CSI proxy processes and named pipes, which are consumed by the legacy Windows SMB node DaemonSet.

## Dependencies And Integration Points
It integrates with `csi-smb-node-windows.yaml` through the expected `\.\pipe\csi-proxy-filesystem-*` and `\.\pipe\csi-proxy-smb-*` endpoints. It depends on Windows HostProcess support and the configured service account/security policy allowing host-process pods.

## Risks And Test Signals
Risks include enabling it on clusters that already install CSI proxy, using an incompatible proxy image tag, or omitting required pipe exposure. Test with `helm template --set windows.csiproxy.enabled=true`, DaemonSet rollout on Windows nodes, and successful Windows PVC mount through the legacy node path.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.20.1`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, csi-resizer, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses configurable `.Values.controller.dnsPolicy`. It uses `Recreate` rollout strategy to avoid overlapping controller pods sharing mount state. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks. Newer sidecars use localhost HTTP liveness endpoints and drop Linux capabilities where possible.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.20.1`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and `spec.volumeLifecycleModes`. It always advertises `Persistent` volumes and conditionally adds `Ephemeral` when `.Values.feature.enableInlineVolume` is true. This version supports optional `.Values.driver.labels` metadata injection.

## Control Flow
Rendering is unconditional. The inline volume mode is the main feature branch, and versions with `.Values.driver.labels` also branch around optional metadata labels. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver`, on node-driver-registrar publishing the same driver name, and on inline-volume RBAC matching the advertised `Ephemeral` lifecycle mode when enabled.

## Risks And Test Signals
Risk centers on name drift and enabling ephemeral mode without matching node secret access. Validate with `helm template`, `kubectl get csidriver`, rendered `volumeLifecycleModes`, and a smoke PVC or inline CSI volume that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

## Purpose
This template renders the Windows HostProcess SMB CSI node `DaemonSet` for chart `v1.20.1`. It is selected when `.Values.windows.enabled` and `.Values.windows.useHostProcessContainers` are both true, replacing the legacy CSI proxy pipe-mounted node pod with host-process containers.

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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.20.1`. It is active when `.Values.windows.enabled` and `not .Values.windows.useHostProcessContainers`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file. It uses `.Values.serviceAccount.node` in modern charts.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.20.1` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts. It conditionally mounts a Kerberos cache hostPath when `.Values.linux.krb5CacheDirectory` is non-empty and passes `--krb5-prefix` to the driver.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/rbac-csi-smb.yaml

## Purpose
This modern `v1.20.1` RBAC template provisions authorization for both the SMB CSI controller and node paths. It covers provisioning, expansion, leader election, controller secret lookup, and optional node secret lookup for inline ephemeral volumes.

## Important APIs, Types, And Functions
The template can render two `ServiceAccount` objects (`.Values.serviceAccount.controller` and `.Values.serviceAccount.node`), an external provisioner `ClusterRole`/`ClusterRoleBinding`, an external resizer `ClusterRole`/`ClusterRoleBinding`, and a conditional node secret role/binding when `.Values.feature.enableInlineVolume` is true. Helm gates are `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Values.feature.enableInlineVolume`.

## Control Flow
Service accounts are emitted first when enabled. RBAC creation then binds the controller service account to provisioning and resizing permissions. The inline-volume block adds `secrets get` for the node service account only when ephemeral volume support is advertised by the CSIDriver.

## State And Persistence Behavior
These cluster-scoped roles and bindings are persistent security state. They do not hold SMB data, but incorrect role updates can immediately break provisioning, expansion, or inline volume mount flows.

## Dependencies And Integration Points
The controller Deployment uses the controller account; Linux and Windows node DaemonSets use the node account. Provisioner/resizer sidecars need PV/PVC/Event/Lease permissions. Node secret access aligns with `podInfoOnMount` and inline CSI volumes that reference secrets.

## Risks And Test Signals
The main risk is excessive or missing Secret access. A disabled inline-volume feature should omit node secret RBAC; an enabled feature should render it. Test with `helm template --set feature.enableInlineVolume=false/true`, `kubectl auth can-i`, PVC provisioning, expansion, and inline-volume mount checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/storageclass.yaml

## Purpose
This template renders zero or more SMB `StorageClass` objects for chart `v1.20.1` from `.Values.storageClasses`. It lets chart users ship provisioner-ready classes with SMB share parameters instead of applying separate manifests.

## Important APIs, Types, And Functions
The Kubernetes API is `storage.k8s.io/v1/StorageClass`. Helm loops over `.Values.storageClasses`, emits `metadata.name`, common SMB labels, optional annotations, optional `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and optional `mountOptions`. The provisioner is always `$.Values.driver.name`.

## Control Flow
The whole file is skipped when `.Values.storageClasses` is unset or empty. Within each item, `reclaimPolicy` defaults to `Delete`, `volumeBindingMode` defaults to `Immediate`, and `allowVolumeExpansion` defaults to true unless the key is explicitly present.

## State And Persistence Behavior
Rendered StorageClasses are persistent cluster objects. They do not hold SMB credentials directly unless users place secret references in `parameters`; PVCs created later bind to these classes and inherit mount options such as `noserverino`.

## Dependencies And Integration Points
The class must match the `CSIDriver`/controller provisioner name and the controller RBAC must allow StorageClass reads plus secret access for provisioner and node-stage secrets. Parameters integrate with external SMB shares and Kubernetes Secrets.

## Risks And Test Signals
Risks include exposing incorrect secret namespaces, omitting required SMB mount options, or accidentally making the class default through annotations. Test by templating example `storageClasses`, creating PVCs against each class, checking PV parameters, testing expansion, and validating mount options on Linux/Windows nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/values.yaml

## Purpose
This `v1.20.1` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context and commented `storageClasses` examples.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, csiResizer, livenessProbe, nodeDriverRegistrar, csiproxy. Feature gates present here are: enableGetVolumeStats, enableInlineVolume. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths, Kerberos cache settings.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.20.1` and matching CSI sidecars. This version configures default-enabled Windows support with HostProcess containers. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.20.1/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.3.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `v1.3.0` with app version `v1.3.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.3.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.3.0`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses hard-coded `ClusterFirstWithHostNet` DNS policy. It uses the default Deployment strategy. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.3.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false` and `spec.podInfoOnMount: true`. Unlike later chart versions, it does not render `spec.volumeLifecycleModes`, does not advertise inline `Ephemeral` volumes, and does not expose custom CSIDriver labels.

## Control Flow
Rendering is unconditional and has no feature-gated branches in this older template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver` and on node-driver-registrar publishing the same driver name. Inline ephemeral volume support is not declared by this template version.

## Risks And Test Signals
Risk centers on driver-name drift and assumptions that this older chart supports inline ephemeral CSI volumes. Validate with `helm template`, `kubectl get csidriver`, and a smoke PVC that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.3.0`. It is active when `.Values.windows.enabled`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.3.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.node.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled. One template risk in these early versions is that `.Values.node.affinity` appears under the `nodeSelector` block rather than as a sibling `affinity` field.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

## Purpose
This `v1.3.0` RBAC template creates the controller service account and the external-provisioner cluster permissions used by the SMB CSI controller Deployment. It is named `rbac-csi-smb-controller.yaml` in these earlier chart versions because node workloads do not receive a separate chart-managed service account here.

## Important APIs, Types, And Functions
The rendered APIs are `v1/ServiceAccount`, `rbac.authorization.k8s.io/v1/ClusterRole`, and `ClusterRoleBinding`. `.Values.serviceAccount.create` gates service account creation, while `.Values.rbac.create` gates the role and binding. The role can create/delete PVs, update PVCs, read StorageClasses, CSINodes, Nodes, Events, Leases, and Secrets; leader election uses `coordination.k8s.io/leases`.

## Control Flow
Helm emits the service account only when requested, then independently emits RBAC when requested. The binding references `.Values.serviceAccount.controller` in `.Release.Namespace`, so setting `serviceAccount.create: false` still expects a preexisting account with the same name.

## State And Persistence Behavior
The resources are cluster-persistent authorization state. They do not store volume data, but they govern whether dynamic provisioning, event recording, secret lookup, and leader election can proceed.

## Dependencies And Integration Points
The controller Deployment uses this account. The provisioner sidecar depends on the PV/PVC/StorageClass/secret permissions; lease verbs must match the sidecar's `--leader-election` settings.

## Risks And Test Signals
The role is broad enough to read Kubernetes Secrets, which is necessary for SMB credentials but security-sensitive. Test with `helm template` for both create flags, `kubectl auth can-i` as the controller account, and dynamic provisioning of a PVC backed by an SMB secret.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/values.yaml

## Purpose
This `v1.3.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, livenessProbe, nodeDriverRegistrar. Feature gates present here are: none in this version. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.3.0` and matching CSI sidecars. This version configures optional legacy Windows support. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.3.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.4.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `v1.4.0` with app version `v1.4.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.4.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.4.0`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses hard-coded `ClusterFirstWithHostNet` DNS policy. It uses the default Deployment strategy. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.4.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false` and `spec.podInfoOnMount: true`. Unlike later chart versions, it does not render `spec.volumeLifecycleModes`, does not advertise inline `Ephemeral` volumes, and does not expose custom CSIDriver labels.

## Control Flow
Rendering is unconditional and has no feature-gated branches in this older template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver` and on node-driver-registrar publishing the same driver name. Inline ephemeral volume support is not declared by this template version.

## Risks And Test Signals
Risk centers on driver-name drift and assumptions that this older chart supports inline ephemeral CSI volumes. Validate with `helm template`, `kubectl get csidriver`, and a smoke PVC that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.4.0`. It is active when `.Values.windows.enabled`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.4.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled. One template risk in these early versions is that `.Values.node.affinity` appears under the `nodeSelector` block rather than as a sibling `affinity` field.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

## Purpose
This `v1.4.0` RBAC template creates the controller service account and the external-provisioner cluster permissions used by the SMB CSI controller Deployment. It is named `rbac-csi-smb-controller.yaml` in these earlier chart versions because node workloads do not receive a separate chart-managed service account here.

## Important APIs, Types, And Functions
The rendered APIs are `v1/ServiceAccount`, `rbac.authorization.k8s.io/v1/ClusterRole`, and `ClusterRoleBinding`. `.Values.serviceAccount.create` gates service account creation, while `.Values.rbac.create` gates the role and binding. The role can create/delete PVs, update PVCs, read StorageClasses, CSINodes, Nodes, Events, Leases, and Secrets; leader election uses `coordination.k8s.io/leases`.

## Control Flow
Helm emits the service account only when requested, then independently emits RBAC when requested. The binding references `.Values.serviceAccount.controller` in `.Release.Namespace`, so setting `serviceAccount.create: false` still expects a preexisting account with the same name.

## State And Persistence Behavior
The resources are cluster-persistent authorization state. They do not store volume data, but they govern whether dynamic provisioning, event recording, secret lookup, and leader election can proceed.

## Dependencies And Integration Points
The controller Deployment uses this account. The provisioner sidecar depends on the PV/PVC/StorageClass/secret permissions; lease verbs must match the sidecar's `--leader-election` settings.

## Risks And Test Signals
The role is broad enough to read Kubernetes Secrets, which is necessary for SMB credentials but security-sensitive. Test with `helm template` for both create flags, `kubectl auth can-i` as the controller account, and dynamic provisioning of a PVC backed by an SMB secret.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/values.yaml

## Purpose
This `v1.4.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, livenessProbe, nodeDriverRegistrar. Feature gates present here are: enableGetVolumeStats. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.4.0` and matching CSI sidecars. This version configures optional legacy Windows support. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.4.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.5.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `v1.5.0` with app version `v1.5.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.5.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-controller.yaml

## Purpose
This template renders the Linux controller `apps/v1` `Deployment` for the SMB CSI driver in chart `v1.5.0`. It runs the controller service account with the CSI sidecars and the SMB controller plugin that handles dynamic provisioning and, in newer versions, expansion.

## Important APIs, Types, And Functions
The resource is a `Deployment` named `.Values.controller.name`. It renders containers for csi-provisioner, liveness-probe, and smb. The provisioner connects to `/csi/csi.sock` through `ADDRESS`; the SMB container receives `CSI_ENDPOINT`, `.Values.driver.name`, metrics and health ports, log level, and, in later charts, `--working-mount-dir`. Image references may use `.Values.image.baseRepo` when repositories start with `/`.

## Control Flow
Helm injects labels, pod labels, annotations, pull secrets, resources, node selectors, tolerations, and affinity from values. This version uses hard-coded `ClusterFirstWithHostNet` DNS policy. It uses the default Deployment strategy. Control-plane scheduling is either explicitly set by affinity or synthesized from `runOnMaster`/`runOnControlPlane` in modern charts.

## State And Persistence Behavior
The controller stores its CSI socket in an `emptyDir`; authoritative state lives in Kubernetes PV/PVC/Lease objects and remote SMB shares. Leader election uses Leases, so RBAC and namespace alignment are required.

## Dependencies And Integration Points
It depends on the RBAC template, controller service account, CSI provisioner image, optional resizer image, liveness-probe image, and the SMB plugin image. It integrates with the `CSIDriver`, `StorageClass` provisioner name, and Kubernetes events.

## Risks And Test Signals
Risks include broken image path composition, insufficient RBAC for provisioning/resizing, controller scheduling to the wrong OS, and privileged SMB container requirements. Test with `helm template`, `helm lint`, rendered Deployment inspection, PVC create/delete, expansion where available, and liveness/metrics endpoint checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-driver.yaml

## Purpose
This template renders the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object for the SMB CSI driver in chart `v1.5.0`. It registers `.Values.driver.name` with Kubernetes so kubelet and the CSI sidecars understand that SMB volumes do not require attach operations and should receive pod information on mount.

## Important APIs, Types, And Functions
The core API is `CSIDriver`. The template sets `spec.attachRequired: false` and `spec.podInfoOnMount: true`. Unlike later chart versions, it does not render `spec.volumeLifecycleModes`, does not advertise inline `Ephemeral` volumes, and does not expose custom CSIDriver labels.

## Control Flow
Rendering is unconditional and has no feature-gated branches in this older template. The rendered driver name is consumed by controller, node, registrar, provisioner, resizer, RBAC, and StorageClass templates.

## State And Persistence Behavior
The object is persistent cluster configuration, not pod-local state. Changing the driver name after installation is disruptive because node socket paths, registration paths, StorageClasses, and existing PVs are tied to the old provisioner identity.

## Dependencies And Integration Points
It depends on Kubernetes supporting `storage.k8s.io/v1` `CSIDriver` and on node-driver-registrar publishing the same driver name. Inline ephemeral volume support is not declared by this template version.

## Risks And Test Signals
Risk centers on driver-name drift and assumptions that this older chart supports inline ephemeral CSI volumes. Validate with `helm template`, `kubectl get csidriver`, and a smoke PVC that checks kubelet registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.5.0`. It is active when `.Values.windows.enabled`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.5.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.linux.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled. One template risk in these early versions is that `.Values.node.affinity` appears under the `nodeSelector` block rather than as a sibling `affinity` field.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

## Purpose
This `v1.5.0` RBAC template creates the controller service account and the external-provisioner cluster permissions used by the SMB CSI controller Deployment. It is named `rbac-csi-smb-controller.yaml` in these earlier chart versions because node workloads do not receive a separate chart-managed service account here.

## Important APIs, Types, And Functions
The rendered APIs are `v1/ServiceAccount`, `rbac.authorization.k8s.io/v1/ClusterRole`, and `ClusterRoleBinding`. `.Values.serviceAccount.create` gates service account creation, while `.Values.rbac.create` gates the role and binding. The role can create/delete PVs, update PVCs, read StorageClasses, CSINodes, Nodes, Events, Leases, and Secrets; leader election uses `coordination.k8s.io/leases`.

## Control Flow
Helm emits the service account only when requested, then independently emits RBAC when requested. The binding references `.Values.serviceAccount.controller` in `.Release.Namespace`, so setting `serviceAccount.create: false` still expects a preexisting account with the same name.

## State And Persistence Behavior
The resources are cluster-persistent authorization state. They do not store volume data, but they govern whether dynamic provisioning, event recording, secret lookup, and leader election can proceed.

## Dependencies And Integration Points
The controller Deployment uses this account. The provisioner sidecar depends on the PV/PVC/StorageClass/secret permissions; lease verbs must match the sidecar's `--leader-election` settings.

## Risks And Test Signals
The role is broad enough to read Kubernetes Secrets, which is necessary for SMB credentials but security-sensitive. Test with `helm template` for both create flags, `kubectl auth can-i` as the controller account, and dynamic provisioning of a PVC backed by an SMB secret.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/values.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/values.yaml

## Purpose
This `v1.5.0` `values.yaml` is the main configuration surface for the SMB CSI Driver Helm chart. It defines image repositories/tags, service account and RBAC toggles, driver name, controller and node scheduling, resource requests/limits, Linux and Windows node defaults, pod metadata, priority class, and security context.

## Important APIs, Types, And Functions
Although not a Kubernetes API object itself, this file feeds every sibling template. Image sections present in this version are: smb, csiProvisioner, livenessProbe, nodeDriverRegistrar. Feature gates present here are: enableGetVolumeStats. The values govern `Deployment`, `DaemonSet`, `CSIDriver`, RBAC, optional CSI proxy, and optional StorageClass rendering.

## Control Flow
Helm conditionals consume booleans such as `serviceAccount.create`, `rbac.create`, `linux.enabled`, `windows.enabled`, `windows.useHostProcessContainers`, `windows.csiproxy.enabled`, and feature flags. Controller and node values determine replica count, rolling update budget, DNS policy, host scheduling, tolerations, selectors, resource blocks, pull policy, and log verbosity.

## State And Persistence Behavior
The file stores desired configuration, not runtime state. It indirectly controls persistent cluster objects and host state: kubelet plugin directories, registration sockets, SMB mount cleanup, controller leader-election Leases, Secrets access, StorageClasses, and optional Kerberos cache hostPaths.

## Dependencies And Integration Points
Defaults assume the SMB CSI driver image tag `1.5.0` and matching CSI sidecars. This version configures optional legacy Windows support. The driver name must remain consistent with PV provisioner names, CSIDriver, registrar paths, and StorageClasses.

## Risks And Test Signals
Risks include image registry drift, enabling Windows without compatible cluster support, granting Secret access through RBAC, invalid custom kubelet paths, and resource defaults that underfit production clusters. Test with `helm lint`, `helm template` across Linux-only, Windows legacy, HostProcess, inline-volume, and StorageClass values, followed by PVC provision/mount/resize/unmount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.5.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/Chart.yaml -->
# sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/Chart.yaml

## Purpose
This Helm `Chart.yaml` declares the SMB CSI Driver chart package for `v1.6.0`. It names the chart `csi-driver-smb`, describes it as the Kubernetes SMB CSI driver, and binds the chart release version to `v1.6.0` with app version `v1.6.0`.

## Important APIs, Types, And Functions
The file uses the Helm chart metadata API (`apiVersion: v1`) rather than a Kubernetes workload API. Its important fields are `name`, `description`, `version`, and `appVersion`; there are no templates, functions, dependencies, or exported objects in this file.

## Control Flow
There is no runtime control flow. Helm reads this metadata before rendering sibling templates, so this file influences chart identity, packaging, index entries, and upgrade/version selection but does not conditionally render resources.

## State And Persistence Behavior
The file is declarative metadata only. Persistent state is created by sibling templates such as `CSIDriver`, `Deployment`, `DaemonSet`, RBAC, and `StorageClass` resources, not by this descriptor.

## Dependencies And Integration Points
The chart integrates with Helm repositories and Kubernetes package installation tooling. Its version must stay aligned with image tags and values defaults in the same chart directory, otherwise users can install a package whose metadata and rendered controller/node image versions disagree.

## Risks And Test Signals
Primary risk is version drift between `appVersion`, `version`, packaged `.tgz` archives, and image tags. Test by running `helm lint`, `helm template`, and checking chart repository indexes for the expected `v1.6.0` package identity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.6.0/csi-driver-smb/Chart.yaml -->
