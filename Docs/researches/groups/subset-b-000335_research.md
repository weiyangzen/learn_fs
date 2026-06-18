# subset-b-000335 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/bases/beegfs.csi.netapp.com_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/bases/beegfs.csi.netapp.com_beegfsdrivers.yaml

## Purpose
Generated Kubernetes apiextensions.k8s.io/v1 CRD for the namespaced `BeegfsDriver` API in group `beegfs.csi.netapp.com`. It is the operator's public configuration and status contract for deploying the BeeGFS CSI driver.

## Important APIs, Types, And Functions
Defines `spec.containerImageOverrides`, `spec.containerResourceOverrides`, `spec.logLevel`, `spec.nodeAffinityControllerService`, `spec.nodeAffinityNodeService`, and `spec.pluginConfig`. Status exposes Kubernetes-style `conditions`. Required fields are sparse, but nested file-system configs require `sysMgmtdHost` and node configs require `nodeList`.

## Control Flow
The API server validates objects against this schema before the controller reads them. Kustomize later applies `patches/singleton.yaml` to restrict metadata.name to `csi-beegfs-cr`.

## State And Persistence
Persisted state is the `BeegfsDriver` custom resource and its status subresource. Plugin configuration is persisted in the CR and rendered by the controller into a ConfigMap for driver pods.

## Dependencies And Integration Points
Generated from the operator API Go types with controller-gen v0.16.5. Integrated by `config/crd/kustomization.yaml`, OLM CSV descriptors, samples, and envtest setup.

## Risks And Edge Cases
The schema repeats Kubernetes core structures and is large, so drift from Go types can hide until regeneration. `beegfsClientConf` values must be strings, which is easy to violate in hand-written YAML. OpenShift form views may not render map fields reliably.

## Test Signals
Envtest loads this base CRD and validates invalid log levels. The singleton name patch is not loaded by envtest, so that constraint depends on kustomize output rather than controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/bases/beegfs.csi.netapp.com_beegfsdrivers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomization.yaml

## Purpose
Builds the BeegfsDriver CRD package for the default operator overlay.

## Important APIs, Types, And Functions
Includes the generated CRD base, leaves webhook and cert-manager strategic-merge patches commented, applies the JSON6902 singleton patch, and registers `kustomizeconfig.yaml`.

## Control Flow
`config/default` consumes this kustomization. Kustomize loads the base CRD, applies `patches/singleton.yaml` to the CRD schema, and uses the configuration file for future webhook name/namespace substitution.

## State And Persistence
No runtime state. The rendered CRD becomes persistent cluster API state when applied.

## Dependencies And Integration Points
Depends on the CRD base and patch files. It is part of the bundle/manifests generation path through `config/manifests/kustomization.yaml`.

## Risks And Edge Cases
Webhook and CA patches are intentionally disabled; enabling them requires coordinated edits here and in default overlays. The singleton patch uses JSON paths into `spec.versions[0]`, so version ordering matters.

## Test Signals
No direct test. Integration coverage is indirect through generated manifests and envtest loading the unpatched base.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomizeconfig.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomizeconfig.yaml

## Purpose
Teaches kustomize how to rewrite CRD conversion webhook service references and annotation variables.

## Important APIs, Types, And Functions
Configures `nameReference` for `spec/conversion/webhook/clientConfig/service/name`, namespace substitution for the matching namespace path, and `varReference` for metadata annotations.

## Control Flow
When webhook/cert-manager patches are enabled, kustomize uses these field specs after resources and patches are loaded.

## State And Persistence
No runtime state. It affects rendered YAML only.

## Dependencies And Integration Points
Integrated by `config/crd/kustomization.yaml`; coordinates with `webhook_in_beegfsdrivers.yaml` and `cainjection_in_beegfsdrivers.yaml`.

## Risks And Edge Cases
Field paths are inert while webhooks are disabled but must remain accurate for future conversion webhook support. Incorrect paths would render manifests that refer to the wrong service or namespace.

## Test Signals
No direct test in this subset; validation would require rendering with webhook patches enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomizeconfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/cainjection_in_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/cainjection_in_beegfsdrivers.yaml

## Purpose
Optional cert-manager CA injection patch for the BeegfsDriver CRD.

## Important APIs, Types, And Functions
Adds `cert-manager.io/inject-ca-from: $(CERTIFICATE_NAMESPACE)/$(CERTIFICATE_NAME)` to the CRD metadata.

## Control Flow
Only participates when uncommented in the CRD kustomization and cert-manager variables are enabled in the parent overlay.

## State And Persistence
No local state. When applied, cert-manager mutates the persisted CRD with a CA bundle for webhook clients.

## Dependencies And Integration Points
Depends on cert-manager, kustomize vars, and conversion webhook configuration.

## Risks And Edge Cases
Incorrect variable wiring leaves an unresolved annotation or points CA injection at the wrong Certificate. OLM comments note cert-manager is not supported in that bundle path.

## Test Signals
No direct tests; render-time validation is needed if webhook support is enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/cainjection_in_beegfsdrivers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/singleton.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/singleton.yaml

## Purpose
Makes the BeegfsDriver API a singleton by restricting CR names to `csi-beegfs-cr`.

## Important APIs, Types, And Functions
JSON6902 add operation inserts `metadata.properties.name` schema with `pattern: ^csi-beegfs-cr$`.

## Control Flow
Kustomize applies the patch to the first CRD version schema. The API server then rejects BeegfsDriver objects with any other name.

## State And Persistence
No state itself; changes persisted CRD validation behavior.

## Dependencies And Integration Points
Used by `config/crd/kustomization.yaml`. Controller and tests assume a single CR but do not enforce the name themselves.

## Risks And Edge Cases
The patch targets `/spec/versions/0`, so adding versions or reordering versions can silently patch the wrong schema. Envtest does not load this patch, leaving a coverage gap.

## Test Signals
Controller tests cover duplicate object creation but explicitly note they do not cover the patched name restriction.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/singleton.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/webhook_in_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/webhook_in_beegfsdrivers.yaml

## Purpose
Optional CRD conversion webhook patch.

## Important APIs, Types, And Functions
Sets `spec.conversion.strategy: Webhook`, references service `webhook-service` in namespace `system`, path `/convert`, and conversionReviewVersions `v1`.

## Control Flow
Inactive until uncommented in kustomization. If enabled, API server conversion requests route through the configured service.

## State And Persistence
No local state. It modifies the persisted CRD conversion configuration.

## Dependencies And Integration Points
Depends on webhook service/deployment overlays and kustomize name/namespace rewriting.

## Risks And Edge Cases
There is only one served/storage version in the current CRD, so webhook support is scaffolded but unused. Enabling without service/certs breaks CRD conversion requests.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/webhook_in_beegfsdrivers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/default/kustomization.yaml

## Purpose
Primary install overlay for deploying the operator into namespace `beegfs-csi`.

## Important APIs, Types, And Functions
Applies `namePrefix: beegfs-csi-driver-operator-`, includes CRD/RBAC/manager bases and metrics service, and carries commented hooks for webhook, cert-manager, Prometheus, and manager component config.

## Control Flow
Kustomize composes all operator resources, prefixes names, rewrites namespaces, and can inject variables if optional features are enabled.

## State And Persistence
No runtime state. Rendered resources create the operator namespace, deployment, service account, RBAC, metrics service, and CRD in the cluster.

## Dependencies And Integration Points
Used by bundle generation through `config/manifests/kustomization.yaml` and manual deployment workflows.

## Risks And Edge Cases
`bases` is an older kustomize field. Optional sections have dependencies across multiple files, so partial uncommenting can produce broken webhook or monitor installs.

## Test Signals
No direct tests; generated manifest validation and operator-sdk bundle checks cover this indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/manager_config_patch.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/default/manager_config_patch.yaml

## Purpose
Optional patch to mount controller-runtime `ControllerManagerConfig` into the manager deployment.

## Important APIs, Types, And Functions
Adds `--config=controller_manager_config.yaml`, mounts a `manager-config` ConfigMap at `/controller_manager_config.yaml`, and defines the volume.

## Control Flow
Only applies when uncommented in the default kustomization. The manager binary then reads component config on startup.

## State And Persistence
No independent state; uses a generated ConfigMap from `config/manager/kustomization.yaml`.

## Dependencies And Integration Points
Depends on `manager-config` ConfigMap and controller-runtime component config support.

## Risks And Edge Cases
Currently inactive. If enabled, command-line flags and component config can conflict, and mount path/subPath must match the binary argument.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/manager_config_patch.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/metrics_service.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/default/metrics_service.yaml

## Purpose
Exposes the operator manager metrics endpoint as a Kubernetes Service.

## Important APIs, Types, And Functions
Service `controller-manager-metrics-service` targets TCP port 8443 and selects pods labeled `control-plane: controller-manager`.

## Control Flow
Kustomize prefixes and namespaces it. Prometheus ServiceMonitor can select the service if enabled.

## State And Persistence
Cluster Service object persists virtual networking state for metrics access.

## Dependencies And Integration Points
Depends on labels in `manager.yaml` and secure metrics server configured in `main.go`.

## Risks And Edge Cases
The Service port lacks a name, while the ServiceMonitor references port `https`; rendered manifests may need a named port for Prometheus Operator compatibility.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/metrics_service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/controller_manager_config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manager/controller_manager_config.yaml

## Purpose
Scaffolded controller-runtime component configuration for the operator manager.

## Important APIs, Types, And Functions
Defines health probe address `:8081`, metrics bind address `127.0.0.1:8080`, webhook port 9443, and leader election resource name `0d697945.csi.netapp.com`.

## Control Flow
Only used if the manager config patch is enabled; otherwise runtime flags in `manager.yaml` and `main.go` determine behavior.

## State And Persistence
Stored as a generated ConfigMap when kustomize renders the manager package.

## Dependencies And Integration Points
Generated by `config/manager/kustomization.yaml` and mounted by the optional default patch.

## Risks And Edge Cases
The active deployment currently binds secure metrics to `0.0.0.0:8443`, so enabling this config would materially change metrics exposure unless reconciled.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/controller_manager_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manager/kustomization.yaml

## Purpose
Builds the operator manager deployment and generated manager ConfigMap.

## Important APIs, Types, And Functions
Includes `manager.yaml`, disables ConfigMap name suffix hashes, generates `manager-config`, and rewrites image `controller` to `ghcr.io/thinkparq/beegfs-csi-driver-operator:v1.8.0`.

## Control Flow
Kustomize loads the deployment, generates config, and applies image substitution.

## State And Persistence
No local state; rendered Deployment and ConfigMap persist in the cluster.

## Dependencies And Integration Points
Consumed by `config/default`. Image values must align with CSV `containerImage` and bundle metadata.

## Risks And Edge Cases
Image tag drift between this file and OLM CSV can publish inconsistent install paths. Disabling hash suffix makes ConfigMap names stable but requires rollout triggers elsewhere if component config changes.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/manager.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manager/manager.yaml

## Purpose
Defines the namespace and Deployment for the BeeGFS CSI driver operator manager.

## Important APIs, Types, And Functions
Runs `/manager` with `--leader-elect` and `--metrics-bind-address=0.0.0.0:8443`, sets liveness/readiness probes on 8081, passes `BEEGFS_CSI_DRIVER_NAMESPACE` via Downward API, and uses service account `controller-manager`.

## Control Flow
Kustomize namespaces/prefixes it. At runtime, `main.go` uses the namespace env var to limit the controller cache to the deployment namespace.

## State And Persistence
Deployment state persists one replica and manages Pod lifecycle. Operator process state is in-memory except Kubernetes objects it reconciles.

## Dependencies And Integration Points
Depends on RBAC, metrics service, and controller-runtime health endpoints.

## Risks And Edge Cases
The manager runs as non-root with no privilege escalation, but reconciles privileged driver resources via RBAC. Metrics are exposed on all interfaces and rely on authn/authz filters.

## Test Signals
No direct manifest test; `main.go` and envtest cover manager construction and controller registration.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/manager.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/bases/beegfs-csi-driver-operator.clusterserviceversion.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manifests/bases/beegfs-csi-driver-operator.clusterserviceversion.yaml

## Purpose
Base OLM ClusterServiceVersion metadata for publishing the BeeGFS CSI driver operator.

## Important APIs, Types, And Functions
Declares owned CRD `beegfsdrivers.beegfs.csi.netapp.com`, spec/status descriptors, provider/maintainer links, minKubeVersion 1.19.0, supported OwnNamespace install mode, and container image `ghcr.io/thinkparq/beegfs-csi-driver-operator:v1.8.0`.

## Control Flow
OLM consumes the rendered CSV from the manifests kustomization to display UI descriptors and manage operator lifecycle.

## State And Persistence
CSV is persisted by OLM and tracks install/upgrade status externally to this file.

## Dependencies And Integration Points
Must stay aligned with CRD schema, sample CRs, manager image, bundle annotations, and scorecard expectations.

## Risks And Edge Cases
`alm-examples` is empty despite samples being included elsewhere. Descriptor paths are manually extensive and can drift from CRD/API fields. `install.spec.deployments` is null in this base and relies on bundle generation overlays.

## Test Signals
Scorecard OLM tests validate bundle structure, CRD validation, resources, descriptors, and status descriptors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/bases/beegfs-csi-driver-operator.clusterserviceversion.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manifests/kustomization.yaml

## Purpose
Top-level kustomization for generating OLM bundle manifests.

## Important APIs, Types, And Functions
Includes the CSV base, default install overlay, samples, and scorecard configuration. Contains commented JSON6902 webhook cleanup for OLM-managed certificates.

## Control Flow
Operator SDK uses this path to assemble bundle manifests. Optional webhook cleanup patches would remove cert volume references because OLM mounts certs itself.

## State And Persistence
No runtime state. Rendered output becomes bundle contents and ultimately OLM-managed cluster resources.

## Dependencies And Integration Points
Integrates config/default, samples, scorecard, and CSV base.

## Risks And Edge Cases
Webhook patch comments reference container and volume indices that can become stale. Optional cert-manager paths should remain disabled for OLM.

## Test Signals
Scorecard and bundle validation consume rendered manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/prometheus/kustomization.yaml

## Purpose
Optional Prometheus overlay entry point.

## Important APIs, Types, And Functions
Includes only `monitor.yaml`.

## Control Flow
When uncommented in the default overlay, kustomize adds a ServiceMonitor to the install set.

## State And Persistence
No local state; rendered ServiceMonitor persists if the Prometheus Operator CRD exists.

## Dependencies And Integration Points
Depends on Prometheus Operator APIs and the manager metrics service.

## Risks And Edge Cases
Applying this without the ServiceMonitor CRD installed fails. The monitor's named port must match the metrics Service.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/monitor.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/prometheus/monitor.yaml

## Purpose
Defines Prometheus Operator scraping configuration for manager metrics.

## Important APIs, Types, And Functions
ServiceMonitor `controller-manager-metrics-monitor` selects `control-plane: controller-manager`, scrapes `/metrics` over HTTPS using service account token auth and TLS verification.

## Control Flow
Prometheus Operator watches ServiceMonitor and creates scrape jobs for matching Services.

## State And Persistence
ServiceMonitor persists scrape configuration in the cluster.

## Dependencies And Integration Points
Requires monitoring.coreos.com/v1, the metrics service, and controller-runtime secure metrics endpoint.

## Risks And Edge Cases
References port `https`, but the metrics Service in this subset does not name its port. `insecureSkipVerify: false` requires serving cert trust to be correct.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/monitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_editor_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_editor_role.yaml

## Purpose
End-user ClusterRole for editing BeegfsDriver resources.

## Important APIs, Types, And Functions
Grants create/delete/get/list/patch/update/watch on `beegfsdrivers` and get on `beegfsdrivers/status`.

## Control Flow
Applied as part of RBAC overlays only when included by higher-level packaging or user binding.

## State And Persistence
ClusterRole persists permissions; it does not bind users by itself.

## Dependencies And Integration Points
Targets the BeegfsDriver CRD API group.

## Risks And Edge Cases
Editor can change singleton driver spec and trigger cluster-wide driver rollout, but cannot update status.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_editor_role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_viewer_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_viewer_role.yaml

## Purpose
End-user ClusterRole for read-only BeegfsDriver access.

## Important APIs, Types, And Functions
Grants get/list/watch on `beegfsdrivers` and get on `beegfsdrivers/status`.

## Control Flow
Applied with RBAC resources and later bound by admins as needed.

## State And Persistence
ClusterRole persists read permissions only.

## Dependencies And Integration Points
Targets CRD group `beegfs.csi.netapp.com`.

## Risks And Edge Cases
No write access; status may reveal deployment health and config metadata.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/beegfsdriver_viewer_role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/kustomization.yaml

## Purpose
Assembles service account and operator runtime RBAC.

## Important APIs, Types, And Functions
Includes service account, manager role/binding, leader election role/binding, metrics auth binding, and metrics reader role.

## Control Flow
The default overlay applies these resources before the manager deployment uses the service account.

## State And Persistence
RBAC objects persist in the cluster and authorize the operator process.

## Dependencies And Integration Points
Coordinates with `manager.yaml` service account name and RBAC annotations in the controller.

## Risks And Edge Cases
End-user editor/viewer roles are not included here, so they may only appear through generated bundle metadata or separate packaging. Any service account rename requires binding subject updates.

## Test Signals
Controller envtest checks RBAC objects produced by deploy manifests, not this kustomization directly.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role.yaml

## Purpose
Namespaced Role allowing controller-runtime leader election.

## Important APIs, Types, And Functions
Grants full get/list/watch/create/update/patch/delete on ConfigMaps and Leases plus create/patch on events.

## Control Flow
Manager uses these permissions when `--leader-elect` is enabled.

## State And Persistence
Leader election records persist as ConfigMaps or Leases in the operator namespace.

## Dependencies And Integration Points
Bound to the controller-manager service account by `leader_election_role_binding.yaml`.

## Risks And Edge Cases
Permissions are broad for ConfigMaps but scoped to namespace. Lost permissions prevent manager startup leadership.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role_binding.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role_binding.yaml

## Purpose
Binds the leader election Role to the manager service account.

## Important APIs, Types, And Functions
RoleBinding `leader-election-rolebinding` references Role `leader-election-role` and subject ServiceAccount `controller-manager` in namespace `system`.

## Control Flow
Kustomize rewrites namespace/name as part of default install. Kubernetes authorization uses it during leader election calls.

## State And Persistence
RoleBinding persists the authorization relationship.

## Dependencies And Integration Points
Depends on the Role and service account resources.

## Risks And Edge Cases
Namespace placeholders must be rewritten consistently. A service account name change breaks leader election unless this binding changes too.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/leader_election_role_binding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role.yaml

## Purpose
Authorizes the metrics server to perform Kubernetes authentication and authorization reviews.

## Important APIs, Types, And Functions
ClusterRole grants create on `authentication.k8s.io/tokenreviews` and `authorization.k8s.io/subjectaccessreviews`.

## Control Flow
controller-runtime secure metrics filter uses these APIs to validate scrape requests.

## State And Persistence
ClusterRole persists cluster-wide review permissions.

## Dependencies And Integration Points
Bound to manager service account by `metrics_auth_role_binding.yaml`; used by `main.go` metrics filter provider.

## Risks And Edge Cases
Without this role, authenticated metrics requests can fail. It grants sensitive review creation but not object access.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role_binding.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role_binding.yaml

## Purpose
Binds metrics auth review permissions to the manager service account.

## Important APIs, Types, And Functions
ClusterRoleBinding `metrics-auth-rolebinding` references ClusterRole `metrics-auth-role` and ServiceAccount `controller-manager`.

## Control Flow
Authorization checks use this binding when the manager handles secure metrics requests.

## State And Persistence
ClusterRoleBinding persists the cluster-wide subject/role link.

## Dependencies And Integration Points
Depends on service account and metrics auth ClusterRole.

## Risks And Edge Cases
Namespace rewrite must place the subject in the actual install namespace.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_auth_role_binding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_reader_role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_reader_role.yaml

## Purpose
Defines read access to the manager metrics endpoint.

## Important APIs, Types, And Functions
ClusterRole `metrics-reader` grants get on non-resource URL `/metrics`.

## Control Flow
Used by Kubernetes authz checks for metrics consumers.

## State And Persistence
ClusterRole persists a reusable permission but has no subject binding in this file.

## Dependencies And Integration Points
Matches controller-runtime secure metrics endpoint.

## Risks And Edge Cases
Requires a separate binding for Prometheus or users. Without it, authenticated scrapes may be denied.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/metrics_reader_role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/role.yaml

## Purpose
Main ClusterRole for the BeeGFS CSI driver operator manager.

## Important APIs, Types, And Functions
Grants namespace object management for ConfigMaps, Secrets, ServiceAccounts, events, PVC/PV operations, apps DaemonSets/StatefulSets, BeegfsDriver resources/status/finalizers, RBAC creation/deletion/update, OpenShift privileged SCC use, CSIDriver creation/deletion, and read access to CSINodes/StorageClasses/nodes/pods.

## Control Flow
The controller uses these permissions while reconciling driver manifests and while granting driver runtime permissions.

## State And Persistence
ClusterRole persists broad operator privileges; actual runtime authorization comes from `role_binding.yaml`.

## Dependencies And Integration Points
Generated from kubebuilder RBAC markers in `beegfsdriver_controller.go` plus operator requirements.

## Risks And Edge Cases
This is intentionally high privilege. It can create RBAC and use privileged SCC, so namespace isolation and singleton enforcement matter. Some resources grant create/delete without update due to controller behavior.

## Test Signals
Envtest verifies the controller creates expected RBAC objects from deploy manifests, but authorization itself is not exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role_binding.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/role_binding.yaml

## Purpose
Binds the main manager ClusterRole to the manager service account.

## Important APIs, Types, And Functions
ClusterRoleBinding `manager-rolebinding` references ClusterRole `manager-role` and ServiceAccount `controller-manager`.

## Control Flow
Kubernetes authorizes manager API calls through this binding.

## State And Persistence
Persists cluster-wide role binding state.

## Dependencies And Integration Points
Depends on `manager-role` and service account resources; kustomize rewrites subject namespace.

## Risks And Edge Cases
Because the role is broad, an incorrect subject namespace/name can either break the operator or accidentally authorize the wrong service account.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/role_binding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/service_account.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/rbac/service_account.yaml

## Purpose
Defines the Kubernetes ServiceAccount used by the operator manager deployment.

## Important APIs, Types, And Functions
ServiceAccount `controller-manager` in placeholder namespace `system`.

## Control Flow
Kustomize namespaces/prefixes it and `manager.yaml` references it by name.

## State And Persistence
ServiceAccount persists identity and token projection behavior for the manager pod.

## Dependencies And Integration Points
Bound by leader election, metrics auth, and manager role bindings.

## Risks And Edge Cases
Changing the name requires updating all bindings and the Deployment.

## Test Signals
Envtest controller tests check that service accounts from driver deployment manifests are created, but not this install service account directly.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/rbac/service_account.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/beegfs_v1_beegfsdriver.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/samples/beegfs_v1_beegfsdriver.yaml

## Purpose
Minimal example BeegfsDriver custom resource for typical OpenShift deployment.

## Important APIs, Types, And Functions
Uses apiVersion `beegfs.csi.netapp.com/v1`, kind `BeegfsDriver`, required singleton name `csi-beegfs-cr`, controller/node affinities excluding `node.openshift.io/os_id=rhcos`, and commented image/log/plugin config sections.

## Control Flow
Users apply or edit this sample to create the singleton CR. The controller then renders driver resources from its spec.

## State And Persistence
The sample becomes the persistent desired state for the operator once applied.

## Dependencies And Integration Points
References the CRD schema and is included by samples kustomization and bundle generation.

## Risks And Edge Cases
Comments contain a CRD filename typo (`beegfsdriver` singular). The sample is OpenShift-biased and requires non-RHCOS nodes with BeeGFS client prerequisites.

## Test Signals
No direct test; envtest helper builds a full CR programmatically.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/beegfs_v1_beegfsdriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/samples/kustomization.yaml

## Purpose
Collects sample custom resources for bundle/manifests generation.

## Important APIs, Types, And Functions
Includes `beegfs_v1_beegfsdriver.yaml` and retains kubebuilder scaffold marker.

## Control Flow
Used by `config/manifests/kustomization.yaml` to include sample CRs.

## State And Persistence
No runtime state unless samples are applied to a cluster.

## Dependencies And Integration Points
Depends on the BeegfsDriver sample and CRD.

## Risks And Edge Cases
Adding more samples without updating CSV `alm-examples` may leave OLM UI examples incomplete.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/bases/config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/bases/config.yaml

## Purpose
Base Operator SDK scorecard configuration.

## Important APIs, Types, And Functions
Defines scorecard.operatorframework.io/v1alpha3 Configuration with one parallel stage and an initially empty tests list.

## Control Flow
Scorecard kustomization patches tests into `/stages/0/tests`.

## State And Persistence
No runtime state; rendered into bundle test config.

## Dependencies And Integration Points
Patched by basic and OLM scorecard patch files.

## Risks And Edge Cases
If patches fail, scorecard runs no tests despite a valid base config.

## Test Signals
The file exists solely to configure scorecard tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/bases/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/kustomization.yaml

## Purpose
Builds the operator scorecard test configuration.

## Important APIs, Types, And Functions
Includes base config and applies JSON6902 patches for basic and OLM scorecard suites.

## Control Flow
Kustomize appends test entries to the base Configuration before bundle generation.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on `patches/basic.config.yaml` and `patches/olm.config.yaml`.

## Risks And Edge Cases
Patch target must match the base object exactly. Scorecard image version is pinned in patches.

## Test Signals
Enables scorecard coverage for spec checks and OLM bundle validation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/basic.config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/basic.config.yaml

## Purpose
Adds the basic scorecard spec test.

## Important APIs, Types, And Functions
JSON6902 add operation appends `scorecard-test basic-check-spec` using image `quay.io/operator-framework/scorecard-test:v1.19.1`.

## Control Flow
Applied by scorecard kustomization; scorecard later runs the configured entrypoint.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on the Operator Framework scorecard test image.

## Risks And Edge Cases
Pinned image can age relative to operator-sdk versions.

## Test Signals
Provides basic spec validation signal for the bundle.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/basic.config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/olm.config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/olm.config.yaml

## Purpose
Adds OLM-focused scorecard validation tests.

## Important APIs, Types, And Functions
Appends tests for bundle validation, CRDs with validation, CRDs with resources, spec descriptors, and status descriptors, all using `quay.io/operator-framework/scorecard-test:v1.19.1`.

## Control Flow
Kustomize appends all entries to the parallel scorecard stage.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Validates consistency among CSV, CRDs, and bundle resources.

## Risks And Edge Cases
Descriptor-heavy CSVs can pass stale semantic descriptions if paths remain syntactically valid.

## Test Signals
Direct scorecard signal for OLM bundle readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/olm.config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller.go -->
# sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller.go

## Purpose
Implements the controller-runtime reconciler for the singleton BeegfsDriver CR and materializes the BeeGFS CSI driver deployment.

## Important APIs, Types, And Functions
`BeegfsDriverReconciler.Reconcile` drives all reconciliation. Helpers include `newConfigMap`, `newSecret`, `newTLS`, `setCommonObjectMetadata`, `setResourceVersionAnnotations`, `setImages`, `setNodeResources`, `setControllerResources`, `getImageStringWithOverride`, `setLogLevel`, and `setNodeAffinity`. `finalizerClusterResourceDeletion` handles cluster-scoped cleanup.

## Control Flow
Reconcile fetches the CR, loads clean driver manifests from `deploy/k8s`, computes status from existing StatefulSet/DaemonSet readiness, updates status only if changed, manages a finalizer, creates or updates ConfigMap/Secrets/RBAC/CSIDriver, and then creates or updates driver StatefulSet and DaemonSet. Pod templates receive ConfigMap/Secret resource-version annotations to force rollouts on config/auth/TLS changes.

## State And Persistence
Persistent cluster state includes namespaced ConfigMap, ConnAuth Secret, TLS Secret, service account/Roles/RoleBindings, StatefulSet, DaemonSet, cluster-scoped ClusterRoles/ClusterRoleBindings, and CSIDriver. Status conditions persist controller/node service readiness. Cluster-scoped resources cannot be owner-referenced, so the finalizer deletes them manually.

## Dependencies And Integration Points
Depends on operator API types, deploy/k8s manifest getters, Kubernetes apps/core/rbac/storage APIs, controller-runtime client/manager, and sigs.k8s.io/yaml for plugin config serialization.

## Risks And Edge Cases
Status is computed before resources are reconciled, so first reconcile can report not-created before creating objects. Secrets are not reconciled after creation by design. Cluster-scoped updates lack owner references and rely on finalizer correctness. Image parsing splits on the first colon, which can mishandle registry strings with ports.

## Test Signals
Envtest verifies object creation, owner refs for namespaced resources, finalizer addition, cluster-scoped cleanup, status unreadiness, ConfigMap/Secret rollout annotation updates, invalid logLevel validation, and helper behavior for image overrides/log level/string containment.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller_test.go -->
# sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller_test.go

## Purpose
Ginkgo/Gomega integration and helper tests for the BeegfsDriver controller.

## Important APIs, Types, And Functions
Tests use `getValidCRWithNoFields`, `getValidCRWithAllFields`, and `getContainerImageForName`. Specs cover resource creation, finalizers, status, deletion cleanup, rollout-triggering updates, invalid CRs, and helper functions.

## Control Flow
Each integration test creates a random namespace and a populated BeegfsDriver CR, then uses Eventually against envtest API server state to observe reconciliation. Modification contexts update pluginConfig or Secrets and assert resource versions/annotations change.

## State And Persistence
Creates transient namespaces, CRs, Kubernetes resources, and cluster-scoped objects inside envtest. Random namespace state avoids collisions but debug output suggests historical duplicate namespace issues.

## Dependencies And Integration Points
Depends on deploy/k8s manifest getters, operator API types, envtest client, Ginkgo/Gomega, and controller-runtime.

## Risks And Edge Cases
The deletion test has a type switch branch for non-pointer `rbacv1.ClusterRoleBinding`, while deploy resources likely use pointers, risking missed assertions. Singleton name patch is explicitly not tested because envtest loads only CRD bases.

## Test Signals
High-value coverage of reconcile side effects and rollout triggers. Missing coverage for RBAC authorization, Prometheus/OLM manifests, and kustomize-only CRD patches.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/beegfsdriver_controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/suite_test.go -->
# sources/control-plane/beegfs-csi-driver/operator/controllers/suite_test.go

## Purpose
Bootstraps the envtest suite for controller integration tests.

## Important APIs, Types, And Functions
`TestAPIs` runs the Ginkgo suite. `BeforeSuite` starts envtest with CRDs from `../config/crd/bases`, registers the BeegfsDriver scheme, creates a controller-runtime manager, registers the reconciler, and starts the manager in a goroutine. `AfterSuite` cancels and stops envtest.

## Control Flow
The test process starts an API server/etcd, initializes client/manager, runs specs, then tears down after all tests.

## State And Persistence
All state is ephemeral envtest state. No real cluster resources persist.

## Dependencies And Integration Points
Uses controller-runtime envtest, client-go scheme, Ginkgo/Gomega, zap logging, and operator API registration.

## Risks And Edge Cases
Only CRD bases are loaded, so kustomize patches such as singleton name are absent. Manager startup is asynchronous and depends on shared global context.

## Test Signals
Provides the foundation for all controller integration tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_deploy_all_examples.sh -->
# sources/control-plane/beegfs-csi-driver/operator/hack/minikube_deploy_all_examples.sh

## Purpose
Development helper to deploy a BeeGFS test file system and all Kubernetes examples into Minikube.

## Important APIs, Types, And Functions
Sets `BEEGFS_VERSION=7.4.6` and `BEEGFS_SECRET=mysecret`, applies a test BeeGFS FS manifest with envsubst, waits for pod `beegfs-fs-1-0`, exposes service with `minikube service`, rewrites `/etc/beegfs` config, creates static provisioning directories via `beegfs-ctl`, substitutes management IP into examples, and applies examples.

## Control Flow
Script exits on errors, polls pod status up to 36 times, prints debug information on timeout, then mutates host/minikube BeeGFS config and applies examples.

## State And Persistence
Creates cluster resources, modifies host `/etc/beegfs/connAuth` and `beegfs-client.conf`, creates BeeGFS directories, and edits files under `../examples/k8s/all` in place.

## Dependencies And Integration Points
Requires kubectl, envsubst, minikube, docker, sudo, BeeGFS client utilities, mounted `/etc/beegfs`, and test/example manifests.

## Risks And Edge Cases
Marked non-idempotent. It mutates local example YAMLs and system BeeGFS config. `sudo echo` is ineffective for privilege by itself, but piping through sudo tee writes the connAuth file.

## Test Signals
Manual/minikube smoke path only; no automated test.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_deploy_all_examples.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_install_driver_prerequisites.sh -->
# sources/control-plane/beegfs-csi-driver/operator/hack/minikube_install_driver_prerequisites.sh

## Purpose
Installs BeeGFS user-space prerequisites into a Minikube node for development testing.

## Important APIs, Types, And Functions
Runs `minikube ssh` commands to reset apt source list snippets, install wget, add BeeGFS 7.4.6 GPG key and focal repository, install `beegfs-utils`, and download a default `beegfs-client.conf`.

## Control Flow
Sequential shell script with `set -euo pipefail`; any failed SSH/package command aborts.

## State And Persistence
Mutates package sources and `/etc/beegfs/beegfs-client.conf` inside the Minikube environment.

## Dependencies And Integration Points
Depends on apt-based Minikube image, network access to beegfs.io and GitHub, and the companion deploy script.

## Risks And Edge Cases
Deletes all `/etc/apt/sources.list.d/*` entries in Minikube, which may remove unrelated repos. Pins BeeGFS focal repo regardless of host/minikube distro.

## Test Signals
Manual setup helper only.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_install_driver_prerequisites.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/set_openshift_min_version.sh -->
# sources/control-plane/beegfs-csi-driver/operator/hack/set_openshift_min_version.sh

## Purpose
Appends OpenShift minimum version metadata to generated bundle artifacts.

## Important APIs, Types, And Functions
Sets `OPENSHIFT_VERSIONS="\"v4.11\""`, appends `com.redhat.openshift.versions` to `bundle/metadata/annotations.yaml`, and appends a LABEL to `bundle.Dockerfile`.

## Control Flow
Straight-line POSIX shell append operations.

## State And Persistence
Mutates bundle output files in place by appending lines.

## Dependencies And Integration Points
Intended for operator bundle publishing workflows.

## Risks And Edge Cases
Not idempotent; repeated runs append duplicate annotations/labels. Uses `echo "\n..."`, whose newline handling varies by shell.

## Test Signals
No tests; manual release helper.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/set_openshift_min_version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/test_catalog_source.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/hack/test_catalog_source.yaml

## Purpose
OpenShift development CatalogSource for testing operator catalog images and upgrade flows.

## Important APIs, Types, And Functions
Defines operators.coreos.com/v1alpha1 CatalogSource `netapp-operators` in `openshift-marketplace`, sourceType `grpc`, image placeholder `docker.repo.eng.netapp.com/<username>/beegfs-csi-driver-operator-catalog:<vX.X.X>`, and registry polling every 30s.

## Control Flow
When applied, OLM watches the catalog image and refreshes it on the poll interval.

## State And Persistence
Creates persistent OpenShift marketplace catalog state until deleted.

## Dependencies And Integration Points
Depends on OLM/OpenShift and a pushed catalog image.

## Risks And Edge Cases
Contains internal registry placeholders and old NetApp naming. Polling with imagePullPolicy Always is useful for development but noisy for long-lived clusters.

## Test Signals
Manual OLM integration testing helper.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/test_catalog_source.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/main.go -->
# sources/control-plane/beegfs-csi-driver/operator/main.go

## Purpose
Entry point for the BeeGFS CSI driver operator manager.

## Important APIs, Types, And Functions
Registers Kubernetes and BeegfsDriver schemes, parses flags for metrics/probes/leader election/HTTP2, creates controller-runtime manager, configures namespace-scoped cache from `BEEGFS_CSI_DRIVER_NAMESPACE`, secure metrics with authn/authz filters, webhook port 9443, health/readiness checks, and registers `BeegfsDriverReconciler`.

## Control Flow
Process initializes logging, optionally disables HTTP/2 in TLS config, builds manager, registers controller and health checks, then starts until signal cancellation.

## State And Persistence
Runtime state is in-memory manager/cache/controller state. Persistent effects happen through the reconciler.

## Dependencies And Integration Points
Integrates controller-runtime cache, metrics server, webhook server, healthz, zap logging, and operator API scheme. Deployment passes namespace env var via Downward API.

## Risks And Edge Cases
If namespace env var is absent, the cache watches all namespaces. Secure metrics require RBAC for TokenReview/SubjectAccessReview. HTTP/2 is disabled by default due to documented CVEs.

## Test Signals
No direct unit test of main; envtest separately instantiates a manager and registers the reconciler.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs.go

## Purpose
Core BeeGFS CSI driver initialization and internal volume model.

## Important APIs, Types, And Functions
Defines `beegfs`, `beegfsVolume`, `stripePatternConfig`, `permissionsConfig`, and `reqParameters`. Exports `NewBeegfsDriver` and `NewBeegfsDriverSanity`. Key helpers are `newBeegfsDriver`, `Run`, `newBeegfsVolume`, `newBeegfsVolumeFromID`, `getDefaultClientConfTemplatePath`, and permission mode methods.

## Control Flow
Driver creation verifies required strings, verifies the BeeGFS client module for real driver mode, reads client config template, parses plugin config/connAuth/TLS files, creates controller service data dir, initializes identity/node/controller servers, and later runs a non-blocking gRPC server.

## State And Persistence
Persists controller service data directory on disk with 0750 permissions. `beegfsVolume` computes host and BeeGFS-root paths for mount dirs, client config, connAuth/TLS files, CSI metadata, and volume directories.

## Dependencies And Integration Points
Depends on operator API config types, config parsing helpers, filesystem abstraction `fs/fsutil`, identity/node/controller server constructors, and BeeGFS URL parsing helpers.

## Risks And Edge Cases
Default client config discovery depends on host/container path assumptions. `vendorVersion` is package-global and mutable during initialization. Special Unix permission bits require custom conversion because Go `os.FileMode` encodes them differently.

## Test Signals
Unit tests cover initialization failure cases, permission helpers, volume path construction, URL-derived volume construction, and default client config path discovery with afero.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl.go

## Purpose
Abstracts BeeGFS 7 and BeeGFS 8 command-line tooling for directory creation, stat, and stripe pattern operations.

## Important APIs, Types, And Functions
`beegfsCtlExecutorInterface` defines the driver-facing CTL operations. `beegfsCtlDispatcher` detects v7/v8 per volume. `beegfsCtlExecutorV8` wraps `beegfs`; `beegfsCtlExecutorV7` wraps `beegfs-ctl`. Shared helpers include `newBeeGFSCtlExecutor`, `detectCTLVersion`, `execBeeGFSCmd`, `constructSetPatternForVolumeArgs`, `constructCreateDirForVolumeArgs`, and typed ctl errors.

## Control Flow
Startup checks whether either v7 or v8 CTL can run. Each operation re-detects the target file system version by trying v8 `node list` then v7 `--listnodes`. Directory creation stats first, builds parent directories from root to target, tolerates already-exists errors, and wraps failures with volume context.

## State And Persistence
No internal persistent state. External side effects are BeeGFS directory creation and stripe pattern changes. V8 commands pass mgmtd/auth/TLS flags from volume config; v7 commands use generated client config files.

## Dependencies And Integration Points
Depends on `os/exec`, BeeGFS CLI binaries, command output strings, connAuth/TLS files written near mount dirs, and controller/node server code that calls these operations.

## Risks And Edge Cases
Error classification is string-matched against stdout/stderr and can drift with CLI versions. Version detection on every command adds overhead but supports upgrades without restart. Special permission bits are intentionally dropped from CTL create args and must be handled elsewhere if needed.

## Test Signals
Unit tests cover v7/v8 set-pattern args, create-directory args including uid/gid/mode, and typed error wrapping. Actual CLI execution is not unit-tested.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl_test.go

## Purpose
Unit tests for BeeGFS CTL argument construction and error types.

## Important APIs, Types, And Functions
Tests `constructSetPatternForVolumeArgs`, `constructCreateDirForVolumeArgs`, and error constructors `newCtlNotExistError`, `newCtlExistError`, `newCtlConnAuthError`.

## Control Flow
Table-driven tests compare generated argument slices for v7/v8 cases and verify typed errors preserve expected Error strings and unwrap with `errors.As`.

## State And Persistence
No persistent state and no real CLI execution.

## Dependencies And Integration Points
Uses Go testing, reflect.DeepEqual, and github.com/pkg/errors wrapping.

## Risks And Edge Cases
Coverage is limited to pure helpers. It does not validate `execBeeGFSCmd` output parsing against real BeeGFS binaries.

## Test Signals
Strong signal for command argument stability, especially v7/v8 flag differences and special-permission truncation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_ctl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_test.go

## Purpose
Unit tests for BeeGFS driver initialization helpers, permission handling, volume path construction, and default config discovery.

## Important APIs, Types, And Functions
Defines `errPermissionFs` to simulate permission errors with afero. Tests `NewBeegfsDriver` failure modes, `permissionsConfig` methods, `newBeegfsVolume`, `newBeegfsVolumeFromID`, and `getDefaultClientConfTemplatePath`.

## Control Flow
Tests replace package filesystem globals with in-memory or permission-error filesystems, construct table-driven cases, and compare expected structs/modes/paths.

## State And Persistence
Uses in-memory afero state; no host filesystem persistence.

## Dependencies And Integration Points
Depends on operator API config defaults, afero filesystem abstraction, path helpers, and BeeGFS URL helpers.

## Risks And Edge Cases
Real `NewBeegfsDriver` path also verifies the BeeGFS client module and creates servers, so tests focus on failure cases rather than successful real-driver startup. Global filesystem substitution can leak if tests are expanded carelessly.

## Test Signals
Covers bad/missing required inputs, unreadable config template, permission bit conversion including sticky/setgid/setuid bits, path derivation, and default path search order.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_test.go -->
