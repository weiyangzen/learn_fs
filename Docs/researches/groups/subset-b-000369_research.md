# subset-b-000369 research

Grouped research for CSI Driver SMB deployment manifests assigned to `subset-b-000369`. Each section preserves the source path as its title and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.12.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v3.5.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.10.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.12.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.12.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.12.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.10.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.8.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.12.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.12.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.10.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.8.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.12.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the health-port flag. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.12.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.12.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also creates `csi-smb-node-sa`, but this version does not yet define separate resizer or node-secret ClusterRoles.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.12.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.13.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v3.6.1`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.11.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.13.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.13.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.13.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.11.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.9.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.13.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.13.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.11.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.9.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.13.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the health-port flag. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.13.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.13.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also creates `csi-smb-node-sa`, but this version does not yet define separate resizer or node-secret ClusterRoles.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.13.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.14.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.0.1`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.14.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.14.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.14.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.11.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.14.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.14.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.11.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.14.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.14.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.14.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also creates `csi-smb-node-sa`, but this version does not yet define separate resizer or node-secret ClusterRoles.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.14.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.15.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.0.2`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.15.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.15.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.15.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.11.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.15.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/csi-smb-node-windows.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.15.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.15.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also creates `csi-smb-node-sa`, but this version does not yet define separate resizer or node-secret ClusterRoles.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.15.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.16.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.0.2`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.16.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.16.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.16.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.11.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.16.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.16.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.13.1`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.11.1`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.16.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.16.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.16.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also creates `csi-smb-node-sa`, but this version does not yet define separate resizer or node-secret ClusterRoles.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.16.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.17.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 4 control-plane tolerations. Containers are `csi-provisioner`, `csi-resizer`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.2.0`, `csi-resizer` `registry.k8s.io/sig-storage/csi-resizer:v1.13.1`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.17.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. It also runs `csi-resizer` for expansion controller loops. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, 30 minute provisioner retry ceiling, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '400Mi'}; `csi-resizer` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '400Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.17.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes `Persistent`, `Ephemeral`.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node-windows-hostprocess.yaml

Purpose: Windows HostProcess node-plugin DaemonSet for SMB CSI v1.17.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `init`, `node-driver-registrar`, `smb`. Images: `init` `registry.k8s.io/sig-storage/smbplugin:v1.17.0-windows-hp`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.13.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.17.0-windows-hp`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. This HostProcess variant omits the liveness sidecar and uses an init container to create `C:\var\lib\kubelet\plugins\smb.csi.k8s.io` before starting host-process registrar and SMB containers.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, HostProcess support, host networking, and direct host filesystem access rather than CSI Proxy pipe mounts. Host paths/pipes include: none declared, because this HostProcess manifest relies on host namespace access and explicit plugin directory initialization.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.17.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.15.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.13.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.17.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.17.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.15.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.13.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.17.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.17.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.17.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding, ClusterRole/smb-external-resizer-role, ClusterRoleBinding/smb-csi-resizer-role, ClusterRole/csi-smb-node-secret-role, ClusterRoleBinding/csi-smb-node-secret-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get) | `smb-external-resizer-role` -> core:persistentvolumes(get/list/watch/update/patch); core:persistentvolumeclaims(get/list/watch); core:persistentvolumeclaims/status(update/patch); core:events(list/watch/create/update/patch); coordination.k8s.io:leases(get/list/watch/create/update/patch) | `csi-smb-node-secret-role` -> core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also binds `csi-smb-controller-sa` to `smb-external-resizer-role` for PVC status and PV update/patch flows, and binds `csi-smb-node-sa` to a Secret get role for node-side credential access.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.17.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.18.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 4 control-plane tolerations. Containers are `csi-provisioner`, `csi-resizer`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.2.0`, `csi-resizer` `registry.k8s.io/sig-storage/csi-resizer:v1.13.2`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.18.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. It also runs `csi-resizer` for expansion controller loops. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, 30 minute provisioner retry ceiling, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '400Mi'}; `csi-resizer` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '400Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.18.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes `Persistent`, `Ephemeral`.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-driver.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.18.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.15.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.13.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.18.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.18.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.15.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.13.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.18.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.18.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.18.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding, ClusterRole/smb-external-resizer-role, ClusterRoleBinding/smb-csi-resizer-role, ClusterRole/csi-smb-node-secret-role, ClusterRoleBinding/csi-smb-node-secret-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get) | `smb-external-resizer-role` -> core:persistentvolumes(get/list/watch/update/patch); core:persistentvolumeclaims(get/list/watch); core:persistentvolumeclaims/status(update/patch); core:events(list/watch/create/update/patch); coordination.k8s.io:leases(get/list/watch/create/update/patch) | `csi-smb-node-secret-role` -> core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also binds `csi-smb-controller-sa` to `smb-external-resizer-role` for PVC status and PV update/patch flows, and binds `csi-smb-node-sa` to a Secret get role for node-side credential access.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.18.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.19.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 4 control-plane tolerations. Containers are `csi-provisioner`, `csi-resizer`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.3.0`, `csi-resizer` `registry.k8s.io/sig-storage/csi-resizer:v1.14.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.17.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. It also runs `csi-resizer` for expansion controller loops. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, 30 minute provisioner retry ceiling, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '400Mi'}; `csi-resizer` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '400Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.19.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes `Persistent`, `Ephemeral`.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node-windows-hostprocess.yaml

Purpose: Windows HostProcess node-plugin DaemonSet for SMB CSI v1.19.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `init`, `node-driver-registrar`, `smb`. Images: `init` `registry.k8s.io/sig-storage/smbplugin:v1.19.0-windows-hp`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.0-windows-hp`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. This HostProcess variant omits the liveness sidecar and uses an init container to create `C:\var\lib\kubelet\plugins\smb.csi.k8s.io` before starting host-process registrar and SMB containers.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, HostProcess support, host networking, and direct host filesystem access rather than CSI Proxy pipe mounts. Host paths/pipes include: none declared, because this HostProcess manifest relies on host namespace access and explicit plugin directory initialization.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.19.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.16.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.19.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.17.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.19.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding, ClusterRole/smb-external-resizer-role, ClusterRoleBinding/smb-csi-resizer-role, ClusterRole/csi-smb-node-secret-role, ClusterRoleBinding/csi-smb-node-secret-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get) | `smb-external-resizer-role` -> core:persistentvolumes(get/list/watch/update/patch); core:persistentvolumeclaims(get/list/watch); core:persistentvolumeclaims/status(update/patch); core:events(list/watch/create/update/patch); coordination.k8s.io:leases(get/list/watch/create/update/patch) | `csi-smb-node-secret-role` -> core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also binds `csi-smb-controller-sa` to `smb-external-resizer-role` for PVC status and PV update/patch flows, and binds `csi-smb-node-sa` to a Secret get role for node-side credential access.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.19.1. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 4 control-plane tolerations. Containers are `csi-provisioner`, `csi-resizer`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v5.3.0`, `csi-resizer` `registry.k8s.io/sig-storage/csi-resizer:v1.14.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.17.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.1`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. It also runs `csi-resizer` for expansion controller loops. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, 30 minute provisioner retry ceiling, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '400Mi'}; `csi-resizer` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '400Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.19.1. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes `Persistent`, `Ephemeral`.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node-windows-hostprocess.yaml

Purpose: Windows HostProcess node-plugin DaemonSet for SMB CSI v1.19.1. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `init`, `node-driver-registrar`, `smb`. Images: `init` `registry.k8s.io/sig-storage/smbplugin:v1.19.1-windows-hp`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.1-windows-hp`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. This HostProcess variant omits the liveness sidecar and uses an init container to create `C:\var\lib\kubelet\plugins\smb.csi.k8s.io` before starting host-process registrar and SMB containers.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, HostProcess support, host networking, and direct host filesystem access rather than CSI Proxy pipe mounts. Host paths/pipes include: none declared, because this HostProcess manifest relies on host namespace access and explicit plugin directory initialization.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.19.1. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.16.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.1`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.19.1. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.17.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.19.1`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.19.1/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.19.1. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding, ClusterRole/smb-external-resizer-role, ClusterRoleBinding/smb-csi-resizer-role, ClusterRole/csi-smb-node-secret-role, ClusterRoleBinding/csi-smb-node-secret-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get) | `smb-external-resizer-role` -> core:persistentvolumes(get/list/watch/update/patch); core:persistentvolumeclaims(get/list/watch); core:persistentvolumeclaims/status(update/patch); core:events(list/watch/create/update/patch); coordination.k8s.io:leases(get/list/watch/create/update/patch) | `csi-smb-node-secret-role` -> core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also binds `csi-smb-controller-sa` to `smb-external-resizer-role` for PVC status and PV update/patch flows, and binds `csi-smb-node-sa` to a Secret get role for node-side credential access.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.19.1/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.2.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `2`, selector label `app=csi-smb-controller`, `hostNetwork=None`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 2 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v2.1.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.3.0`, `smb` `mcr.microsoft.com/k8s/csi/smb-csi:v1.2.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: none beyond leader election.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and no pod-level seccomp profile in this version.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': '100m', 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': '100m', 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': '200m', 'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.2.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.2.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.3.0`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.2.0`, `smb` `mcr.microsoft.com/k8s/csi/smb-csi:v1.2.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.2.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.3.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.2.0`, `smb` `mcr.microsoft.com/k8s/csi/smb-csi:v1.2.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares and publishes plugin metrics on 29645. The liveness sidecar probes the CSI socket using the health-port flag.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.2.0/rbac-csi-smb-controller.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.2.0. This controller-only file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It does not create the node ServiceAccount; node manifests in this release rely on preexisting/default permissions or separate setup.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.2.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.20.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 4 control-plane tolerations. Containers are `csi-provisioner`, `csi-resizer`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v6.0.0`, `csi-resizer` `registry.k8s.io/sig-storage/csi-resizer:v2.0.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.17.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. It also runs `csi-resizer` for expansion controller loops. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, VolumeAttributesClass disabled, 30 minute provisioner retry ceiling, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '400Mi'}; `csi-resizer` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '400Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.20.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes `Persistent`, `Ephemeral`.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node-windows-hostprocess.yaml

Purpose: Windows HostProcess node-plugin DaemonSet for SMB CSI v1.20.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `init`, `node-driver-registrar`, `smb`. Images: `init` `registry.k8s.io/sig-storage/smbplugin:v1.20.0-windows-hp`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.0-windows-hp`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. This HostProcess variant omits the liveness sidecar and uses an init container to create `C:\var\lib\kubelet\plugins\smb.csi.k8s.io` before starting host-process registrar and SMB containers.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, HostProcess support, host networking, and direct host filesystem access rather than CSI Proxy pipe mounts. Host paths/pipes include: none declared, because this HostProcess manifest relies on host namespace access and explicit plugin directory initialization.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.20.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.16.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.20.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.17.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.0/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.20.0. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding, ClusterRole/smb-external-resizer-role, ClusterRoleBinding/smb-csi-resizer-role, ClusterRole/csi-smb-node-secret-role, ClusterRoleBinding/csi-smb-node-secret-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get) | `smb-external-resizer-role` -> core:persistentvolumes(get/list/watch/update/patch); core:persistentvolumeclaims(get/list/watch); core:persistentvolumeclaims/status(update/patch); core:events(list/watch/create/update/patch); coordination.k8s.io:leases(get/list/watch/create/update/patch) | `csi-smb-node-secret-role` -> core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also binds `csi-smb-controller-sa` to `smb-external-resizer-role` for PVC status and PV update/patch flows, and binds `csi-smb-node-sa` to a Secret get role for node-side credential access.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.0/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.20.1. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 4 control-plane tolerations. Containers are `csi-provisioner`, `csi-resizer`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v6.1.1`, `csi-resizer` `registry.k8s.io/sig-storage/csi-resizer:v2.1.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.18.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.1`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. It also runs `csi-resizer` for expansion controller loops. The liveness sidecar probes the same socket using the HTTP endpoint; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: HonorPVReclaimPolicy, 30 minute provisioner retry ceiling, PVC/PV metadata injection.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and pod seccomp `RuntimeDefault`.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '400Mi'}; `csi-resizer` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '400Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.20.1. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes `Persistent`, `Ephemeral`.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node-windows-hostprocess.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node-windows-hostprocess.yaml

Purpose: Windows HostProcess node-plugin DaemonSet for SMB CSI v1.20.1. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `init`, `node-driver-registrar`, `smb`. Images: `init` `registry.k8s.io/sig-storage/smbplugin:v1.20.1-windows-hp`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.16.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.1-windows-hp`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. This HostProcess variant omits the liveness sidecar and uses an init container to create `C:\var\lib\kubelet\plugins\smb.csi.k8s.io` before starting host-process registrar and SMB containers.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, HostProcess support, host networking, and direct host filesystem access rather than CSI Proxy pipe mounts. Host paths/pipes include: none declared, because this HostProcess manifest relies on host namespace access and explicit plugin directory initialization.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.20.1. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.16.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.15.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.1`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`, `--remove-smb-mapping-during-unmount=true`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.20.1. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.18.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.16.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.20.1`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares. The liveness sidecar probes the CSI socket using the HTTP endpoint.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses pod seccomp `RuntimeDefault` and a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/rbac-csi-smb.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.20.1/rbac-csi-smb.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.20.1. This combined controller/node file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ServiceAccount/csi-smb-node-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding, ClusterRole/smb-external-resizer-role, ClusterRoleBinding/smb-csi-resizer-role, ClusterRole/csi-smb-node-secret-role, ClusterRoleBinding/csi-smb-node-secret-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/patch/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get) | `smb-external-resizer-role` -> core:persistentvolumes(get/list/watch/update/patch); core:persistentvolumeclaims(get/list/watch); core:persistentvolumeclaims/status(update/patch); core:events(list/watch/create/update/patch); coordination.k8s.io:leases(get/list/watch/create/update/patch) | `csi-smb-node-secret-role` -> core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It also binds `csi-smb-controller-sa` to `smb-external-resizer-role` for PVC status and PV update/patch flows, and binds `csi-smb-node-sa` to a Secret get role for node-side credential access.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.20.1/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.3.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `2`, selector label `app=csi-smb-controller`, `hostNetwork=None`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 2 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `mcr.microsoft.com/oss/kubernetes-csi/csi-provisioner:v2.2.2`, `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.4.0`, `smb` `mcr.microsoft.com/k8s/csi/smb-csi:v1.3.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: none beyond leader election.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and no pod-level seccomp profile in this version.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': '100m', 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': '100m', 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': '200m', 'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.3.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.3.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.4.0`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.3.0`, `smb` `mcr.microsoft.com/k8s/csi/smb-csi:v1.3.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.3.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.4.0`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.3.0`, `smb` `mcr.microsoft.com/k8s/csi/smb-csi:v1.3.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares and publishes plugin metrics on 29645. The liveness sidecar probes the CSI socket using the health-port flag. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.3.0/rbac-csi-smb-controller.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.3.0. This controller-only file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It does not create the node ServiceAccount; node manifests in this release rely on preexisting/default permissions or separate setup.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.3.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.4.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `2`, selector label `app=csi-smb-controller`, `hostNetwork=None`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 2 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `mcr.microsoft.com/oss/kubernetes-csi/csi-provisioner:v2.2.2`, `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.5.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.4.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: none beyond leader election.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and no pod-level seccomp profile in this version.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.4.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.4.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.5.0`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.4.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.4.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.4.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v2.5.0`, `node-driver-registrar` `mcr.microsoft.com/oss/kubernetes-csi/csi-node-driver-registrar:v2.4.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.4.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares and publishes plugin metrics on 29645. The liveness sidecar probes the CSI socket using the health-port flag. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.4.0/rbac-csi-smb-controller.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.4.0. This controller-only file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It does not create the node ServiceAccount; node manifests in this release rely on preexisting/default permissions or separate setup.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.4.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.5.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `2`, selector label `app=csi-smb-controller`, `hostNetwork=None`, DNS policy `ClusterFirstWithHostNet`, Linux node selection, `system-cluster-critical` priority, and 2 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v2.2.2`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.5.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.5.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: none beyond leader election.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and no pod-level seccomp profile in this version.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.5.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.5.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.5.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.4.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.5.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.5.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `ClusterFirstWithHostNet`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.5.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.4.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.5.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares and publishes plugin metrics on 29645. The liveness sidecar probes the CSI socket using the health-port flag. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.5.0/rbac-csi-smb-controller.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.5.0. This controller-only file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It does not create the node ServiceAccount; node manifests in this release rely on preexisting/default permissions or separate setup.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.5.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.6.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=None`, DNS policy `Default`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v3.1.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.5.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.6.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: none beyond leader election.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and no pod-level seccomp profile in this version.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.6.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-node-windows.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-node-windows.yaml

Purpose: Windows node-plugin DaemonSet for SMB CSI v1.6.0. It deploys `csi-smb-node-win` to Windows nodes so kubelet can register the SMB CSI driver and publish SMB-backed volumes for Windows workloads.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node-win` with rolling update `maxUnavailable: 1`, Windows node selector, `system-node-critical` priority, and `csi-smb-node-sa` where present. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.5.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.4.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.6.0`.

Control flow: The pod runs on Windows nodes and uses Windows paths for CSI sockets such as `unix://C:\csi\csi.sock` or `unix://C:\var\lib\kubelet\plugins\smb.csi.k8s.io\csi.sock`. `node-driver-registrar` registers the kubelet plugin path, while `smbplugin.exe` handles CSI node calls using `--nodeid=$(KUBE_NODE_NAME)`. Liveness probing is present in standard Windows manifests; HostProcess manifests instead rely on the host-process SMB plugin and registrar startup path.

State/persistence: Host state lives under `C:\var\lib\kubelet` plugin, registry, and workload mount directories, plus Windows SMB mappings created during node publish. The manifest mounts Windows hostPath directories and, for CSI Proxy based operation, named pipes for filesystem and SMB proxy APIs.

Dependencies and integration points: Integrates with Windows kubelet CSI registration, `CSIDriver/smb.csi.k8s.io`, SMB credentials in Kubernetes Secrets, CSI Proxy pipes when present, and HostProcess support when enabled. Host paths/pipes include: `csi-proxy-fs-pipe-v1` -> `\\.\pipe\csi-proxy-filesystem-v1`, `csi-proxy-smb-pipe-v1` -> `\\.\pipe\csi-proxy-smb-v1`, `csi-proxy-fs-pipe-v1beta1` -> `\\.\pipe\csi-proxy-filesystem-v1beta1`, `csi-proxy-smb-pipe-v1beta1` -> `\\.\pipe\csi-proxy-smb-v1beta1`, `registration-dir` -> `C:\var\lib\kubelet\plugins_registry\`, `kubelet-dir` -> `C:\var\lib\kubelet\`, `plugin-dir` -> `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`.

Risks: Windows path escaping and socket path consistency are fragile. CSI Proxy version drift matters when both v1 and v1beta1 pipes are mounted. HostProcess variants require Kubernetes/Windows support for `windowsOptions.hostProcess` and run as `NT AUTHORITY\SYSTEM`, which is powerful. Failure to remove SMB mappings during unmount can leak credentials or drive mappings across workloads.

Test signals: DaemonSet readiness on Windows nodes, kubelet registration for `smb.csi.k8s.io`, liveness probe success where configured, Windows pod mount/read/write/unmount, SMB mapping cleanup after pod deletion, and HostProcess startup logs when using the `-windows-hp` image.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-node.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-node.yaml

Purpose: Linux node-plugin DaemonSet for SMB CSI v1.6.0. It installs one `csi-smb-node` pod on every Linux node so kubelet can register `smb.csi.k8s.io` and publish SMB volumes into pod mount namespaces.

Important APIs/types/functions: Declares `apps/v1` `DaemonSet/csi-smb-node` with rolling update `maxUnavailable: 1`, `serviceAccountName: csi-smb-node-sa`, `hostNetwork=True`, DNS policy `Default`, `system-node-critical` priority, Linux node selector, and broad `Exists` toleration. Containers are `liveness-probe`, `node-driver-registrar`, `smb`. Images: `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.5.0`, `node-driver-registrar` `registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.4.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.6.0`.

Control flow: Kubelet schedules the DaemonSet on Linux nodes, creates `/var/lib/kubelet/plugins/smb.csi.k8s.io` for the CSI socket, and exposes `/var/lib/kubelet/plugins_registry` for node-driver registration. `node-driver-registrar` announces the driver using `--kubelet-registration-path=$(DRIVER_REG_SOCK_PATH)`. The SMB plugin starts with `--endpoint=$(CSI_ENDPOINT)` and `--nodeid=$(KUBE_NODE_NAME)`, then handles CSI node calls for stage/publish/unpublish against SMB shares and publishes plugin metrics on 29645. The liveness sidecar probes the CSI socket using the health-port flag. Registrar has an exec kubelet-registration liveness probe.

State/persistence: Persistent host state is limited to kubelet plugin sockets/registration files and mounted SMB volume paths under `/var/lib/kubelet`; the pod-local CSI socket is backed by hostPath. Mount propagation is `Bidirectional` on the kubelet mountpoint directory so mounts created by the plugin become visible to kubelet and workload pods.

Dependencies and integration points: Depends on Linux CIFS/SMB mount support on the node, kubelet plugin registration, the `CSIDriver` object, controller-created PV metadata, Kubernetes Secrets for SMB credentials, and companion RBAC for node secret reads in newer releases. Host paths: `socket-dir` -> `/var/lib/kubelet/plugins/smb.csi.k8s.io`, `mountpoint-dir` -> `/var/lib/kubelet/`, `registration-dir` -> `/var/lib/kubelet/plugins_registry/`. Pod security uses a privileged SMB container.

Risks: Privileged access plus bidirectional `/var/lib/kubelet` mount propagation is necessary for CSI but high impact. Missing CIFS utilities/kernel support, blocked host networking, wrong registration path, or stale sockets can make all SMB volumes fail on a node. Older manifests also expose plugin metrics from the node container, so port collisions and unauthenticated metrics exposure should be considered.

Test signals: DaemonSet desired/current/ready counts, `CSINode` entries for `smb.csi.k8s.io`, kubelet plugin registration files, liveness `/healthz` on 29643, successful Linux pod mount/read/write/unmount against an SMB share, and cleanup of mountpoints after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/rbac-csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.6.0/rbac-csi-smb-controller.yaml

Purpose: RBAC and ServiceAccount manifest for SMB CSI v1.6.0. This controller-only file grants the external sidecars the Kubernetes API permissions needed to provision SMB PVs and, in newer releases, resize volumes and let node pods read SMB credential Secrets.

Important APIs/types/functions: Declares ServiceAccount/csi-smb-controller-sa, ClusterRole/smb-external-provisioner-role, ClusterRoleBinding/smb-csi-provisioner-binding. ClusterRole rules: `smb-external-provisioner-role` -> core:persistentvolumes(get/list/watch/create/delete); core:persistentvolumeclaims(get/list/watch/update); storage.k8s.io:storageclasses(get/list/watch); core:events(get/list/watch/create/update/patch); storage.k8s.io:csinodes(get/list/watch); core:nodes(get/list/watch); coordination.k8s.io:leases(get/list/watch/create/update/patch); core:secrets(get).

Control flow: Applying this manifest creates service accounts in `kube-system`, then binds `csi-smb-controller-sa` to `smb-external-provisioner-role` so the provisioner can watch PVCs/PVs/StorageClasses/CSINodes/nodes, emit Events, read Secrets, and coordinate leader election with Leases. It does not create the node ServiceAccount; node manifests in this release rely on preexisting/default permissions or separate setup.

State/persistence: RBAC objects are persisted cluster-scoped authorization state plus namespaced ServiceAccounts. They do not run code but gate controller and node reconciliation at every API call. Leader election state itself is stored separately as `coordination.k8s.io` Lease objects.

Dependencies and integration points: Must be applied before the controller Deployment and node DaemonSets that reference these ServiceAccounts. It integrates with external-provisioner, external-resizer when present, Kubernetes Events, PV/PVC controllers, StorageClass lookup, CSINode discovery, and Secret-backed SMB credentials.

Risks: Broad Secret `get` access is necessary for credential retrieval but sensitive. Missing `patch`/`update` verbs can break newer sidecar behavior, while over-broad cluster roles increase exposure if the service account token is compromised. Version skew is especially visible around resize support and PV reclaim policy handling.

Test signals: `kubectl auth can-i` checks as the controller and node service accounts, successful leader-election Lease updates, absence of RBAC forbidden errors in sidecar logs, dynamic provisioning/deletion, Secret-backed mounts, and PVC expansion tests when resizer RBAC is present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.6.0/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-controller.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-controller.yaml

Purpose: Kubernetes Deployment manifest for the SMB CSI controller in v1.7.0. It runs one `csi-smb-controller` workload in `kube-system` with `csi-smb-controller-sa`, binding the external CSI sidecars to the in-pod Unix socket and exposing SMB controller metrics on port 29644.

Important APIs/types/functions: Declares `apps/v1` `Deployment` `Deployment/csi-smb-controller` with replicas `1`, selector label `app=csi-smb-controller`, `hostNetwork=None`, DNS policy `Default`, Linux node selection, `system-cluster-critical` priority, and 3 control-plane tolerations. Containers are `csi-provisioner`, `liveness-probe`, `smb`. Images: `csi-provisioner` `registry.k8s.io/sig-storage/csi-provisioner:v3.1.0`, `liveness-probe` `registry.k8s.io/sig-storage/livenessprobe:v2.6.0`, `smb` `registry.k8s.io/sig-storage/smbplugin:v1.7.0`.

Control flow: Kubernetes schedules the controller pod on Linux control-plane-capable nodes, creates an `emptyDir` socket directory at `/csi`, and starts the SMB plugin with `--endpoint=$(CSI_ENDPOINT)`. The provisioner connects to `/csi/csi.sock`, uses leader election, `--leader-election-namespace=kube-system`, and watches PVC/PV/storage objects to issue CSI `CreateVolume`/`DeleteVolume` calls through the socket. No external resizer is present in this release. The liveness sidecar probes the same socket using the legacy health-port flag; the SMB container serves `/healthz` on 29642 and metrics on 29644.

State/persistence: This controller is mostly stateless: the pod socket is an `emptyDir`, while durable state lives in Kubernetes PV/PVC objects, Leases for leader election, Secrets referenced by volumes, and remote SMB shares. Runtime state includes sidecar work queues, liveness status, and emitted Events. Feature switches present here: none beyond leader election.

Dependencies and integration points: Integrates with the `CSIDriver` object `smb.csi.k8s.io`, RBAC in the companion `rbac-csi-smb*.yaml`, kube-controller-manager storage workflows, the external provisioner/resizer sidecars, and the SMB plugin image. Pod security relies on privileged SMB container access and no pod-level seccomp profile in this version.

Risks: Privileged controller plugin execution and host networking increase blast radius if the image or socket is compromised. Leader-election namespace and RBAC must match the deployment namespace or provisioning stalls. Sidecar/image version skew can break CSI calls. Health-probe flag changes between older and newer sidecars make upgrades sensitive to exact livenessprobe arguments. Resource limits are small (`csi-provisioner` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '300Mi'}; `liveness-probe` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'cpu': 1, 'memory': '100Mi'}; `smb` requests {'cpu': '10m', 'memory': '20Mi'} and limits {'memory': '200Mi'}), so noisy clusters can expose throttling or OOM behavior.

Test signals: `kubectl apply --dry-run=server`, rollout readiness for `deployment/csi-smb-controller`, leader-election Lease creation in `kube-system`, liveness `/healthz` success, controller metrics on 29644, successful dynamic PVC provisioning/deletion, and expansion tests when `csi-resizer` is included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-driver.yaml -->
# sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-driver.yaml

Purpose: Registers the SMB CSI driver with the Kubernetes storage API for v1.7.0. The object tells Kubernetes that `smb.csi.k8s.io` is a CSI driver, not an in-tree volume plugin.

Important APIs/types/functions: Declares `storage.k8s.io/v1` `CSIDriver/smb.csi.k8s.io`. The spec sets `attachRequired: false`, `podInfoOnMount: true`, and lifecycle modes not declared in this manifest version.

Control flow: Once applied, Kubernetes admission/scheduler/kubelet storage paths consult this object when handling PVC-backed and inline SMB CSI volumes. `attachRequired: false` bypasses the external-attacher path, so nodes mount SMB shares directly through the node plugin. `podInfoOnMount` makes pod metadata available to CSI `NodePublishVolume`, and lifecycle modes decide whether inline ephemeral volumes are advertised in addition to persistent volumes.

State/persistence: This is a persisted cluster-scoped API object with no pod runtime state. Its fields influence kubelet CSI calls, volume scheduling assumptions, and compatibility with the controller/node DaemonSets.

Dependencies and integration points: Integrates with the SMB controller Deployment, Linux and Windows node DaemonSets, StorageClasses, PVs/PVCs, and kubelet CSI plugin registration under the same driver name. The driver name must match the registrar socket registration path and SMB plugin identity.

Risks: A mismatched or missing `CSIDriver` can disable inline ephemeral support, cause Kubernetes to wait for attach operations that never exist, or omit pod context expected by the plugin. Lifecycle mode changes are cluster-contract changes and should be checked against supported Kubernetes versions.

Test signals: Server-side apply validation, `kubectl get csidriver smb.csi.k8s.io -o yaml`, inline ephemeral volume smoke tests when `Ephemeral` is present, and normal PVC pod mount tests using `driver: smb.csi.k8s.io`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-driver.yaml -->
