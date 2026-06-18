# subset-b-000354 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: Helm RBAC template for the latest CSI NFS chart. It creates controller and node ServiceAccounts when `serviceAccount.create` is true, and cluster-scoped provisioner/resizer roles when `rbac.create` is true.

Important APIs/types/functions: Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`; Helm values `.Values.serviceAccount.*`, `.Values.rbac.name`, `.Release.Namespace`, and `include "nfs.labels"`.

Control flow: Two top-level Helm gates render service accounts independently from RBAC. The provisioner role covers PV/PVC/storageclass/node/csinode/event/lease/secrets access plus snapshot API reads and VolumeSnapshotContent updates. A separate resizer role grants PV/PVC/status and event/lease access.

State and persistence: Persistent state is Kubernetes RBAC and service-account identity. No workload state is stored here.

Dependencies and integration points: Bound to the controller ServiceAccount used by `csi-nfs-controller.yaml`; permissions serve external-provisioner, csi-resizer, and snapshotter sidecars.

Risks: Cluster-wide RBAC is broad, especially PV mutation, secrets get, and snapshot content patch/update. Turning off service account creation requires matching pre-created names. Test signals: `helm template` with RBAC on/off and Kubernetes RBAC dry-run should verify all generated bindings.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

Purpose: Optional RBAC for deploying the upstream external snapshot-controller with this chart.

Important APIs/types/functions: Kubernetes `ServiceAccount`, `ClusterRole`, `ClusterRoleBinding`, namespaced `Role`, and `RoleBinding`; Helm values `.Values.externalSnapshotter.enabled`, `.Values.externalSnapshotter.name`, `.Values.externalSnapshotter.enabledDistributedSnapshotting`, `.Release.Namespace`, and `include "nfs.labels"`.

Control flow: The entire file renders only when `externalSnapshotter.enabled` is true. It creates a runner ClusterRole for PV/PVC/events and snapshot.storage.k8s.io resources, optionally adds node read permissions for distributed snapshotting, then adds cluster and namespace leader-election bindings.

State and persistence: Persists snapshot-controller identity and authorization; leader-election state itself is stored in `coordination.k8s.io` Leases at runtime.

Dependencies and integration points: Paired with `csi-snapshot-controller.yaml` and CRDs from `crd-csi-snapshot.yaml`.

Risks: This deploys a cluster-level controller that may duplicate a platform-installed snapshot-controller. Missing CRDs causes controller startup failure. Test signals: render with `externalSnapshotter.enabled` true/false and run server-side dry-run on clusters with snapshot CRDs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/snapshotclass.yaml

Purpose: Optional `VolumeSnapshotClass` template for NFS CSI snapshots.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass`; Helm values `.Values.volumeSnapshotClass.create`, `.Values.volumeSnapshotClass.name`, `.Values.volumeSnapshotClass.annotations`, `.Values.volumeSnapshotClass.deletionPolicy`, `.Values.driver.name`, and `include "nfs.labels"`.

Control flow: Renders only when `volumeSnapshotClass.create` is true. It writes metadata labels, optional annotations, the CSI driver name, and deletion policy.

State and persistence: Persists cluster-scoped snapshot class configuration used by VolumeSnapshot admission/controller logic. It does not hold snapshot data.

Dependencies and integration points: Requires snapshot CRDs and a controller-side CSI snapshotter. The `driver` must match the `CSIDriver` and CSI plugin name.

Risks: Incorrect default-class annotations or deletion policy can affect all matching snapshots. The template assumes snapshot APIs already exist or are installed by this chart. Test signals: render with and without annotations, then validate with `kubectl apply --dry-run=server`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/storageclass.yaml

Purpose: Optional StorageClass rendering for one legacy `storageClass` object plus a newer `storageClasses` list for multiple NFS classes.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass`; Helm `with`, `range`, `hasKey`, defaults, `.Values.driver.name`, `.Values.storageClass.*`, and `.Values.storageClasses`.

Control flow: First gate renders the single class when `storageClass.create` is true. A second gate ranges over `storageClasses`, rendering each with per-entry annotations, parameters, reclaim policy, binding mode, mount options, and configurable `allowVolumeExpansion`.

State and persistence: Persists cluster storage provisioning policy. Runtime PV/PVC state is created later by the external provisioner.

Dependencies and integration points: Consumed by PVCs and `csi-provisioner`; parameters such as `server`, `share`, `subDir`, and provisioner secrets drive NFS volume creation and deletion behavior.

Risks: Multiple default StorageClasses can cause ambiguous provisioning. Missing server/share parameters makes the class unusable. Test signals: template both modes and run server-side dry-run plus a PVC provisioning smoke test.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/values.yaml

Purpose: Default values for the latest/canary CSI NFS Helm chart.

Important APIs/types/functions: Helm values configure image repositories/tags, service accounts, RBAC, driver name, feature gates, kubelet paths, controller/node pod settings, external snapshotter, optional `VolumeSnapshotClass`, image pull secrets, one `storageClass`, and multiple `storageClasses`.

Control flow: Templates read these values to choose sidecar images, render optional resources, set scheduling policy, enable snapshotter and snapshot compression, propagate host mount options, and configure node-driver-registrar liveness options.

State and persistence: Values themselves are chart input; persisted state appears as rendered Kubernetes objects and workload pods.

Dependencies and integration points: Uses staging/canary NFS plugin and newer sidecars (`csi-provisioner`, `csi-resizer`, `csi-snapshotter`, livenessprobe, registrar, snapshot-controller). `baseRepo` combines with repositories beginning with `/`.

Risks: Canary images are not release-pinned. Feature defaults can install privileged host-mounted pods and cluster-wide RBAC. Test signals: `helm lint`, `helm template`, image reference checks, and install/upgrade tests with snapshot/storage class options.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/Chart.yaml

Purpose: Helm chart metadata for CSI NFS chart release v2.0.0.

Important APIs/types/functions: Helm v1 chart fields `apiVersion`, `appVersion`, `description`, `name`, and `version`.

Control flow: There is no runtime control flow; Helm uses this metadata for packaging, dependency resolution, install history, and repository indexes.

State and persistence: Persists only as chart package metadata and release metadata after install.

Dependencies and integration points: Links the template set under the v2.0.0 chart to application version `v2.0.0`.

Risks: v2 uses older Kubernetes manifests such as `storage.k8s.io/v1beta1` CSIDriver in its templates, so chart metadata alone may look installable on clusters where rendered APIs are removed. Test signals: `helm lint`, package index validation, and install dry-run against target Kubernetes versions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: Controller Deployment for v2.0.0 CSI NFS.

Important APIs/types/functions: Kubernetes `apps/v1` `Deployment`; containers `csi-provisioner`, `liveness-probe`, and privileged `nfs`; Helm image/resource values and `include "nfs.labels"`.

Control flow: The deployment runs two replicas by default, selects Linux nodes, starts provisioner against `/csi/csi.sock`, probes the NFS CSI endpoint, and runs the NFS driver with node id and Unix socket endpoint.

State and persistence: Uses hostPath mounts for kubelet plugin and pod directories plus an emptyDir socket directory. Runtime state is CSI socket files, mounts, and provisioned PV/PVC objects.

Dependencies and integration points: Requires controller RBAC/service account, kubelet host paths, NFS CSI image, and external-provisioner.

Risks: Privileged container with `SYS_ADMIN`, hostPath access, hard-coded kubelet path, and Recreate/replica interactions can affect availability. Test signals: render/install smoke, provision a PVC, and inspect liveness endpoint.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes for v2.0.0.

Important APIs/types/functions: `storage.k8s.io/v1beta1` `CSIDriver` named `nfs.csi.k8s.io`; fields `attachRequired: false`, `volumeLifecycleModes: Persistent`, and `podInfoOnMount: true`.

Control flow: Static manifest, no Helm gates. The object tells Kubernetes the driver does not require attach/detach and only handles persistent volumes.

State and persistence: Persists cluster-scoped driver metadata used by kubelet and storage controllers.

Dependencies and integration points: Name must match `--drivername` arguments in controller/node pods and StorageClass provisioner fields.

Risks: `v1beta1` CSIDriver is unsupported on newer Kubernetes releases. Static driver name cannot be customized in this version. Test signals: server-side dry-run against supported clusters and CSI node registration smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: Node DaemonSet for v2.0.0 CSI NFS.

Important APIs/types/functions: Kubernetes `DaemonSet`; containers `node-driver-registrar` and privileged `nfs`; hostPath volumes for plugin, pods, and plugin registry.

Control flow: Runs on every Linux node using host networking. The registrar removes stale registration files in a lifecycle hook, registers `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, and the NFS container exposes the CSI endpoint.

State and persistence: Persists socket/registration artifacts and bidirectional pod mount propagation through kubelet host paths.

Dependencies and integration points: Integrates with kubelet plugin registration and per-node volume mount/unmount operations.

Risks: Hard-coded kubelet paths, privileged hostPath access, and no separate node service account in this version. Test signals: DaemonSet readiness, `CSINode` entries, and pod volume mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: Controller service account and external-provisioner RBAC for v2.0.0.

Important APIs/types/functions: Optional `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`; Helm gates `.Values.serviceAccount.create` and `.Values.rbac.create`; fixed names `csi-nfs-controller-sa`, `nfs-external-provisioner-role`, and `nfs-csi-provisioner-binding`.

Control flow: Service account creation and RBAC creation are independently gated. The role grants PV create/delete, PVC update, StorageClass/CSINode/node reads, events mutation, and lease access for leader election.

State and persistence: Persists authorization and identity for the controller Deployment.

Dependencies and integration points: Bound to `csi-nfs-controller.yaml` and external-provisioner leader election.

Risks: Fixed names complicate multi-release installs. No secrets permission exists, so StorageClass provisioner-secret workflows may not work. Test signals: render with gates toggled and provisioner startup/RBAC error checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/values.yaml

Purpose: Minimal default configuration for the v2.0.0 CSI NFS chart.

Important APIs/types/functions: Image repository/tag/pullPolicy for NFS plugin, external-provisioner, livenessprobe, and node-driver-registrar; booleans `serviceAccount.create` and `rbac.create`; `controller.replicas`.

Control flow: Templates consume these values for image references, controller replica count, and optional service account/RBAC rendering.

State and persistence: Values drive rendered Kubernetes resources but are not runtime state themselves.

Dependencies and integration points: All repositories are under `k8s.gcr.io/sig-storage`, matching the era of v2 sidecars.

Risks: Sparse configurability leaves kubelet paths, names, scheduling, RBAC names, and driver name hard-coded. Registry migration from `k8s.gcr.io` may affect pulls. Test signals: `helm template` with custom image tags and install smoke on a compatible Kubernetes version.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v3.0.0.

Important APIs/types/functions: Helm v1 chart fields with `appVersion: v3.0.0`, `name: csi-driver-nfs`, and `version: v3.0.0`.

Control flow: Static packaging metadata; Helm reads it during chart install/package/index operations.

State and persistence: Stored in chart package and Helm release history.

Dependencies and integration points: Associates the v3.0.0 templates with the v3 NFS plugin and sidecar defaults.

Risks: Still uses chart API v1, and install compatibility depends on rendered templates rather than metadata. Test signals: `helm lint`, repository index validation, and dry-run install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v3.0.0 controller Deployment for dynamic NFS provisioning.

Important APIs/types/functions: `Deployment`; containers `csi-provisioner`, `liveness-probe`, `nfs`; values for names, service account, replicas, tolerations, resources, log level, and images.

Control flow: Host-networked controller runs on Linux, optionally tolerates control-plane taints, starts provisioner with leader election and extra metadata, probes the CSI socket, and starts the NFS driver with `--drivername` and liveness endpoint.

State and persistence: Uses emptyDir socket and hostPath kubelet pod mount. Persistent cluster state is created by sidecars as PVs/PVC updates/events/leases.

Dependencies and integration points: Requires RBAC, CSIDriver object, and kubelet pod path access for NFS directory operations.

Risks: Privileged `SYS_ADMIN` container, hostNetwork DNS assumptions, and no configurable kubelet path. Test signals: leader election lease, liveness probe, and PVC create/delete workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: Registers the v3.0.0 CSI NFS driver using the GA CSIDriver API.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; values `.Values.driver.name` and `.Values.feature.enableFSGroupPolicy`.

Control flow: Static object with optional `fsGroupPolicy: File` when enabled. It declares `attachRequired: false` and persistent lifecycle mode.

State and persistence: Cluster-scoped CSIDriver metadata governs kubelet/storage-controller handling.

Dependencies and integration points: Must match controller/node `--drivername` and StorageClass provisioner name.

Risks: FSGroup behavior can change ownership/mode semantics for mounted volumes; default v3.0.0 values disable it. Test signals: server-side dry-run and pod mount tests with/without fsGroup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v3.0.0 node plugin DaemonSet.

Important APIs/types/functions: `DaemonSet`; livenessprobe, node-driver-registrar, and privileged NFS containers; values for node name, update strategy, tolerations, resources, log level, and image tags.

Control flow: Runs host-networked on Linux nodes. The registrar has a liveness probe using kubelet-registration-probe mode and registers the CSI socket; NFS serves the node CSI endpoint and mounts through bidirectional kubelet pod paths.

State and persistence: HostPath socket directory, plugin registry, and pod mount directory persist on each node.

Dependencies and integration points: Kubelet plugin registration, CSINode updates, and NFS mount lifecycle.

Risks: Hard-coded `/var/lib/kubelet`, privileged mount propagation, and cluster-wide DaemonSet blast radius. Test signals: DaemonSet rollout, kubelet registration, and workload pod using an NFS PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: v3.0.0 configurable controller RBAC and ServiceAccount.

Important APIs/types/functions: `ServiceAccount`, `ClusterRole`, `ClusterRoleBinding`; values `.Values.rbac.name`, `.Values.serviceAccount.create`, `.Values.rbac.create`, and `.Release.Namespace`.

Control flow: Creates a name-derived controller service account and external-provisioner ClusterRole when enabled. Permissions include PV/PVC/storageclass/event/csinode/node/lease access for provisioning and leader election.

State and persistence: Service account identity and cluster RBAC bindings persist until Helm uninstall.

Dependencies and integration points: Used by controller Deployment serviceAccountName and external-provisioner sidecar.

Risks: Name templating improves multi-release support but still grants cluster-wide PV/PVC authority. Secrets access is absent, limiting StorageClass secret workflows. Test signals: render with custom `rbac.name`, check binding subject, and run provisioner RBAC smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/values.yaml

Purpose: Default values for v3.0.0 chart.

Important APIs/types/functions: Image tags, serviceAccount/controller name, RBAC name, controller/node names and resources, tolerations, health ports, driver name, FSGroup feature flag, and image pull secrets.

Control flow: Values parameterize controller/node Deployments, RBAC naming, CSIDriver options, images, resources, and liveness ports.

State and persistence: Rendered resources persist in Kubernetes; values are Helm input and release configuration.

Dependencies and integration points: Moves to explicit controller/node naming and `registry.k8s.io`-era sidecar repositories from older defaults.

Risks: `enableFSGroupPolicy` default false may surprise users expecting fsGroup support; kubelet path remains hard-coded. Test signals: `helm template` with custom service account/RBAC names and node/controller rollout checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v3.1.0.

Important APIs/types/functions: Static Helm chart fields `apiVersion: v1`, `appVersion: v3.1.0`, `description`, `name`, and `version`.

Control flow: No runtime control flow; consumed by Helm package/install/index commands.

State and persistence: Stored in packaged chart and Helm release metadata.

Dependencies and integration points: Identifies the v3.1.0 template/value set, which adds inline-volume and mount-permission options relative to prior versions.

Risks: Metadata does not express Kubernetes API compatibility. Test signals: chart lint/package and dry-run install against target clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v3.1.0 controller Deployment, extending v3.0.0 with mount permission and working mount directory controls.

Important APIs/types/functions: `Deployment`; sidecars `csi-provisioner` and `liveness-probe`; NFS driver args `--mount-permissions` and `--working-mount-dir`; controller values and resources.

Control flow: Renders host-networked controller pods on Linux with optional master toleration. Sidecars share `/csi/csi.sock`; NFS container mounts kubelet pods and serves the CSI endpoint with configured driver and permission behavior.

State and persistence: HostPath pod mounts plus emptyDir socket. Dynamic state appears as PV/PVCs, events, and leader-election leases.

Dependencies and integration points: Integrates with RBAC, CSIDriver, external-provisioner, and kubelet pod directories.

Risks: Privileged hostPath mount with configurable permissions can over-open NFS directories if set broadly. Test signals: PVC lifecycle and permission checks on created subdirectories.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v3.1.0 CSIDriver registration with optional inline ephemeral volume support.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; values `.Values.driver.name`, `.Values.feature.enableInlineVolume`, and `.Values.feature.enableFSGroupPolicy`.

Control flow: Always emits `Persistent` lifecycle mode. Adds `Ephemeral` mode when inline volume support is enabled and adds `fsGroupPolicy: File` when FSGroup support is enabled.

State and persistence: Persists driver capabilities in cluster storage API state.

Dependencies and integration points: Must align with node/controller driver flags and kubelet support for CSI inline volumes.

Risks: Advertising unsupported `Ephemeral` behavior could let pods request inline NFS volumes that the driver or cluster cannot satisfy. Test signals: dry-run, CSIDriver inspection, fsGroup mount test, and optional inline volume pod test.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v3.1.0 node DaemonSet with mount-permission support.

Important APIs/types/functions: `DaemonSet`; containers livenessprobe, node-driver-registrar, NFS; NFS arg `--mount-permissions`; hostPath socket, pod, and registration volumes.

Control flow: Host-networked Linux DaemonSet registers the CSI socket with kubelet, probes health, and runs the NFS node service. Socket and pod mounts use bidirectional propagation.

State and persistence: Per-node socket and registration files under kubelet directories, plus mounted NFS volume state under pod paths.

Dependencies and integration points: Kubelet plugin registry, CSINode, CSIDriver, and StorageClass/PVC volume consumers.

Risks: Hard-coded kubelet path and privileged mount access remain. Mount permission defaults in values are octal-like and should be validated after rendering. Test signals: rollout, registration probe, and mounted file mode checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: v3.1.0 controller RBAC, adding secrets read access to the v3 provisioner role.

Important APIs/types/functions: Optional `ServiceAccount`, `ClusterRole`, `ClusterRoleBinding`; value-derived names from `.Values.rbac.name`.

Control flow: When enabled, creates the controller service account and a ClusterRole with PV/PVC/storageclass/event/csinode/node/lease permissions plus `secrets get`.

State and persistence: Persists cluster authorization for controller sidecars.

Dependencies and integration points: Enables provisioner secret use for StorageClass mount options and deletion workflows.

Risks: Secret read is cluster-wide in the role, so least-privilege deployments may need tighter custom RBAC. Test signals: render with `rbac.create` toggled and exercise StorageClass secret parameters.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/values.yaml

Purpose: Default values for v3.1.0 chart.

Important APIs/types/functions: Image tags, serviceAccount/RBAC names, driver name and `mountPermissions`, feature flags for FSGroup and inline volume, controller working mount directory, node/controller resources and tolerations, imagePullSecrets.

Control flow: Templates consume values to render names, images, resources, driver capabilities, mount permissions, and controller working directory.

State and persistence: Values become Helm release configuration and rendered workload/RBAC objects.

Dependencies and integration points: Bridges chart settings to NFS driver flags and Kubernetes CSIDriver capability fields.

Risks: `mountPermissions: 0777` is permissive and may be parsed differently by YAML tooling if not handled consistently. Test signals: render values into driver args and validate created volume permissions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v4.0.0.

Important APIs/types/functions: Helm `apiVersion: v1`, `appVersion: v4.0.0`, `description`, `name`, and `version: v4.0.0`.

Control flow: Static metadata only.

State and persistence: Chart and Helm release metadata.

Dependencies and integration points: Marks the v4.0.0 template generation that introduces kubeletDir and FSGroup default changes.

Risks: Uses older chart API metadata while templates target modern Kubernetes APIs. Test signals: `helm lint`, package validation, and rendered manifest dry-run.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v4.0.0 controller Deployment with configurable `kubeletDir` and DNS policy.

Important APIs/types/functions: `Deployment`; Helm values `.Values.kubeletDir`, `.Values.controller.dnsPolicy`, `.Values.driver.mountPermissions`, resources, and images.

Control flow: Renders a host-networked Linux controller using a value-driven service account and DNS policy. Provisioner and liveness sidecars share the CSI socket; the NFS container mounts `${kubeletDir}/pods` and uses working mount directory and mount permission args.

State and persistence: HostPath pod mount and emptyDir socket; cluster state through sidecars.

Dependencies and integration points: Controller RBAC, CSIDriver, external-provisioner, livenessprobe, and kubelet pod directory.

Risks: `hostNetwork` with configurable DNS requires correct `dnsPolicy`; wrong `kubeletDir` breaks mounts. Test signals: render with non-default kubeletDir and run PVC provisioning on target node layout.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v4.0.0 CSIDriver manifest.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; `.Values.driver.name`, `.Values.feature.enableInlineVolume`, `.Values.feature.enableFSGroupPolicy`.

Control flow: Emits persistent lifecycle mode, optional ephemeral lifecycle mode, optional `fsGroupPolicy: File`, and `attachRequired: false`.

State and persistence: Cluster-scoped driver capability state.

Dependencies and integration points: Must match driver flags and StorageClass provisioner references.

Risks: Default FSGroup changed to enabled in v4 values, which can change volume ownership handling. Test signals: dry-run, CSIDriver inspection, fsGroup workload test.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v4.0.0 node DaemonSet with configurable kubelet directory.

Important APIs/types/functions: `DaemonSet`; `.Values.kubeletDir`, `.Values.controller.dnsPolicy`, node liveness/registrar/NFS containers, hostPath volumes.

Control flow: Host-networked node pods run on Linux, register `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`, mount `${kubeletDir}/pods`, and expose the NFS CSI endpoint with mount-permissions.

State and persistence: Per-node socket, registry, and pod mount state under the configured kubelet directory.

Dependencies and integration points: Kubelet plugin registry, CSIDriver, workload pod mounts.

Risks: Template uses controller DNS policy for node pod DNS; wrong kubeletDir or missing plugin registry directory breaks registration. Test signals: DaemonSet rollout and kubelet registration on custom kubeletDir clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml

Purpose: v4.0.0 controller RBAC for provisioning.

Important APIs/types/functions: Optional ServiceAccount, ClusterRole, ClusterRoleBinding; value-derived names; PV/PVC/storageclass/event/csinode/node/lease/secrets permissions.

Control flow: Service account and RBAC render behind independent values gates. The binding targets `csi-{{ .Values.rbac.name }}-controller-sa`.

State and persistence: Kubernetes service account and cluster RBAC.

Dependencies and integration points: Controller Deployment and provisioner sidecar.

Risks: Cluster-wide secret get remains broad, and no node service account is created in this older v4 file. Test signals: render and dry-run with RBAC gates and custom rbac name.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/values.yaml

Purpose: Default v4.0.0 chart values.

Important APIs/types/functions: `customLabels`, image settings, service account/RBAC names, driver `mountPermissions`, FSGroup/inline feature flags, `kubeletDir`, controller/node DNS policy, resources, tolerations, and imagePullSecrets.

Control flow: Values render image refs, scheduling, kubelet hostPath locations, CSIDriver features, service accounts/RBAC, and pod resources.

State and persistence: Helm release configuration and rendered Kubernetes resources.

Dependencies and integration points: Adds `kubeletDir` as a central integration point for node and controller templates.

Risks: Default `mountPermissions: 0777` and enabled FSGroup can alter security posture. `dnsPolicy: Default` with hostNetwork may not resolve cluster services. Test signals: render with kubeletDir override and validate DNS/PVC workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v4.1.0.

Important APIs/types/functions: Helm chart fields `apiVersion`, `appVersion: v4.1.0`, `description`, `name`, and `version`.

Control flow: Static packaging metadata.

State and persistence: Stored in chart packages and Helm release metadata.

Dependencies and integration points: Identifies the v4.1.0 templates that add node service-account creation and scheduling customization.

Risks: Metadata compatibility must be checked against rendered objects. Test signals: `helm lint`, package index check, and install dry-run.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v4.1.0 controller Deployment with affinity/nodeSelector customization.

Important APIs/types/functions: `Deployment`; Helm `tpl`/`contains` affinity branch, values for `runOnControlPlane`, `runOnMaster`, `controller.affinity`, `controller.nodeSelector`, DNS policy, service account, images, and resources.

Control flow: If explicit affinity contains nodeSelectorTerms it is used; otherwise run-on-control-plane/master booleans synthesize required node affinity. The pod then runs provisioner, liveness, and privileged NFS containers.

State and persistence: Kubelet pod hostPath and CSI socket; cluster PV/PVC/event/lease state through sidecars.

Dependencies and integration points: RBAC, CSIDriver, node scheduling labels/taints, kubeletDir.

Risks: String-based affinity detection is fragile. Scheduling booleans do not apply when custom affinity is set. Test signals: render each scheduling branch and run Helm unit/dry-run checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v4.1.0 CSIDriver registration.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; driver name and feature gates for inline volumes and FSGroup policy.

Control flow: Same GA CSIDriver flow as v4.0.0: persistent mode always, optional ephemeral mode, optional `fsGroupPolicy: File`.

State and persistence: Cluster driver capability state.

Dependencies and integration points: Controller/node driver `--drivername`, StorageClass provisioner, kubelet volume handling.

Risks: Capability flags must match actual driver support and target Kubernetes version. Test signals: server-side dry-run and workload tests for fsGroup and optional inline volumes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v4.1.0 node DaemonSet with service account and scheduling customization.

Important APIs/types/functions: `DaemonSet`; value-driven affinity/nodeSelector/tolerations/resources, `kubeletDir`, node service account, registrar/liveness/NFS containers.

Control flow: Runs host-networked on Linux using `serviceAccountName: csi-nfs-node-sa`, optional affinity and nodeSelector, then registers and serves the CSI socket under the configured kubelet directory.

State and persistence: Node-local hostPath socket/registration/mount state.

Dependencies and integration points: Node service account from `rbac-csi-nfs.yaml`, kubelet plugin registry, host NFS mount configuration.

Risks: ServiceAccount name is literal in this version, so custom `serviceAccount.node` is not available. Privileged mount access remains. Test signals: render node SA and DaemonSet together, check registration and PVC mount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: Consolidated v4.1.0 RBAC template creating both controller and node service accounts plus controller provisioner RBAC.

Important APIs/types/functions: Optional ServiceAccounts, ClusterRole, ClusterRoleBinding; `.Values.rbac.name`, `.Values.serviceAccount.create`, `.Values.rbac.create`, and namespace.

Control flow: Service-account gate creates `csi-<rbac.name>-controller-sa` and `csi-<rbac.name>-node-sa`. RBAC gate creates one external-provisioner role and binds it to the controller account.

State and persistence: Service account identities and cluster authorization.

Dependencies and integration points: Controller and node pod serviceAccountName fields; provisioner sidecar.

Risks: The node service account receives no explicit RBAC here, which is usually fine for node plugin but should be verified. Controller binding does not cover resizer/snapshotter because those sidecars are not present yet. Test signals: render custom `rbac.name` and confirm pod service accounts match.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/values.yaml

Purpose: v4.1.0 default chart values.

Important APIs/types/functions: Images, serviceAccount controller name, RBAC name, driver features, kubeletDir, controller/node DNS, affinity, nodeSelector, tolerations, resources, and image pull secrets.

Control flow: Values drive image references, labels, scheduling, host paths, driver args, CSIDriver features, and RBAC/service account rendering.

State and persistence: Helm release configuration and rendered Kubernetes state.

Dependencies and integration points: Introduces control-plane scheduling flags and affinity/nodeSelector inputs for controller and node workloads.

Risks: `serviceAccount.node` is absent though the template creates a node account from `rbac.name`, limiting customization. Defaults still use `mountPermissions: 0777`. Test signals: render custom affinity/nodeSelector and verify pod placement.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart v4.10.0.

Important APIs/types/functions: Helm v1 chart fields with `appVersion: v4.10.0` and `version: v4.10.0`.

Control flow: Static metadata used by Helm packaging and install history.

State and persistence: Chart/release metadata only.

Dependencies and integration points: Identifies the richer v4.10.0 chart set including resizer, snapshotter, snapshot CRDs, StorageClass, and VolumeSnapshotClass templates.

Risks: The `v` prefix differs from later v4.11.0/v4.12.0 metadata and may matter for tooling that parses semver strictly. Test signals: `helm lint`, package index validation, and dry-run install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

Purpose: Optional bundled snapshot.storage.k8s.io CRDs for VolumeSnapshot, VolumeSnapshotClass, and VolumeSnapshotContent.

Important APIs/types/functions: `apiextensions.k8s.io/v1` `CustomResourceDefinition`; Helm gate `and .Values.externalSnapshotter.enabled .Values.externalSnapshotter.customResourceDefinitions.enabled`; annotations `api-approved.kubernetes.io` and `helm.sh/resource-policy: keep`.

Control flow: When enabled, renders CRD schemas generated by controller-gen v0.8.0. Each CRD defines group, names, scope, printer columns, OpenAPI schema, status subresource, and served/storage flags.

State and persistence: CRDs are cluster-scoped API extensions and are kept on Helm uninstall due to resource-policy keep. They enable persistent VolumeSnapshot* custom resources.

Dependencies and integration points: Required by `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, `snapshotclass.yaml`, and the CSI snapshotter sidecar.

Risks: Installing CRDs from an application chart can conflict with cluster-managed snapshot CRDs or versions. Kept CRDs leave lifecycle outside Helm. Test signals: server-side dry-run, CRD version comparison, and snapshot creation smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v4.10.0 controller Deployment including provisioner, resizer, optional CSI snapshotter, liveness probe, and NFS driver.

Important APIs/types/functions: `Deployment`; sidecars `csi-provisioner`, `csi-resizer`, `csi-snapshotter`, `liveness-probe`, `nfs`; values for image `baseRepo`, strategy, snapshotter, tar snapshots, default on-delete policy, scheduling, resources, and security contexts.

Control flow: Host-networked controller uses scheduling branch logic, then starts sidecars against `/csi/csi.sock`. Snapshotter container renders only when `controller.enableSnapshotter` is true. NFS driver receives mount permissions, working dir, delete policy, and tar snapshot flags.

State and persistence: PV/PVC resize/provision/snapshot state, leases, events, CSI socket, and host pod mounts.

Dependencies and integration points: Requires RBAC including resizer and snapshot permissions, snapshot CRDs for snapshot workflows, and kubelet host paths.

Risks: Privileged host mounts, leader election, image repository composition, and snapshot flags require integration testing. Test signals: PVC create/delete/resize and VolumeSnapshot workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v4.10.0 CSIDriver manifest.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; driver name plus inline-volume and FSGroup feature gates.

Control flow: Renders persistent lifecycle mode, optional ephemeral mode, optional `fsGroupPolicy: File`, and `attachRequired: false`.

State and persistence: Cluster-scoped CSI driver capability object.

Dependencies and integration points: Must match StorageClasses, snapshot classes, and controller/node driver args.

Risks: Capability mismatch can cause kubelet scheduling/mount failures. Test signals: dry-run and workload mount tests for fsGroup/inline options.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v4.10.0 node DaemonSet with optional host NFS mount option propagation.

Important APIs/types/functions: `DaemonSet`; livenessprobe, node-driver-registrar, NFS containers; values for serviceAccount.node, image baseRepo composition, dnsPolicy, resources, kubeletDir, and `.Values.feature.propagateHostMountOptions`.

Control flow: Host-networked Linux pods register the CSI socket, run liveness checks, and serve node CSI. When host mount option propagation is enabled, `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d` are mounted into the NFS container.

State and persistence: Node socket/registration/pod mount state plus optional host NFS configuration mounts.

Dependencies and integration points: Kubelet, node service account, CSIDriver, and host NFS client config.

Risks: Mounting host NFS config can couple pod behavior to node drift. Privileged NFS container remains high risk. Test signals: node rollout, registration, and mount option propagation test.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

Purpose: Optional Deployment for the external snapshot-controller.

Important APIs/types/functions: `apps/v1` `Deployment`; Helm gate `.Values.externalSnapshotter.enabled`; values for name, labels, annotations, replicas, priority class, resources, image, imagePullSecrets, and controller scheduling.

Control flow: Renders only when enabled. It creates a rolling-update Deployment with `minReadySeconds: 15`, Linux nodeSelector, optional controller affinity/tolerations, leader election args, and a security context dropping all capabilities.

State and persistence: Controller runtime state is leader-election leases and updates to VolumeSnapshot* resources.

Dependencies and integration points: Requires snapshot CRDs and RBAC from `rbac-snapshot-controller.yaml`.

Risks: Duplicates platform snapshot-controller if one already exists; uses controller scheduling values instead of separate snapshotter scheduling knobs. Test signals: render enabled/disabled and create a VolumeSnapshot.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: v4.10.0 RBAC for CSI NFS controller/node identities, provisioner, resizer, and snapshot sidecar interactions.

Important APIs/types/functions: ServiceAccounts from `.Values.serviceAccount.controller` and `.Values.serviceAccount.node`; provisioner/resizer ClusterRoles and ClusterRoleBindings; snapshot API permissions.

Control flow: Service account creation is gated separately from RBAC. The provisioner role includes PV create/patch/delete, PVC update, storage class reads, snapshot reads/content updates/status updates, events, csinodes, nodes, leases, and secrets get. Resizer role handles PV/PVC/status/events/leases.

State and persistence: Cluster RBAC and service-account identities.

Dependencies and integration points: Controller Deployment sidecars depend on these permissions for provisioning, resizing, and snapshots.

Risks: Broad cluster-scoped rights and secrets read; RBAC does not gate snapshot permissions on snapshotter enablement. Test signals: sidecar startup logs, resize, provision, and snapshot authorization tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

Purpose: v4.10.0 optional RBAC for the external snapshot-controller.

Important APIs/types/functions: Snapshot-controller ServiceAccount, runner ClusterRole/Binding, namespaced leader-election Role/Binding, and optional node read permission for distributed snapshotting.

Control flow: Entire file is gated by `externalSnapshotter.enabled`. It grants read/update/create/delete/patch permissions across VolumeSnapshot, VolumeSnapshotContent, VolumeSnapshotClass, PVCs, PVs, events, and leases.

State and persistence: Cluster authorization and leader-election namespace authorization.

Dependencies and integration points: Used by `csi-snapshot-controller.yaml`; requires snapshot CRDs.

Risks: Cluster-wide snapshot controller permissions can conflict with existing controller installations. Test signals: enabled render, RBAC dry-run, and snapshot reconciliation smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/snapshotclass.yaml

Purpose: v4.10.0 optional VolumeSnapshotClass.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass`; values `.Values.volumeSnapshotClass.create`, `.name`, `.deletionPolicy`, and `.Values.driver.name`.

Control flow: Renders only when create is true. Emits name, driver, and deletion policy without labels or annotations in this version.

State and persistence: Cluster-scoped snapshot class used by VolumeSnapshots.

Dependencies and integration points: Snapshot CRDs, snapshot-controller, and NFS CSI snapshotter.

Risks: No annotation support limits default class declaration. Wrong deletion policy affects snapshot content retention. Test signals: render true/false and create/delete VolumeSnapshot using the class.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/storageclass.yaml

Purpose: v4.10.0 optional single StorageClass template.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass`; values `.Values.storageClass.create`, `.name`, `.annotations`, `.parameters`, `.reclaimPolicy`, `.volumeBindingMode`, `.mountOptions`, and `.Values.driver.name`.

Control flow: Renders only when `storageClass.create` is true. It always sets `allowVolumeExpansion: true` and includes optional parameters and mountOptions.

State and persistence: Cluster-scoped provisioning policy for PVCs.

Dependencies and integration points: External provisioner and resizer; parameters identify NFS server/share/subDir and optional provisioner secrets.

Risks: Empty annotations block can render even when no annotations are provided. Missing parameters make provisioning fail. Test signals: render with sample NFS parameters and create/resize a PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/values.yaml

Purpose: Default values for v4.10.0 chart.

Important APIs/types/functions: Image baseRepo and sidecar tags, controller/node service accounts, RBAC name, driver, feature gates, kubeletDir, controller snapshotter/resizer settings, external snapshotter, optional CRDs/classes, and StorageClass example.

Control flow: Values enable snapshotter by default inside the CSI controller but disable standalone externalSnapshotter and optional classes by default. They configure host networking, priority classes, resources, default delete policy, tar snapshot behavior, and host mount option propagation.

State and persistence: Helm configuration; rendered workloads/RBAC/CRDs/classes persist in cluster.

Dependencies and integration points: Coordinates csi-provisioner v5.2.0, csi-resizer v1.13.1, snapshotter v8.2.0, and NFS plugin v4.10.0.

Risks: Snapshot sidecar enabled while CRDs/external controller are optional requires cluster preconditions. Test signals: render with default and full snapshot/storage options.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart 4.11.0.

Important APIs/types/functions: Helm chart fields with `appVersion: 4.11.0` and `version: 4.11.0` without the earlier `v` prefix.

Control flow: Static metadata used by Helm.

State and persistence: Chart package and Helm release metadata.

Dependencies and integration points: Identifies the 4.11.0 chart content, which is largely identical to v4.10.0 except image/tag metadata.

Risks: Version string format changed from `v4.10.0`; automation expecting a leading `v` can break. Test signals: package/index validation and upgrade dry-run from v4.10.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

Purpose: Optional snapshot CRD bundle for chart 4.11.0.

Important APIs/types/functions: Same `apiextensions.k8s.io/v1` CRD set as v4.10.0 for VolumeSnapshot, VolumeSnapshotClass, and VolumeSnapshotContent; gated by `externalSnapshotter.enabled` and `customResourceDefinitions.enabled`; `helm.sh/resource-policy: keep`.

Control flow: When both values are true, renders the CRD OpenAPI schemas, printer columns, status subresources, names, group, and version metadata.

State and persistence: Adds/updates cluster API extensions and persists them after uninstall due to keep policy.

Dependencies and integration points: Required by snapshot class/controller and CSI snapshotter workflows.

Risks: CRD ownership conflicts with cluster-managed CSI snapshot CRDs; kept resources complicate rollback. Test signals: compare existing CRD versions before install, then server-side dry-run and snapshot smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: 4.11.0 controller Deployment with provisioner, resizer, optional snapshotter, liveness probe, and NFS plugin.

Important APIs/types/functions: Same template structure as v4.10.0; values drive strategy, images, service account, scheduling, resources, snapshot flags, and NFS driver arguments.

Control flow: Host-networked pod uses controller affinity logic, starts sidecars against the CSI socket, conditionally includes `csi-snapshotter`, and runs privileged NFS with mount/delete/snapshot options.

State and persistence: CSI socket, host pod mounts, PV/PVC/VolumeSnapshot state, events, and leases.

Dependencies and integration points: RBAC, CSIDriver, kubeletDir, sidecar image versions, and optional snapshot APIs.

Risks: Same operational risks as v4.10.0, with image tag bump to NFS plugin 4.11.0. Test signals: upgrade smoke, provision/resize/snapshot workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: 4.11.0 CSIDriver registration.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; driver name and feature gates for inline volumes and FSGroup policy.

Control flow: Emits `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle, and optional File FSGroup policy.

State and persistence: Cluster-scoped driver capabilities.

Dependencies and integration points: Must match NFS controller/node `--drivername`, StorageClass provisioner, and VolumeSnapshotClass driver.

Risks: Incorrectly advertised lifecycle or FSGroup support causes runtime mount or scheduling issues. Test signals: dry-run plus pod mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: 4.11.0 node DaemonSet.

Important APIs/types/functions: Same structure as v4.10.0: livenessprobe, node-driver-registrar, privileged NFS, kubeletDir hostPaths, serviceAccount.node, image baseRepo handling, and optional host NFS config mounts.

Control flow: Host-networked Linux DaemonSet registers the CSI socket, provides health checks, and runs node mount service. Host NFS config mounts render only when propagation feature is true.

State and persistence: Node-local socket, registration, and pod mount state.

Dependencies and integration points: Kubelet plugin registry, CSIDriver, node RBAC identity, and host NFS client config.

Risks: Privileged hostPath access and optional host config propagation. Test signals: rollout, kubelet registration, mount/unmount workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

Purpose: Optional external snapshot-controller Deployment for 4.11.0.

Important APIs/types/functions: `Deployment` gated by `.Values.externalSnapshotter.enabled`; snapshot-controller image settings, replicas, labels/annotations, priority class, resources, imagePullSecrets, and controller scheduling values.

Control flow: Renders a Linux Deployment with leader election args and `minReadySeconds: 15`; optional affinity/tolerations follow controller settings.

State and persistence: Runtime leader-election leases and updates to VolumeSnapshot resources.

Dependencies and integration points: Snapshot CRDs and RBAC snapshot-controller template.

Risks: Can duplicate an existing cluster snapshot-controller and uses shared controller scheduling knobs. Test signals: enabled render, controller startup, and VolumeSnapshot reconcile.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

Purpose: 4.11.0 RBAC for NFS CSI controller and node service accounts plus provisioner/resizer roles.

Important APIs/types/functions: ServiceAccount, ClusterRole, ClusterRoleBinding; values `.Values.serviceAccount.controller`, `.Values.serviceAccount.node`, `.Values.rbac.name`.

Control flow: Same as v4.10.0: service accounts gate independently from RBAC; provisioner role includes provisioning and snapshot permissions; resizer role covers resize/status/event/lease permissions.

State and persistence: Service-account identities and cluster RBAC.

Dependencies and integration points: Controller Deployment sidecars and node DaemonSet identity.

Risks: Broad cluster permissions and unconditional snapshot API permissions. Test signals: RBAC dry-run, provisioner/resizer/snapshot sidecar startup, PVC resize smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

Purpose: 4.11.0 optional RBAC for external snapshot-controller.

Important APIs/types/functions: ServiceAccount, runner ClusterRole/Binding, leader-election Role/Binding; optional distributed snapshotting node reads.

Control flow: Rendered only when `externalSnapshotter.enabled` is true. Grants snapshot-controller authority over VolumeSnapshot*, PV/PVC/event resources and lease objects.

State and persistence: Cluster and namespace RBAC; runtime lease state is created by controller.

Dependencies and integration points: `csi-snapshot-controller.yaml` and snapshot CRDs.

Risks: Duplicate cluster-level snapshot controller and broad snapshot mutation permissions. Test signals: render enabled and run snapshot create/delete smoke.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/snapshotclass.yaml

Purpose: 4.11.0 optional VolumeSnapshotClass.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass`; values for create flag, name, deletionPolicy, and driver name.

Control flow: Renders only when `volumeSnapshotClass.create` is true and emits name, driver, and deletionPolicy.

State and persistence: Cluster-scoped snapshot class policy.

Dependencies and integration points: Snapshot CRDs, snapshot-controller, CSI snapshotter, and matching driver name.

Risks: No labels/annotations in this version; deletion policy mistakes affect backend snapshot retention. Test signals: dry-run and VolumeSnapshot create/delete with the class.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/storageclass.yaml

Purpose: 4.11.0 optional single StorageClass.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass`; values for create, name, annotations, parameters, reclaim policy, binding mode, mount options, and driver name.

Control flow: Renders on `storageClass.create`; includes labels, an annotations section, optional parameters/mountOptions, and fixed `allowVolumeExpansion: true`.

State and persistence: Cluster storage provisioning policy.

Dependencies and integration points: External provisioner/resizer and NFS driver parameters/secrets.

Risks: Bad parameters or default annotations can affect PVC provisioning cluster-wide. Test signals: render with realistic NFS parameters and perform PVC create/resize/delete.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/values.yaml

Purpose: Default values for chart 4.11.0.

Important APIs/types/functions: Same value surface as v4.10.0 with NFS plugin tag updated to `v4.11.0`; sidecar tags remain provisioner v5.2.0, resizer v1.13.1, snapshotter/snapshot-controller v8.2.0, livenessprobe v2.15.0, registrar v2.13.0.

Control flow: Values control image refs, RBAC/service accounts, feature gates, controller/node scheduling/resources, optional snapshot controller/CRDs/classes, and optional StorageClass.

State and persistence: Helm release values and rendered Kubernetes resources.

Dependencies and integration points: Coordinates CSI sidecars, kubeletDir, snapshot APIs, and storage class parameters.

Risks: Snapshotter enabled by default in controller while external snapshotter/CRDs are disabled by default. Test signals: default render and full-feature snapshot/storage install dry-run.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/Chart.yaml

Purpose: Helm metadata for CSI NFS chart 4.12.0.

Important APIs/types/functions: `apiVersion: v1`, `appVersion: 4.12.0`, `description: CSI NFS Driver for Kubernetes`, `name: csi-driver-nfs`, and `version: 4.12.0`.

Control flow: Static chart metadata only; Helm uses it for package identity, repository index entries, install/upgrade records, and chart dependency bookkeeping.

State and persistence: No runtime Kubernetes state. Metadata is persisted in chart archives and Helm release history.

Dependencies and integration points: Connects the v4.12.0 chart directory to the CSI NFS application release; the rest of the v4.12.0 templates and values are outside this work item except where Helm reads the metadata.

Risks: Version format remains no-`v` like 4.11.0, which differs from older directories. Test signals: `helm lint`, `helm package`, repository index validation, and upgrade dry-run from 4.11.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/Chart.yaml -->
