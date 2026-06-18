# Research: subset-b-000366

Grouped research for selected SMB CSI Driver Helm chart files across releases v0.6.0 through v1.18.0. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned per-file output.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v0.6.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and does not yet expose the get-volume-stats feature flag in the node args. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v0.6.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v0.6.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates only the controller service account and provisioner ClusterRole/Binding; node service accounts and inline-volume secret access are not represented in this early RBAC file.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v0.6.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. early chart with fixed object names, Linux enabled by default, Windows disabled, controller replicas defaulting to 2, and images under the older microsoft/registry.k8s.io mix. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.0.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.0.0 metadata participates in the release line where first 1.x chart in this subset, adding a CSIDriver object, driver-name values, Windows node template, and still using v1beta1 CSIDriver plus beta csi-proxy pipe paths.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.0.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses the Deployment default rolling strategy unless the cluster default changes it; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. also embedded a v1beta1 CSIDriver object in adjacent driver template material in v1.0-era charts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.0.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1beta1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.0.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts the older beta csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.0.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and does not yet expose the get-volume-stats feature flag in the node args. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.0.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.0.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates the controller service account and provisioner ClusterRole/Binding with values-driven driver/RBAC names used by the 1.0 and 1.1 charts.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.0.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. first 1.x chart in this subset, adding a CSIDriver object, driver-name values, Windows node template, and still using v1beta1 CSIDriver plus beta csi-proxy pipe paths. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.0.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.1.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.1.0 metadata participates in the release line where adds values-driven resources, affinity, nodeSelector, tolerations, pod labels/annotations, priorityClassName, and pod securityContext while keeping most workload topology from v1.0.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.1.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses the Deployment default rolling strategy unless the cluster default changes it; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.1.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.1.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts the older beta csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.1.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and does not yet expose the get-volume-stats feature flag in the node args. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.1.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.1.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates the controller service account and provisioner ClusterRole/Binding with values-driven driver/RBAC names used by the 1.0 and 1.1 charts.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/templates/rbac-csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.1.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. adds values-driven resources, affinity, nodeSelector, tolerations, pod labels/annotations, priorityClassName, and pod securityContext while keeping most workload topology from v1.0.0. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.1.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.10.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.10.0 metadata participates in the release line where modernizes defaults around registry.k8s.io/sig-storage/smbplugin, baseRepo-aware images, named service accounts/RBAC, configurable workload names, dnsPolicy, maxUnavailable, workingMountDir, and enableGetVolumeStats.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.10.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses the Deployment default rolling strategy unless the cluster default changes it; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.10.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.10.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.10.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.10.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.10.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.10.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. modernizes defaults around registry.k8s.io/sig-storage/smbplugin, baseRepo-aware images, named service accounts/RBAC, configurable workload names, dnsPolicy, maxUnavailable, workingMountDir, and enableGetVolumeStats. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.10.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.11.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.11.0 metadata participates in the release line where small release bump over v1.10.0 with newer image tags and otherwise stable workload/RBAC shape in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.11.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses the Deployment default rolling strategy unless the cluster default changes it; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.11.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.11.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.11.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.11.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.11.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.11.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. small release bump over v1.10.0 with newer image tags and otherwise stable workload/RBAC shape in this subset. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.11.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.12.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.12.0 metadata participates in the release line where adds the optional Windows csi-proxy HostProcess DaemonSet and csiproxy image/default values, keeping the non-hostprocess Windows SMB node model.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.12.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.12.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses the Deployment default rolling strategy unless the cluster default changes it; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.12.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.12.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.12.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.12.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.12.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.12.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. adds the optional Windows csi-proxy HostProcess DaemonSet and csiproxy image/default values, keeping the non-hostprocess Windows SMB node model. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.12.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.13.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.13.0 metadata participates in the release line where adds Recreate strategy on the controller and capability drops/read-only root hardening, while retaining the v1.12 csi-proxy shape.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.13.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.13.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses `strategy: Recreate`; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.13.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.13.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.13.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It does not yet include Kerberos cache host-path support in this release.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.13.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.13.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.13.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. adds Recreate strategy on the controller and capability drops/read-only root hardening, while retaining the v1.12 csi-proxy shape. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.13.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.14.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.14.0 metadata participates in the release line where continues the hardened templates, bumps images, and extends Linux node behavior with Kerberos cache mounting/prefix support.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.14.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.14.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses `strategy: Recreate`; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.14.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.14.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.14.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It includes optional Kerberos cache directory/prefix handling.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.14.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.14.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.14.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. continues the hardened templates, bumps images, and extends Linux node behavior with Kerberos cache mounting/prefix support. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.14.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.15.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.15.0 metadata participates in the release line where keeps workload templates mostly stable but updates RBAC to include leader-election lease permissions and bumps chart/app images.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.15.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.15.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses `strategy: Recreate`; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.15.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.15.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.15.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It includes optional Kerberos cache directory/prefix handling.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.15.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.15.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.15.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. keeps workload templates mostly stable but updates RBAC to include leader-election lease permissions and bumps chart/app images. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.16.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.16.0 metadata participates in the release line where keeps the v1.15 chart structure with newer sidecar/image versions and the same non-hostprocess Windows defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.16.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.16.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses `strategy: Recreate`; it does not include the resizer sidecar in this release; resizing support is absent from this controller template. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.16.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and only persistent lifecycle mode. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.16.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled`  and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.16.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It includes optional Kerberos cache directory/prefix handling.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.16.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.16.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.16.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. keeps the v1.15 chart structure with newer sidecar/image versions and the same non-hostprocess Windows defaults. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.16.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.17.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.17.0 metadata participates in the release line where introduces csi-resizer, inline ephemeral volume support, Windows HostProcess node mode enabled by default, hostprocess-specific node template, expanded RBAC, and newer sidecars.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.17.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.17.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses `strategy: Recreate`; it includes a `csi-resizer` sidecar with leader election and volume-in-use handling. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-driver.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the Kubernetes `CSIDriver` registration object for the SMB CSI driver in chart v1.17.0. It names the driver from `.Values.driver.name`, tells Kubernetes that attach is not required, and asks kubelet to pass pod information on mount.

Important API surface is the `CSIDriver` resource under `storage.k8s.io/v1` with `spec.attachRequired: false`, `spec.podInfoOnMount: true`, and persistent lifecycle mode plus conditional ephemeral lifecycle mode when `feature.enableInlineVolume` is true. Helm control flow is minimal: later releases conditionally add `Ephemeral` to `volumeLifecycleModes` from `.Values.feature.enableInlineVolume`.

State and persistence are cluster-level: this object is stored in the Kubernetes API and controls kubelet/CSI interactions for every node plugin pod. Dependencies include the storage.k8s.io API version supported by the target cluster and the chart values that determine driver name and inline volume support. Integration points are kubelet plugin registration, inline CSI ephemeral volumes, and StorageClass/PV provisioning. Risks include API-version compatibility on older clusters, driver-name mismatch with node/controller args, and enabling ephemeral mode without the required RBAC secret access. Test signals are rendered-manifest diffing, `kubectl get csidriver`, kubelet plugin registration events, and PVC or inline volume mount smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml

Purpose: renders the Windows HostProcess variant of the SMB CSI node `DaemonSet` introduced in chart v1.17.0. It is selected when both `.Values.windows.enabled` and `.Values.windows.useHostProcessContainers` are true, replacing the older pod-plus-csi-proxy-pipes model with host-process containers running directly as `NT AUTHORITY\SYSTEM`.

Important APIs and inputs are `apps/v1 DaemonSet`, HostProcess pod `securityContext.windowsOptions`, `seccompProfile: RuntimeDefault`, `hostNetwork: true`, Windows node scheduling settings, an init container that creates the kubelet plugin directory, node-driver-registrar running `csi-node-driver-registrar.exe`, and smbplugin running `smbplugin.exe` with `--enable-windows-host-process=true`. Images use the SMB tag with a `-windows-hp` suffix for init and plugin containers.

Control flow is gated by `.Values.windows.useHostProcessContainers`, while the non-hostprocess Windows node template is explicitly disabled under the same flag. State persists in Kubernetes DaemonSet/pods and on the Windows host through kubelet plugin directories, registration data, SMB mappings, and direct host filesystem/network access.

Dependencies and integration points include Kubernetes Windows HostProcess support, kubelet Windows plugin paths, node-driver-registrar plugin registration flags, Windows SMB APIs, and the controller-provisioned volumes that later mount on Windows workloads. Risks are high privilege, requiring compatible Windows/Kubernetes versions, image tag suffix drift, hard-coded plugin directory creation using `C:\var\lib\kubelet`, and reduced liveness coverage compared with the non-hostprocess template. Test signals are Windows HostProcess admission/scheduling, plugin registration, kubelet CSINode visibility, SMB mount/unmount tests, and upgrade tests toggling `useHostProcessContainers`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node-windows-hostprocess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the Windows node `DaemonSet` for non-HostProcess SMB CSI node pods in chart v1.17.0. It schedules on Windows nodes, registers the CSI driver with kubelet, runs liveness checks, and starts smbplugin with access to kubelet directories and csi-proxy named pipes.

Important APIs and template inputs are `apps/v1 DaemonSet`, Windows `nodeSelector`, tolerations, affinity, priority class, service account, image pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, kubelet/plugin/registration hostPaths, and csi-proxy pipe hostPaths. This template is gated by `.Values.windows.enabled` and is disabled when `.Values.windows.useHostProcessContainers` is true and mounts both GA v1 and beta v1beta1 csi-proxy filesystem/SMB named pipes. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, volume-stats flag in newer releases, and `--remove-smb-mapping-during-unmount` in modern versions.

State persists as the DaemonSet/pods plus Windows host plugin directories, kubelet registration files, SMB mappings, and csi-proxy pipe interactions. Dependencies and integration points are Windows kubelet, csi-node-driver-registrar, livenessprobe, smbplugin, csi-proxy filesystem/SMB APIs, node OS labels, and Windows image variants.

Risks include Windows disabled by default in many releases, requiring csi-proxy to be installed separately unless the chart csi-proxy DaemonSet is enabled, path escaping mistakes in Helm values, stale beta pipe compatibility, missing hostPath directories, non-HostProcess limitations on newer Windows clusters, and security context fields that differ from Linux behavior. Test signals are `helm template` on Windows values, pod scheduling on Windows nodes, kubelet driver registration, csi-proxy pipe availability, SMB mount/unmount smoke tests, and cleanup of SMB mappings during unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux node `DaemonSet` for SMB CSI node service pods in chart v1.17.0. It deploys one pod per selected Linux node to register the CSI socket with kubelet, serve liveness checks, and run the privileged smb node plugin that mounts SMB shares through the host kubelet directory.

Important APIs and template inputs are `apps/v1 DaemonSet`, `hostNetwork`, Linux `nodeSelector`, tolerations, priority class, pull secrets, liveness-probe, node-driver-registrar, smbplugin containers, `hostPath` volumes for the plugin socket, kubelet mount tree, and plugins_registry. The smb container receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name in 1.x templates, and passes `--enable-get-volume-stats` from values. It includes optional Kerberos cache directory/prefix handling.

Control flow is gated by `.Values.linux.enabled`; modern versions use `.Values.linux.dsName`, `.Values.node.maxUnavailable`, `.Values.linux.dnsPolicy`, `.Values.node.affinity`, `.Values.node.nodeSelector`, and values-driven resources/security context, while early v1.17.0 material uses more fixed names and ports. State persists in Kubernetes as the DaemonSet and on each node as CSI socket/registration files and mounted volume state under kubelet. Mount propagation is bidirectional so kubelet can observe plugin mounts.

Dependencies and integration points include kubelet plugin registration, Linux hostPath semantics, livenessprobe, csi-node-driver-registrar, smbplugin node service, StorageClass/PV mounts produced by the controller, and optional Kerberos cache paths in newer releases. Risks include privileged container exposure, wrong kubelet path breaking registration or mounts, stale registration sockets in older lifecycle logic, maxUnavailable disruptions during upgrades, missing host mount propagation, and health-port mismatch. Test signals are rendered DaemonSet validation, node pod readiness, kubelet plugin registration events, `kubectl get csinode`, successful PVC mount/unmount, volume stats checks where enabled, and Kerberos mount tests when krb5 values are set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/csi-smb-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service-account and cluster-scoped RBAC resources for SMB CSI controller-side and, in newer charts, node-side operations for release v1.17.0. Creation is gated by `.Values.serviceAccount.create` and `.Values.rbac.create`, so operators can bring their own identities and permissions.

Important APIs are Kubernetes `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding`. The provisioner role grants PV/PVC, StorageClass, events, CSINode, node, secret, and leader-election lease access according to the sidecar generation used in this release. It creates both controller and node service accounts, a provisioner ClusterRole/Binding, and later lease permissions for leader election. From v1.17.0 it also adds a csi-resizer ClusterRole/Binding and conditional node secret RBAC for inline ephemeral volumes.

Control flow is Helm conditional rendering: service accounts are emitted only when requested, RBAC is emitted only when requested, and inline-volume secret access in newer releases is tied to `.Values.feature.enableInlineVolume`. State is persisted as cluster RBAC objects and directly controls what the csi-provisioner, csi-resizer, and node plugin can read or mutate.

Dependencies and integration points include the external-provisioner, external-resizer, Kubernetes coordination leases for leader election, secret-backed SMB credentials, and the chart serviceAccount names. Risks are over-broad secret read access, missing lease verbs causing leader election failures, missing resizer RBAC when resizing is enabled, and name mismatches if users override service-account values. Test signals are `helm template` with RBAC toggles, Kubernetes SubjectAccessReview or `kubectl auth can-i`, sidecar leader-election logs, PVC provisioning/resize tests, and inline ephemeral volume mount tests when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/templates/rbac-csi-smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/values.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/values.yaml

Purpose: supplies the default Helm values for the SMB CSI Driver chart release v1.17.0. These defaults bind image repositories/tags, service-account/RBAC names, driver identity, feature flags, controller Deployment settings, Linux and Windows node DaemonSet settings, resources, scheduling constraints, labels, annotations, priority class, and pod security context.

Important configuration areas are `image.*` sidecars and smbplugin tags, `serviceAccount`, `rbac`, `driver.name`, `feature`, `controller`, `node`, `linux`, `windows`, `customLabels`, `podAnnotations`, `podLabels`, `priorityClassName`, and `securityContext`. introduces csi-resizer, inline ephemeral volume support, Windows HostProcess node mode enabled by default, hostprocess-specific node template, expanded RBAC, and newer sidecars. The control flow is indirect: templates branch on booleans such as `linux.enabled`, `windows.enabled`, `windows.csiproxy.enabled`, `windows.useHostProcessContainers`, `serviceAccount.create`, `rbac.create`, and `feature.enableInlineVolume`.

State and persistence are Helm release values stored with the release and used to render persistent Kubernetes API objects. They influence runtime state by changing container images, liveness ports, kubelet host paths, Kerberos cache mounting, Windows csi-proxy integration, HostProcess mode, and controller/node resource envelopes.

Dependencies and integration points include registry.k8s.io or older Microsoft image registries, kubelet plugin and plugins_registry directories, Windows csi-proxy named pipes or HostProcess APIs, Kubernetes scheduling labels/tolerations, and external-provisioner/resizer/liveness/registrar sidecars. Risks include unsupported image/tag combinations, enabling Windows without csi-proxy or HostProcess prerequisites, wrong kubelet path values, overly strict securityContext for privileged node behavior, unbounded broad tolerations, and feature flags whose RBAC/templates must stay synchronized. Test signals are `helm template` using default and overridden values, `helm lint`, install/upgrade tests on Linux and Windows clusters, pod scheduling checks, sidecar startup logs, PVC provisioning/mount/resize tests, and Kerberos or Windows-specific mount smoke tests where configured.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.17.0/csi-driver-smb/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/Chart.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/Chart.yaml

Purpose: Helm chart metadata for the SMB CSI Driver release v1.18.0. It declares apiVersion v1, chart name `csi-driver-smb`, description, chart `version`, and `appVersion`, allowing Helm repositories and consumers to identify the packaged Kubernetes manifests for this driver release.

Important fields are `apiVersion`, `appVersion`, `description`, `name`, and `version`; there are no templates, functions, or runtime APIs in this file. Control flow and state are absent, but Helm uses these values when packaging, indexing, installing, and upgrading the chart.

Dependencies and integration points are Helm itself, the chart repository index, Artifact Hub style metadata around the chart tree, and the image tags in adjacent `values.yaml` files. The main risk is version skew: a mismatched `appVersion` or `version` can make automated upgrades install templates that do not correspond to the intended smbplugin image. Test signals are `helm lint`, chart packaging/index validation, and install/upgrade smoke tests that verify rendered manifests match the release being advertised. This v1.18.0 metadata participates in the release line where carries the v1.17 controller/csi-proxy pattern forward with appVersion/chart/image bumps; this subset includes Chart, csi-proxy, and controller only.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.18.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the controller `Deployment` for the SMB CSI driver release v1.18.0. The pod hosts the external provisioner, liveness probe, smb controller process, and in newer releases the external resizer, all sharing an in-pod CSI Unix socket directory.

Important APIs and template inputs include `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.serviceAccount.controller`, `.Values.driver.name`, `.Values.podLabels`, `.Values.podAnnotations`, pull secrets, resources, node selectors, affinity, tolerations, and security context. This release uses `strategy: Recreate`; it includes a `csi-resizer` sidecar with leader election and volume-in-use handling. The smb container runs privileged, exposes metrics and health endpoints, receives `CSI_ENDPOINT`, and passes controller log level, driver name in newer templates, metrics address, and working mount dir where available.

Control flow is Helm-driven scheduling and image selection: repository names beginning with `/` are prefixed by `.Values.image.baseRepo` in modern charts, control-plane/master affinity is synthesized only when explicit affinity is not set, and resource/security blocks are read from values. State is mostly external: the controller uses Kubernetes API objects through provisioner/resizer RBAC and socket-local CSI calls to create PVs, watch PVCs, emit events, and perform volume expansion; the chart persists only the Deployment and pods.

Dependencies and integration points include external-provisioner, external-resizer when present, livenessprobe, smbplugin controller mode, Kubernetes leader election leases, the controller service account, PVC/PV/StorageClass APIs, and Helm labels from `_helpers.tpl`. Risks include service account/RBAC drift, leader-election namespace mistakes, controller replicas greater than one without healthy leader election, privileged controller attack surface, image-baseRepo templating errors, and liveness port mismatch. Test signals are `helm template`, `kubectl rollout status deployment`, sidecar leader-election logs, controller liveness endpoint checks, PVC provisioning, reclaim policy behavior, and resize tests for v1.17+ charts. relies on the separate `csi-smb-driver.yaml` template for CSIDriver registration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.18.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
