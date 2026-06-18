# Research Group subset-b-000390

This grouped report covers JuiceFS CSI driver Kubernetes deployment manifests, CI overlays, webhook/cert-manager manifests, dashboard monitoring JSON, image build helpers, and maintenance scripts. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/k8s_before_v1_18.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/k8s_before_v1_18.yaml

## Purpose
Generated all-in-one Kubernetes manifest for installing the JuiceFS CSI driver on Kubernetes versions before 1.18. It is marked as kustomize output and uses `storage.k8s.io/v1beta1` `CSIDriver`, which is the compatibility difference from newer manifests.

## Important APIs, Types, and Resources
Defines ServiceAccounts for controller, node, and dashboard; ClusterRoles and bindings for provisioning, snapshotting, node services, and dashboard; `juicefs-csi-driver-config` ConfigMap; dashboard Service/Deployment; controller StatefulSet; node DaemonSet; and `CSIDriver csi.juicefs.com`. Images include `juicedata/juicefs-csi-driver:v0.31.3`, `juicedata/csi-dashboard:v0.31.3`, and sig-storage sidecars.

## Control Flow
Applying the manifest creates RBAC first, then config/service/workload resources. The controller StatefulSet exposes a CSI socket for provisioner/resizer/liveness sidecars and runs with leader election. The node DaemonSet registers the CSI driver with kubelet, mounts host paths, and serves node publish/unpublish calls. Dashboard deployment queries cluster state using its RBAC.

## State and Persistence
All durable state is Kubernetes API state plus hostPath directories under `/var/lib/juicefs`, kubelet plugin sockets, webhook/dashboard Services, and leader-election leases/configmaps. The ConfigMap embeds driver settings and mountPodPatch defaults.

## Dependencies and Integration Points
Depends on Kubernetes RBAC, apps/v1 workloads, sig-storage CSI sidecars, kubelet plugin paths, snapshot CRDs for snapshotter permissions, and JuiceFS CSI driver flag/config behavior. It is integrated with generated install scripts and should correspond to kustomize output from the deployment tree.

## Risks
Risks include broad RBAC (`nodes/proxy`, pod create/delete, secrets mutate, pod exec), privileged node/controller containers with bidirectional mount propagation, hostPath assumptions, outdated v1beta1 CSIDriver compatibility, and generated-file drift from source kustomize overlays.

## Test Signals
Signals are `kustomize build` parity checks, `kubectl apply --dry-run=server`, successful CSI registration on pre-1.18 clusters, dynamic/static volume tests, snapshot tests when CRDs exist, and dashboard health/metrics checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/k8s_before_v1_18.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/daemonset_resource.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/daemonset_resource.yaml

## Purpose
Resource patch that assigns CPU and memory requests/limits to the node DaemonSet's `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` `juicefs-csi-node` in `kube-system`; sets limits `cpu: 1000m`, `memory: 1Gi` and requests `cpu: 100m`, `memory: 512Mi`.

## Control Flow
The base kustomization applies this patch to the node workload after loading `resources.yaml`, adding scheduling and limit metadata without touching the rest of the DaemonSet spec.

## State and Persistence
No state is stored in the file. Once applied, resource settings are persisted in the DaemonSet pod template and influence scheduler reservations and cgroup limits for new node pods.

## Dependencies and Integration Points
Depends on Kustomize strategic merge by container name and Kubernetes resource quantity parsing. Integrates with node plugin performance and cluster capacity planning.

## Risks
Risks are under-provisioning memory for high-volume mount workloads, over-reserving on small nodes, or patch target drift if the container is renamed.

## Test Signals
Render the base overlay and inspect resource fields; run node publish/unpublish load tests and watch pod OOM/throttling metrics.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/daemonset_resource.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `resources.yaml` and applies deployment-mode-specific patches rather than defining runtime resources from scratch.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `resources.yaml`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `daemonset_resource.yaml and statefulset_resource.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/resources.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/resources.yaml

## Purpose
Canonical base manifest for the JuiceFS CSI driver deployment. It defines the full set of deployable Kubernetes resources before release/webhook/CI overlays remove or specialize pieces.

## Important APIs, Types, and Resources
Contains 22 YAML documents: controller/node/dashboard ServiceAccounts, ClusterRoles and ClusterRoleBindings, `CSIDriver csi.juicefs.com`, driver ConfigMap, controller StatefulSet, node DaemonSet, mutating and validating webhook configurations, webhook Service/Secret, dashboard Deployment, and dashboard Service. It embeds CSI sidecars including provisioner, resizer, snapshotter, node-driver-registrar, and livenessprobe.

## Control Flow
Kustomize overlays consume this file as the root resource set. Applying the base directly creates both node and controller CSI components, admission webhook resources, and dashboard. The controller handles provisioning/resizing/snapshot control-plane calls while the DaemonSet handles node plugin registration and mount operations.

## State and Persistence
Persistent cluster state includes RBAC, ConfigMap settings, admission configurations, TLS Secret, Services, StatefulSet/DaemonSet/Deployment pod templates, hostPath-backed JuiceFS directories, CSI sockets, leader-election leases, and objects created later by the driver such as mount pods, jobs, and secrets.

## Dependencies and Integration Points
Depends on Kubernetes RBAC, admissionregistration.k8s.io/v1, storage.k8s.io/v1 CSIDriver, apps/v1 workloads, sig-storage sidecars, hostPath kubelet layout, and JuiceFS CSI driver flags. It integrates with all deployment overlays and generated top-level YAMLs.

## Risks
Major risks are broad privileged access, admission webhook availability blocking pod/serverless admission when enabled, secret mutation permissions, hostPath and mountPropagation sensitivity, and base changes breaking many overlays that assume exact resource/container names.

## Test Signals
Signals include building every overlay, server-side dry-run validation, CSI sanity/e2e suites, webhook admission tests, dashboard access tests, and RBAC review with least-privilege tooling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/resources.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/statefulset_resource.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/statefulset_resource.yaml

## Purpose
Resource patch that assigns CPU and memory requests/limits to the controller StatefulSet's `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` `juicefs-csi-controller`; sets limits `cpu: 1000m`, `memory: 1Gi` and requests `cpu: 100m`, `memory: 512Mi`.

## Control Flow
The base kustomization merges this into the controller pod template, leaving sidecar resources unchanged. New controller pods inherit these constraints.

## State and Persistence
No standalone persistence; rendered values persist in the StatefulSet template and affect scheduling/cgroups for controller replicas.

## Dependencies and Integration Points
Depends on Kustomize merge keys and Kubernetes resource quantity support. Integrates with controller leader election and CSI sidecar socket behavior by shaping available CPU/memory.

## Risks
Too-low memory can destabilize provisioning or webhook flows; too-high requests may block scheduling in small clusters. Container-name drift can make the patch ineffective.

## Test Signals
Render the base overlay, inspect pod template resources, and watch controller OOM/throttle metrics during provisioning and webhook tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/statefulset_resource.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `fs-mount-share` CI deployment variant. It injects `FS_SHARE_MOUNT=true` into the `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `fs-mount-share` behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `fs-mount-share/daemonset.yaml and fs-mount-share/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `fs-mount-share` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--cache-client-conf` and shared filesystem mount env. It injects `FS_SHARE_MOUNT=true` into the controller container.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `pod-mount-share` CI deployment variant. It injects `STORAGE_CLASS_SHARE_MOUNT=true` into the `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `pod-mount-share` behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `pod-mount-share/daemonset.yaml and pod-mount-share/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `pod-mount-share` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--cache-client-conf` and shared storage-class mount env. It injects `STORAGE_CLASS_SHARE_MOUNT=true` into the controller container.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-mount-share/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `pod-provisioner` CI deployment variant.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `pod-provisioner` behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `pod-provisioner/daemonset.yaml and pod-provisioner/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `pod-provisioner` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--provisioner=true`. It also deletes the `csi-provisioner` sidecar so the driver process handles provisioning directly.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod-provisioner/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `pod` CI deployment variant.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `pod` behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `pod/daemonset.yaml and pod/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `pod` CI/deployment variant. It rewrites the `juicefs-plugin` args to include standard pod-mount controller args with `--v=1`.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `process` CI deployment variant.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--by-process=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `process` behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `process/daemonset.yaml and process/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `process` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--by-process=true`.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/process/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../base` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. It creates a controller-only webhook plus in-process provisioner CI mode and intentionally removes node DaemonSet resources; the duplicated RBAC patch entry should be reviewed because it can append duplicate rules.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../base`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `statefulset.yaml, rbac.yaml, duplicate rbac.yaml entry, and inline deletes for node resources` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/rbac.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/rbac.yaml

## Purpose
JSON6902 patch that extends `juicefs-external-provisioner-role` for webhook-style controller operation.

## Important APIs, Types, and Resources
The document is a list of `op: add` operations appending to `/rules/-`. It grants wildcard `pods/exec` and, in most variants, read access for `statefulsets/replicasets get` in the `apps` API group.

## Control Flow
Kustomize applies these operations to the ClusterRole after loading the base role. The rendered controller can then exec into pods and inspect owning workloads while handling webhook/provisioner flows.

## State and Persistence
The patch has no independent state. Once applied, the persisted state is expanded ClusterRole permission in the cluster, bound to `juicefs-csi-controller-sa` by the base ClusterRoleBinding.

## Dependencies and Integration Points
Depends on Kubernetes RBAC JSON patch semantics and the exact base ClusterRole name. It integrates with admission-webhook code that needs pod exec or workload lookups.

## Risks
The main risk is privilege expansion: wildcard `pods/exec` is powerful and should be limited to deployment modes that need it. Duplicate application can append duplicate RBAC rules, which is noisy and may hide review errors.

## Test Signals
Validate by rendering the overlay, reviewing effective RBAC with `kubectl auth can-i`, and running webhook/provisioner tests that exercise pod exec and workload ownership checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `webhook-provisioner` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--webhook=true` and `--provisioner=true`. It also deletes the `csi-provisioner` sidecar so the driver process handles provisioning directly.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook-provisioner/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../base` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. It creates a controller-only webhook CI mode with validating webhook enabled.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../base`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `statefulset.yaml, rbac.yaml, and inline deletes for node resources` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/rbac.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/rbac.yaml

## Purpose
JSON6902 patch that extends `juicefs-external-provisioner-role` for webhook-style controller operation.

## Important APIs, Types, and Resources
The document is a list of `op: add` operations appending to `/rules/-`. It grants wildcard `pods/exec` and, in most variants, read access for `statefulsets/replicasets get` in the `apps` API group.

## Control Flow
Kustomize applies these operations to the ClusterRole after loading the base role. The rendered controller can then exec into pods and inspect owning workloads while handling webhook/provisioner flows.

## State and Persistence
The patch has no independent state. Once applied, the persisted state is expanded ClusterRole permission in the cluster, bound to `juicefs-csi-controller-sa` by the base ClusterRoleBinding.

## Dependencies and Integration Points
Depends on Kubernetes RBAC JSON patch semantics and the exact base ClusterRole name. It integrates with admission-webhook code that needs pod exec or workload lookups.

## Risks
The main risk is privilege expansion: wildcard `pods/exec` is powerful and should be limited to deployment modes that need it. Duplicate application can append duplicate RBAC rules, which is noisy and may hide review errors.

## Test Signals
Validate by rendering the overlay, reviewing effective RBAC with `kubectl auth can-i`, and running webhook/provisioner tests that exercise pod exec and workload ownership checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `webhook` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--webhook=true` and `--validating-webhook=true`.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `without-kubelet/fs-mount-share` CI deployment variant. It injects `FS_SHARE_MOUNT=true` into the `juicefs-plugin` container. It deletes `KUBELET_PORT` and `HOST_IP`, forcing behavior that does not rely on kubelet host metadata.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `without-kubelet/fs-mount-share` behavior. It removes kubelet-derived env from the node plugin to test API-server fallback behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `without-kubelet/fs-mount-share/daemonset.yaml and without-kubelet/fs-mount-share/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `without-kubelet/fs-mount-share` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--cache-client-conf` plus `FS_SHARE_MOUNT`. It injects `FS_SHARE_MOUNT=true` into the controller container.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/fs-mount-share/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `without-kubelet/pod-mount-share` CI deployment variant. It injects `STORAGE_CLASS_SHARE_MOUNT=true` into the `juicefs-plugin` container. It deletes `KUBELET_PORT` and `HOST_IP`, forcing behavior that does not rely on kubelet host metadata.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `without-kubelet/pod-mount-share` behavior. It removes kubelet-derived env from the node plugin to test API-server fallback behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `without-kubelet/pod-mount-share/daemonset.yaml and without-kubelet/pod-mount-share/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `without-kubelet/pod-mount-share` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--cache-client-conf` plus `STORAGE_CLASS_SHARE_MOUNT`. It injects `STORAGE_CLASS_SHARE_MOUNT=true` into the controller container.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-mount-share/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `without-kubelet/pod-provisioner` CI deployment variant. It deletes `KUBELET_PORT` and `HOST_IP`, forcing behavior that does not rely on kubelet host metadata.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `without-kubelet/pod-provisioner` behavior. It removes kubelet-derived env from the node plugin to test API-server fallback behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `without-kubelet/pod-provisioner/daemonset.yaml and without-kubelet/pod-provisioner/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `without-kubelet/pod-provisioner` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--provisioner=true`. It also deletes the `csi-provisioner` sidecar so the driver process handles provisioning directly.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod-provisioner/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `without-kubelet/pod` CI deployment variant. It deletes `KUBELET_PORT` and `HOST_IP`, forcing behavior that does not rely on kubelet host metadata.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `without-kubelet/pod` behavior. It removes kubelet-derived env from the node plugin to test API-server fallback behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `without-kubelet/pod/daemonset.yaml and without-kubelet/pod/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `without-kubelet/pod` CI/deployment variant. It rewrites the `juicefs-plugin` args to include standard pod mode args.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/without-kubelet/pod/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-v1/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-v1/kustomization.yaml

## Purpose
Small Kustomize overlay that builds the base deployment but retags the `juicedata/juicefs-csi-driver` image to `csi-v1`.

## Important APIs, Types, and Resources
Uses Kustomize `images` transformer with `name: juicedata/juicefs-csi-driver` and `newTag: csi-v1`; resources come from `../base`.

## Control Flow
Kustomize loads base resources and rewrites matching image references in controller/node workloads to the compatibility tag. No resource shape changes occur.

## State and Persistence
Stateless source file; rendered image tags persist in workload pod templates when applied.

## Dependencies and Integration Points
Depends on exact image name matching and Kustomize image transformer semantics. Integrates with compatibility testing or release workflows for the `csi-v1` driver image.

## Risks
If the base image name changes or includes registry prefixes unexpectedly, retagging may not apply. A moving `csi-v1` tag also weakens reproducibility.

## Test Signals
Run `kustomize build`, confirm image tags, and smoke-test CSI registration and volume operations with the retagged image.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-v1/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../base` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This is the default release overlay that strips admission-webhook resources while keeping normal controller, node, and dashboard components.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../base`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `statefulset.yaml and inline deletes for webhook Service, Secret, MutatingWebhookConfiguration, and ValidatingWebhookConfiguration` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/statefulset.yaml

## Purpose
Release overlay patch that removes the webhook certificate volume and mount from the controller StatefulSet.

## Important APIs, Types, and Resources
Targets `apps/v1` StatefulSet `juicefs-csi-controller`; deletes `volumeMounts[name=webhook-certs]` from `juicefs-plugin` and `volumes[name=webhook-certs]` from the pod spec.

## Control Flow
When the release overlay builds, this patch is applied after base resources are loaded and before inline deletion of webhook objects. The release controller runs without webhook TLS material.

## State and Persistence
No source-level state. Persisted effect is the rendered StatefulSet template lacking the certificate mount and volume.

## Dependencies and Integration Points
Depends on Kustomize strategic merge `$patch: delete` and base names. Integrates with default release mode where admission webhooks are not installed.

## Risks
If webhook flags remain enabled while cert volumes are deleted, the controller would fail webhook serving. Name drift can make the delete ineffective and leave unused secret mounts.

## Test Signals
Build the release overlay and verify no `webhook-certs` volume/mount remains; run controller startup and non-webhook provisioning tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/certificate.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/certificate.yaml

## Purpose
cert-manager resource bundle for webhook TLS. It defines a self-signed issuer and a certificate whose secret is consumed by webhook-serving controller pods.

## Important APIs, Types, and Resources
Defines `cert-manager.io/v1` `Issuer juicefs-selfsigned` and `Certificate juicefs-cert` in `kube-system`. The certificate lasts 43800h, covers `juicefs-admission-webhook`, `juicefs-admission-webhook.kube-system`, and `juicefs-admission-webhook.kube-system.svc`, and writes `juicefs-webhook-certs`.

## Control Flow
cert-manager reconciles the Issuer and Certificate after apply, creates/renews the target Secret, and later injects the CA into webhook configurations through annotations in companion patches.

## State and Persistence
Persistent state is cert-manager CRDs plus generated TLS Secret. The source file itself has no active state.

## Dependencies and Integration Points
Depends on cert-manager being installed and on webhook Service DNS names matching certificate SANs. Integrates with webhook-with-certmanager overlay and controller TLS volume mounts from base resources.

## Risks
Risks include missing cert-manager CRDs, long-lived self-signed cert rotation expectations, SAN mismatch after service rename, and startup races before the Secret exists.

## Test Signals
Validate by applying to a cert-manager cluster, checking Certificate Ready condition, Secret contents, CA injection, and successful admission HTTPS calls.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/certificate.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../base plus certificate.yaml` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This overlay enables controller-only webhook operation using cert-manager-managed TLS instead of the static secret.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../base plus certificate.yaml`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `statefulset.yaml, rbac.yaml, webhookconfiguration.yaml, validating_webhookconfiguration.yaml, and inline deletes for node resources and static Secret` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/rbac.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/rbac.yaml

## Purpose
JSON6902 patch that extends `juicefs-external-provisioner-role` for webhook-style controller operation.

## Important APIs, Types, and Resources
The document is a list of `op: add` operations appending to `/rules/-`. It grants wildcard `pods/exec` and, in most variants, read access for `pods/exec only` in the `apps` API group.

## Control Flow
Kustomize applies these operations to the ClusterRole after loading the base role. The rendered controller can then exec into pods and inspect owning workloads while handling webhook/provisioner flows.

## State and Persistence
The patch has no independent state. Once applied, the persisted state is expanded ClusterRole permission in the cluster, bound to `juicefs-csi-controller-sa` by the base ClusterRoleBinding.

## Dependencies and Integration Points
Depends on Kubernetes RBAC JSON patch semantics and the exact base ClusterRole name. It integrates with admission-webhook code that needs pod exec or workload lookups.

## Risks
The main risk is privilege expansion: wildcard `pods/exec` is powerful and should be limited to deployment modes that need it. Duplicate application can append duplicate RBAC rules, which is noisy and may hide review errors.

## Test Signals
Validate by rendering the overlay, reviewing effective RBAC with `kubectl auth can-i`, and running webhook/provisioner tests that exercise pod exec and workload ownership checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `webhook-with-certmanager` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--webhook=true` and `--validating-webhook=true`.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/validating_webhookconfiguration.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/validating_webhookconfiguration.yaml

## Purpose
Patch fragment adding cert-manager CA injection metadata to the validating webhook configuration.

## Important APIs, Types, and Resources
Targets `admissionregistration.k8s.io/v1` `ValidatingWebhookConfiguration juicefs-admission-webhook` and adds annotation `cert-manager.io/inject-ca-from: kube-system/juicefs-cert`.

## Control Flow
Kustomize merges the metadata annotation into the base validating webhook object. cert-manager's injector later fills the webhook client CA bundle from the named Certificate.

## State and Persistence
No state in the file. Persisted state is the annotation on the ValidatingWebhookConfiguration and cert-manager-managed CA bundle updates.

## Dependencies and Integration Points
Depends on cert-manager CA injector, exact webhook configuration name, and Certificate namespace/name. Integrates with the webhook-with-certmanager overlay.

## Risks
If cert-manager is absent or the annotation points to the wrong Certificate, admission calls fail TLS validation. Patch drift can leave the validating webhook using stale static CA data.

## Test Signals
Render the overlay, inspect annotations, verify CA bundle injection, and run validating-admission negative/positive tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/validating_webhookconfiguration.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/webhookconfiguration.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/webhookconfiguration.yaml

## Purpose
Patch fragment adding cert-manager CA injection metadata to the mutating webhook configuration.

## Important APIs, Types, and Resources
Targets `admissionregistration.k8s.io/v1` `MutatingWebhookConfiguration juicefs-admission-webhook` and adds annotation `cert-manager.io/inject-ca-from: kube-system/juicefs-cert`.

## Control Flow
Kustomize merges the annotation into the mutating webhook. cert-manager injects CA data so kube-apiserver can trust the webhook Service TLS certificate.

## State and Persistence
No local state; persisted cluster state is the annotation and injected CA bundle.

## Dependencies and Integration Points
Depends on cert-manager, the named Certificate, and base webhook object identity. Integrates with pod/serverless mutation paths in the CSI controller.

## Risks
Wrong annotation targets or absent cert-manager can make the mutating webhook reject or time out admissions. CA injection delays can affect initial rollout.

## Test Signals
Check rendered annotation, cert-manager injector events, populated `clientConfig.caBundle`, and admission mutation e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/webhookconfiguration.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../base` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This is the non-cert-manager webhook overlay that keeps static webhook Secret material from the base manifest.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../base`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `statefulset.yaml, rbac.yaml, and inline deletes for node DaemonSet/service account/RBAC` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/rbac.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/rbac.yaml

## Purpose
JSON6902 patch that extends `juicefs-external-provisioner-role` for webhook-style controller operation.

## Important APIs, Types, and Resources
The document is a list of `op: add` operations appending to `/rules/-`. It grants wildcard `pods/exec` and, in most variants, read access for `statefulsets/replicasets get` in the `apps` API group.

## Control Flow
Kustomize applies these operations to the ClusterRole after loading the base role. The rendered controller can then exec into pods and inspect owning workloads while handling webhook/provisioner flows.

## State and Persistence
The patch has no independent state. Once applied, the persisted state is expanded ClusterRole permission in the cluster, bound to `juicefs-csi-controller-sa` by the base ClusterRoleBinding.

## Dependencies and Integration Points
Depends on Kubernetes RBAC JSON patch semantics and the exact base ClusterRole name. It integrates with admission-webhook code that needs pod exec or workload lookups.

## Risks
The main risk is privilege expansion: wildcard `pods/exec` is powerful and should be limited to deployment modes that need it. Duplicate application can append duplicate RBAC rules, which is noisy and may hide review errors.

## Test Signals
Validate by rendering the overlay, reviewing effective RBAC with `kubectl auth can-i`, and running webhook/provisioner tests that exercise pod exec and workload ownership checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/statefulset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-controller` StatefulSet in the `webhook` CI/deployment variant. It rewrites the `juicefs-plugin` args to include `--webhook=true` and `--validating-webhook=true` with verbosity 5.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` named `juicefs-csi-controller` in `kube-system`, especially `spec.template.spec.containers[name=juicefs-plugin]`. Some variants also target `containers[name=csi-provisioner]` with `$patch: delete`.

## Control Flow
Kustomize applies this after loading the base/release StatefulSet. The resulting controller pod starts the driver with leader election and the selected mode flags, then sidecars connect over `/var/lib/csi/sockets/pluginproxy/csi.sock` unless the provisioner sidecar is removed.

## State and Persistence
The patch is stateless; runtime state is the controller replica set, CSI socket, leader-election leases, cached client config, generated mount pods/jobs/secrets, and any provisioning decisions triggered by flags.

## Dependencies and Integration Points
Depends on base controller container names, Kubernetes leader election resources, sig-storage CSI sidecars, and JuiceFS driver flag parsing. It integrates with the same ConfigMap mounted at `/etc/config/config.yaml`.

## Risks
Risks include a patch replacing the full args list and accidentally omitting required flags, mismatched sidecar deletion leaving no provisioner path, and mode flags that require extra RBAC or webhook resources not present in the overlay.

## Test Signals
Signals are rendered StatefulSet inspection, controller startup logs with expected flags, dynamic provisioning tests, leader-election health, and mode-specific CSI integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/monitor/dashboard.json -->
# sources/control-plane/juicefs-csi-driver/deploy/monitor/dashboard.json

## Purpose
Grafana dashboard JSON for monitoring JuiceFS CSI driver health and operation errors.

## Important APIs, Types, and Resources
Defines dashboard `JuiceFS CSI Driver`, schema version 41, 30s refresh, datasource template variable, stat panels for node readiness/controller availability/mount points/error counters, timeseries panels for volume path health and error rates, and a table for volume health details. PromQL expressions reference kube-state-metrics and JuiceFS metrics such as `juicefs_volume_path_health`, `juicefs_provision_errors`, `juicefs_volume_errors`, and `juicefs_volume_del_errors`.

## Control Flow
Grafana loads the JSON, resolves the Prometheus datasource, and executes panel queries over the last hour by default. Operators use stat panels for current health and timeseries/table panels to drill into node-level or volume-level failures.

## State and Persistence
The JSON stores dashboard definition only. Runtime state lives in Grafana's dashboard store and Prometheus time series; no metrics are persisted by this file.

## Dependencies and Integration Points
Depends on Grafana dashboard schema, Prometheus datasource availability, kube-state-metrics names for DaemonSet/StatefulSet readiness, and CSI driver metric names. Integrates with monitoring documentation and cluster observability setup.

## Risks
Risks are metric-name drift, missing kube-state-metrics, fixed resource names that do not match customized installs, and dashboard JSON schema drift in future Grafana versions.

## Test Signals
Import the dashboard into Grafana, run Prometheus query validation, confirm non-empty panels on a live cluster, and compare panel queries with current driver metric names.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/monitor/dashboard.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook-with-certmanager.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/webhook-with-certmanager.yaml

## Purpose
Generated all-in-one manifest for deploying JuiceFS CSI controller/dashboard with admission webhooks and cert-manager-managed TLS. It is kustomize output for the webhook-with-certmanager overlay.

## Important APIs, Types, and Resources
Includes controller/dashboard service accounts, provisioner/snapshotter/dashboard RBAC, ConfigMap, webhook Service, dashboard Service/Deployment, controller StatefulSet, `Certificate juicefs-cert`, `Issuer juicefs-selfsigned`, `CSIDriver`, mutating webhook configurations for standard and serverless admission, and validating webhook configuration. It excludes the node DaemonSet and node RBAC.

## Control Flow
Applying it installs controller-only admission infrastructure. cert-manager reconciles TLS Secret and CA injection, the controller StatefulSet runs with webhook flags, and kube-apiserver calls the webhook Service during matching admissions.

## State and Persistence
Persistent state includes RBAC, webhook configurations, cert-manager CRDs/status, generated TLS Secret, dashboard and controller workloads, CSI driver object, and ConfigMap settings. There is no node-side DaemonSet state from this manifest.

## Dependencies and Integration Points
Depends on cert-manager, Kubernetes admissionregistration/v1, sig-storage sidecars, JuiceFS CSI webhook code, and the dashboard. Integrates with install script update tooling and webhook-with-certmanager kustomize overlay.

## Risks
Risks include admission outage if the controller or cert-manager is unavailable, broad controller RBAC, generated-file drift, and the absence of node DaemonSet resources if users expect a complete CSI node deployment from this manifest.

## Test Signals
Signals are `kustomize build` parity, server-side dry-run on a cert-manager cluster, Certificate Ready/CA injection checks, webhook admission e2e tests, and controller/dashboard readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook-with-certmanager.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/webhook.yaml

## Purpose
Generated all-in-one manifest for deploying JuiceFS CSI controller/dashboard with admission webhooks and static TLS Secret material. It is kustomize output for the webhook overlay.

## Important APIs, Types, and Resources
Includes controller/dashboard service accounts, provisioner/snapshotter/dashboard RBAC, ConfigMap, static `juicefs-webhook-certs` Secret, webhook Service, dashboard Service/Deployment, controller StatefulSet with webhook flags, `CSIDriver`, two mutating webhook configurations, and one validating webhook configuration. It excludes node DaemonSet and node RBAC.

## Control Flow
Applying it creates static TLS material, starts the controller webhook server, and registers mutating/validating webhooks. kube-apiserver then routes matching admissions to `juicefs-admission-webhook` in `kube-system`.

## State and Persistence
Persistent cluster state includes the static Secret, webhook configurations and CA bundles, controller/dashboard workloads, RBAC, ConfigMap, and Services. Certificate rotation is not automatic unless the generated Secret is replaced.

## Dependencies and Integration Points
Depends on Kubernetes admissionregistration/v1, valid embedded webhook certificate data, sig-storage sidecars, and driver webhook behavior. Integrated into `scripts/juicefs-csi-webhook-install.sh` by `hack/update_install_script.sh`.

## Risks
Risks are stale/expired static certs, admission failure policy impact, generated-file drift, broad RBAC, and confusing controller-only scope if a full CSI node deployment is expected.

## Test Signals
Validate by dry-run apply, TLS Secret sanity checks, webhook call success, admission mutation/validation tests, and diffing against kustomize output.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/webhook.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/docker/Makefile -->
# sources/control-plane/juicefs-csi-driver/docker/Makefile

## Purpose
Docker image build Makefile for JuiceFS CSI driver, JuiceFS mount images, and dashboard images.

## Important APIs, Types, and Resources
Defines variables for image names, registry, architecture, versions, JuiceFS CE/EE versions, package URLs, and targets such as `image-nightly`, `image-version`, `image-release-check`, `ce-image`, `ce-image-buildx`, `ee-image`, `ee-image-buildx`, `ee-image-4.0-buildx`, `dashboard-build`, and `dashboard-buildx`.

## Control Flow
Targets invoke Docker or Docker Buildx with build contexts for the project and dashboard UI, pass JuiceFS image/version build args, tag images, push multi-arch outputs, and in release-check mode import images into microk8s. Version discovery uses git, Docker, curl, and JuiceFS CLI commands.

## State and Persistence
State is external: built Docker images, pushed registry tags, temporary tar archives during microk8s import, downloaded `juicefs-ee`, and Docker build cache. The Makefile itself persists no runtime data.

## Dependencies and Integration Points
Depends on Docker/Buildx, git, curl, microk8s for import target, GitHub/juicefs release endpoints, Dockerfiles in the same directory, and project/dashboard UI build contexts.

## Risks
Risks include network-dependent version discovery at parse time, mutable latest URLs/tags, accidental pushes, credentials/registry mismatch, multi-arch builder availability, and local `juicefs-ee` artifact churn.

## Test Signals
Signals are dry-run target review with `make -n`, successful multi-arch builds in CI, registry manifest inspection, smoke testing images in k8s, and release-check import on microk8s.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/docker/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/add-license.sh -->
# sources/control-plane/juicefs-csi-driver/hack/add-license.sh

## Purpose
License maintenance helper that checks or applies Apache license headers to source files using `addlicense`.

## Important APIs, Types, and Resources
Accepts one positional mode: `check` or `run`. Builds `addlicense` arguments with copyright holder `Juicedata Inc`, template `LICENSE_TEMPLATE`, and many ignore patterns for docs, YAML/JSON, generated/site assets, deploy, docker, scripts, and GitHub metadata.

## Control Flow
The script validates its mode, appends `-check` for check mode, runs `addlicense`, and emits a remediation message if missing headers are found. In run mode it updates files in place.

## State and Persistence
Check mode is read-only except for tool side effects; run mode mutates file headers. It relies on repository files and `LICENSE_TEMPLATE` as persistent inputs.

## Dependencies and Integration Points
Depends on Bash features despite lacking an explicit bash shebang in the snippet, `addlicense`, and repository root execution. Integrates with CI/license verification workflows.

## Risks
Risks include no shebang causing `/bin/sh` incompatibility for arrays/`[[ ]]` if executed directly, broad ignore patterns excluding files that should be licensed, and run mode touching many files.

## Test Signals
Run `bash hack/add-license.sh check`, ensure CI invokes it with bash, and test a temporary missing-header file to verify detection.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/add-license.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update-gofmt -->
# sources/control-plane/juicefs-csi-driver/hack/update-gofmt

## Purpose
Developer helper that reformats all non-vendor Go files with `gofmt -s -w`.

## Important APIs, Types, and Resources
Uses `find . -name '*.go'`, filters `/vendor/`, and pipes to `gofmt -s -w` under `set -euo pipefail`.

## Control Flow
When run from the repo root, it enumerates Go files and rewrites them in place using simplified gofmt formatting.

## State and Persistence
Persists formatting changes directly to Go source files. No separate state is stored.

## Dependencies and Integration Points
Depends on Bash, GNU-ish find/grep/xargs behavior, and the Go toolchain. Paired with `hack/verify-gofmt`.

## Risks
Risks include xargs behavior with unusual filenames, running from the wrong directory, and touching generated files if they are not under vendor.

## Test Signals
Run it then `git diff`; `hack/verify-gofmt` should report no issues afterward.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update-gofmt -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update-gomock -->
# sources/control-plane/juicefs-csi-driver/hack/update-gomock

## Purpose
Mock regeneration helper for Go interfaces used in tests.

## Important APIs, Types, and Resources
Invokes `${GOPATH}/bin/mockgen` four times to generate mocks for `k8s.io/utils/mount Interface`, `pkg/juicefs Interface`, `pkg/juicefs Jfs`, and `pkg/juicefs/mount MntInterface` into `pkg/driver/mocks`, `pkg/juicefs/mocks`, and `pkg/juicefs/mount/mocks`.

## Control Flow
The script runs mockgen with package/destination arguments and overwrites generated mock files. It exits on the first failure.

## State and Persistence
Persists generated Go mock source files. No runtime state is stored beyond filesystem outputs.

## Dependencies and Integration Points
Depends on Bash, GOPATH, installed mockgen, module import paths, and interface names. Integrates with unit tests that use generated mocks.

## Risks
Risks include GOPATH/bin missing mockgen, generator version drift changing output, stale paths after package refactors, and overwriting manual edits in generated files.

## Test Signals
Run after interface changes, review diffs, then run affected Go tests and compile all packages.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update-gomock -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update_install_script.sh -->
# sources/control-plane/juicefs-csi-driver/hack/update_install_script.sh

## Purpose
Maintenance helper that refreshes embedded webhook manifest blocks inside `scripts/juicefs-csi-webhook-install.sh` from generated deploy YAML files.

## Important APIs, Types, and Resources
Reads `deploy/webhook.yaml` and `deploy/webhook-with-certmanager.yaml`, locates marker comments `# webhook.yaml start/end` and `# webhook-with-certmanager.yaml start/end` in the install script, and rewrites the marked ranges using `head`, `tail`, `cat`, `mv`, and `chmod`.

## Control Flow
For each manifest, it copies the current deploy YAML to a temporary file, computes marker line numbers with `cat -n | grep | awk`, writes a backup replacement containing head + manifest + tail, moves it over the install script, and removes temporaries.

## State and Persistence
Persists changes to `scripts/juicefs-csi-webhook-install.sh`; creates transient `.bak`, `webhook.yaml`, and `webhook-with-certmanager.yaml` files in the working directory.

## Dependencies and Integration Points
Depends on Bash, marker comments staying unique, generated deploy YAMLs being current, POSIX text utilities, and the install script path. Integrates generated manifests with standalone webhook install tooling.

## Risks
Risks include fragile line-number math, duplicate/missing markers corrupting the install script, unquoted variables, temporary files colliding with real files, and appending via `cat >>` if stale temp files exist.

## Test Signals
Run from repo root after regenerating manifests, diff the install script, execute shellcheck if available, and smoke-test the install script in a disposable cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/update_install_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-all -->
# sources/control-plane/juicefs-csi-driver/hack/verify-all

## Purpose
Aggregate verification script for Go formatting, vetting, and linting.

## Important APIs, Types, and Resources
Computes `PKG_ROOT` with `git rev-parse --show-toplevel`, then runs `hack/verify-gofmt`, `hack/verify-govet`, and `hack/verify-golint` in order.

## Control Flow
The script stops at the first failing verifier under `set -euo pipefail`. It provides a single CI entry point for common static checks.

## State and Persistence
No repository state is intended to change, though `verify-golint` may install `golangci-lint` if missing. Failure state is expressed via exit code.

## Dependencies and Integration Points
Depends on git, Bash, Go toolchain, and the three verifier scripts. Integrates with CI and pre-submit workflows.

## Risks
Risks include verifier side effects from auto-installing lint tooling, long runtime, and order hiding later failures until earlier ones are fixed.

## Test Signals
Run `hack/verify-all` in CI and locally; success means gofmt, go vet, and golangci-lint all passed.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-all -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-gofmt -->
# sources/control-plane/juicefs-csi-driver/hack/verify-gofmt

## Purpose
Read-only formatter verifier for Go source files.

## Important APIs, Types, and Resources
Enumerates all non-vendor Go files and captures `gofmt -s -d` output. Non-empty diff output is printed and causes exit 1 with remediation text.

## Control Flow
The script runs gofmt in diff mode rather than write mode, so it reports formatting drift without mutating files.

## State and Persistence
No persistent state changes. Exit code and diff output are the state signal consumed by CI.

## Dependencies and Integration Points
Depends on Bash, Go toolchain, find/grep/xargs, and repository execution context. Paired with `hack/update-gofmt`.

## Risks
Risks are xargs edge cases for empty or unusual filenames and scanning generated Go files that may intentionally deviate.

## Test Signals
Introduce a formatting change and confirm failure; run `hack/update-gofmt` and confirm this script succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-gofmt -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-golint -->
# sources/control-plane/juicefs-csi-driver/hack/verify-golint

## Purpose
Go lint verifier that ensures `golangci-lint` exists and runs it across the repository.

## Important APIs, Types, and Resources
Checks `which golangci-lint`; if absent, installs `github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.11.4` into `$(go env GOPATH)/bin` using current `GOTOOLCHAIN`, then executes `golangci-lint run`.

## Control Flow
The script bootstraps the linter if needed, prepends GOPATH/bin to PATH, and runs the configured lint suite. It exits nonzero on lint findings or install failures.

## State and Persistence
May persist a downloaded linter binary in GOPATH/bin and module/cache downloads. It does not modify repository source.

## Dependencies and Integration Points
Depends on Bash, Go, network/module proxy access for install, golangci-lint configuration, and PATH. Integrated into `verify-all`.

## Risks
Risks include network-dependent CI, tool version changes relative to config, GOTOOLCHAIN compatibility, and installing tools during verification rather than using pinned CI images.

## Test Signals
Run in a clean environment, verify install path and lint results, and pin/cache the linter in CI for reproducibility.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-golint -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-govet -->
# sources/control-plane/juicefs-csi-driver/hack/verify-govet

## Purpose
Go vet verifier for all non-vendor packages.

## Important APIs, Types, and Resources
Runs `go vet $(go list ./... | grep -v vendor)` and prints progress messages.

## Control Flow
The script asks `go list` for packages, filters vendor, then invokes `go vet` over the resulting package list. Any vet failure stops the script.

## State and Persistence
No intended repository state changes, though Go may populate module/build caches. Exit code is the CI signal.

## Dependencies and Integration Points
Depends on Bash, Go module resolution, package compileability, and network/cache availability for dependencies. Integrated into `verify-all`.

## Risks
Risks include command-line length for very large package lists, filtering only literal `vendor`, and go vet behavior changing across Go versions.

## Test Signals
Run in CI with the project Go version; pair with unit tests for behavior that vet cannot prove.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-govet -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-cli/Dockerfile -->
# sources/control-plane/juicefs-csi-driver/juicefs-cli/Dockerfile

## Purpose
Minimal Dockerfile that packages the JuiceFS CLI in a Python base image.

## Important APIs, Types, and Resources
Uses `FROM python`, sets `JUICEFS_CLI=/bin/juicefs`, downloads `https://juicefs.com/static/juicefs` with curl, chmods it executable, verifies `juicefs version`, and sets `ENTRYPOINT ["juicefs"]`.

## Control Flow
Docker build pulls the Python base, downloads the CLI binary, validates it during build, and produces an image whose default command runs JuiceFS.

## State and Persistence
Persistent state is the built image layer containing `/bin/juicefs`. The source file stores no runtime state.

## Dependencies and Integration Points
Depends on Docker, the mutable `python` base tag, network access to juicefs.com, and curl availability in the base image. Integrates with CLI/testing workflows needing a containerized JuiceFS binary.

## Risks
Risks include unpinned base image and binary URL, no checksum verification, larger-than-needed Python base, and build breakage if curl is absent from a future base.

## Test Signals
Build the image, run `docker run --rm <image> version`, and consider digest/checksum pinning for release use.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-cli/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-csi-driver-config.example.yaml -->
# sources/control-plane/juicefs-csi-driver/juicefs-csi-driver-config.example.yaml

## Purpose
Example ConfigMap documenting the JuiceFS CSI driver runtime configuration schema and common `mountPodPatch` use cases.

## Important APIs, Types, and Resources
Defines `v1` ConfigMap `juicefs-csi-driver-config` in `kube-system` with embedded `config.yaml`. Important settings include `enableNodeSelector`, `enableNativeSidecar`, `enableSetQuota`, `enableControllerSetQuota`, `enableAutoRemoveRequestResources`, `enableAutoAbortStuckMountPod`, `enableKubeletListMountPod`, and a list-based `mountPodPatch` with PVC/node selectors, mountOptions, labels, resources, images, probes, annotations, env, volumes, initContainers, and DNS settings.

## Control Flow
The CSI driver reads `/etc/config/config.yaml` at startup. It applies global booleans to scheduling, quota, cleanup, stuck-mount handling, and kubelet list behavior, then recursively merges matching mountPodPatch entries into generated mount pod specs based on selectors.

## State and Persistence
The ConfigMap persists cluster-level driver configuration. Effective behavior persists through mounted config in controller/node pods and through generated mount pod specs derived from it.

## Dependencies and Integration Points
Depends on Kubernetes ConfigMap projection, driver config parsing/merge code, PVC and node label selectors, and template variables such as `${MOUNT_POINT}`, `${SUB_PATH}`, and `${VOLUME_ID}`. Integrates with deployment manifests mounting `/etc/config`.

## Risks
Risks include malformed YAML embedded in ConfigMap, selector patches applying too broadly, resource/image/probe changes destabilizing mount pods, and comments drifting from actual config defaults.

## Test Signals
Validate by applying a config, restarting driver pods, inspecting generated mount pods, and running config parser unit tests plus selected PVC/node selector e2e cases.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/juicefs-csi-driver-config.example.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/k8s-mod.sh -->
# sources/control-plane/juicefs-csi-driver/k8s-mod.sh

## Purpose
Kubernetes module alignment helper for updating Go module replacements to a selected Kubernetes release.

## Important APIs, Types, and Resources
Accepts a version argument with optional leading `v`, downloads the Kubernetes `go.mod` from GitHub, extracts staging module names, resolves each `k8s.io/*@kubernetes-$VERSION` module version with `go mod download -json`, adds `go mod edit -replace` entries, and finally runs `go get k8s.io/kubernetes@v$VERSION`.

## Control Flow
The script exits if no version is supplied. For a valid version, it discovers all staging modules used by Kubernetes, maps them to published pseudo/module versions, edits the local module file, and updates the Kubernetes dependency.

## State and Persistence
Persists changes to `go.mod` and likely `go.sum`; Go also updates module cache. No other state is intended.

## Dependencies and Integration Points
Depends on Bash arrays, curl access to GitHub, sed patterns matching Kubernetes go.mod replace format, Go modules, and published `kubernetes-$VERSION` module tags. Integrates with dependency upgrade workflows.

## Risks
Risks include no bash shebang despite Bash-specific arrays and `pipefail`, network/API drift, sed pattern breakage if Kubernetes go.mod format changes, partial go.mod edits after a failure, and complex replace churn.

## Test Signals
Run on a branch with a target version, review `go.mod`/`go.sum`, run `go mod tidy`, full build, unit tests, and Kubernetes-client integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/k8s-mod.sh -->
