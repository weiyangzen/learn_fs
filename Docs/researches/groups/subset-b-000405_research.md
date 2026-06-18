# subset-b-000405 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/default-setting.yaml -->
# sources/control-plane/longhorn/chart/templates/default-setting.yaml

Purpose: renders the `longhorn-default-setting` ConfigMap whose `default-setting.yaml` payload seeds Longhorn Setting CR values at install or upgrade time. It maps many Helm `.Values.defaultSettings.*` knobs into the kebab-case setting names consumed by Longhorn Manager, while intentionally omitting null or invalid values so the controller can keep built-in defaults.

Important APIs/types/functions: Kubernetes `ConfigMap`, Helm `include "release_namespace"`, `include "longhorn.labels"`, `kindIs "invalid"` null checks, `quote`, `join`, `compact`, and `include "longhorn.multiTypeSetting"` for settings that may be plain values or per-data-engine JSON. Key value groups cover replica scheduling, backup/restore limits, snapshot integrity, V1/V2 data engines, SPDK/ublk tuning, logging, CSI topology/capacity, and manager URL behavior.

Control flow: the template emits one ConfigMap unconditionally, then conditionally writes individual lines inside the embedded YAML block when the corresponding value is present. Windows/Rancher cluster mode merges `.Values.global.cattle.windowsCluster.defaultSetting` toleration and node selector defaults with user-provided Longhorn defaults using semicolon-separated strings. Multi-type settings are delegated to the helper so chart consumers can pass data-engine-specific JSON without each setting duplicating parsing logic.

State and persistence: rendered data becomes Kubernetes ConfigMap state, but Longhorn Manager typically copies these defaults into Setting CRs; some settings, notably `manager-url`, persist beyond Helm value removal and require explicit CR cleanup. Storage, backup, data-engine, and snapshot choices influence persistent volume data layout and runtime controller behavior after startup.

Dependencies/integration: depends on the chart helper templates, `values.yaml`, Longhorn Manager's default-setting loader, Kubernetes ConfigMap delivery, and Longhorn Setting CR semantics. It is integrated with `deployment-driver.yaml` because an externally protected `manager-url` can break driver deployment links, and with `storageclass.yaml` because several defaults overlap with StorageClass parameters.

Risks: type handling is subtle because booleans, strings, nulls, and JSON-like multi-type values are mixed. A rendered but malformed setting can make Longhorn reject or misapply configuration. Settings affecting V2 data engine CPU masks, hugepages, storage networking, or data-engine enablement can destabilize clusters if changed while volumes are attached. Because absent values are omitted rather than reset, Helm users may assume a rollback clears persisted Setting CRs when it does not.

Test signals: run `helm template` with null defaults, explicit booleans, explicit zero-like strings, and multi-type JSON values; verify the embedded YAML parses and contains only intended keys. Add cases for Rancher Windows cluster merging, `managerUrl` protected-ingress warnings, V2 data engine settings, and upgrade paths where existing Setting CRs retain values after Helm values become null.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/default-setting.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/deployment-driver.yaml -->
# sources/control-plane/longhorn/chart/templates/deployment-driver.yaml

Purpose: deploys the single-replica `longhorn-driver-deployer` Deployment that waits for Longhorn Manager and then runs `longhorn-manager deploy-driver` to create or update CSI sidecars and driver components.

Important APIs/types/functions: Kubernetes `Deployment`, init container, manager image command `longhorn-manager -d deploy-driver`, Helm image registry coalescing, env vars `POD_NAMESPACE`, `NODE_NAME`, `SERVICE_ACCOUNT`, `KUBELET_ROOT_DIR`, CSI sidecar image variables, CSI replica-count variables, `GOCOVERDIR`, priority class, tolerations, node selectors, image pull secrets, and `longhorn.timezoneEnv`.

Control flow: an init container loops on `http://longhorn-backend:9500/v1` until it receives HTTP 200. The main container then starts the manager binary in deploy-driver mode, passes the manager image and internal manager URL, and conditionally exports CSI image, kubelet root, anti-affinity, replica-count, and coverage settings. Scheduling fields merge global, Longhorn-driver-specific, and Rancher Windows node placement settings.

State and persistence: the Deployment itself is persistent desired state. The deployer mutates cluster state by creating system-managed CSI objects outside this template. Optional coverage mode writes to host path `/go-cover-dir/`, and the driver deployment depends on service account and RBAC permissions from sibling templates.

Dependencies/integration: depends on the `longhorn-backend` service, manager image, CSI image values from `values.yaml`, `longhorn-service-account`, Role/RoleBinding permissions, private registry/image pull secret handling, and Longhorn Manager deploy-driver implementation. It also interacts with default settings such as `manager-url` and CSI storage capacity/topology settings.

Risks: the init wait loop has no explicit deadline, so a missing backend service can leave pods stuck indefinitely. Any registry, tag, or private-secret mismatch blocks driver deployment. A manager URL that resolves to an auth-protected external endpoint can cause internal JSON clients to receive HTML redirects. Node selector/toleration merges can accidentally unschedule the deployer, and coverage hostPath should not be enabled in production.

Test signals: template with default and custom registries, all CSI image overrides, Rancher Windows cluster placement, private registry strings and lists, coverage enabled, and custom kubelet root. In-cluster smoke tests should confirm the deployer reaches the backend, creates CSI components, and fails visibly on unavailable manager service or bad manager URL.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/deployment-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/deployment-ui.yaml -->
# sources/control-plane/longhorn/chart/templates/deployment-ui.yaml

Purpose: deploys the Longhorn UI frontend and its service, with optional OpenShift Route/service/oauth-proxy support. It exposes the UI through `longhorn-frontend` and points UI traffic at the internal manager API service.

Important APIs/types/functions: Kubernetes `Deployment`, `Service`, optional OpenShift `Route`, optional OpenShift service with serving cert annotation, `longhorn-ui` container, optional `oauth-proxy` sidecar, env vars `LONGHORN_MANAGER_IP` and `LONGHORN_UI_PORT`, service type handling including `Rancher-Proxy`, LoadBalancer fields, image pull secrets, affinity, priority class, tolerations, and node selectors.

Control flow: when OpenShift and route settings are enabled, the template first emits a reencrypt Route and TLS-serving service. It always emits the UI Deployment, conditionally adds the oauth-proxy sidecar and TLS secret volume for OpenShift route mode, mounts emptyDir locations for nginx writable paths, and then creates the `longhorn-frontend` service on port 80 targeting the container's named `http` port.

State and persistence: desired state lives in Deployment, Service, optional Route, and generated OpenShift serving-cert secret references. Runtime state is ephemeral nginx cache/config/run data in `emptyDir`; UI state is not persisted here. The service can become externally reachable if NodePort or LoadBalancer is selected.

Dependencies/integration: depends on Longhorn UI image values, `longhorn-ui-service-account`, `longhorn-backend:9500`, OpenShift OAuth proxy image values when enabled, ingress/HTTPRoute templates that target `longhorn-frontend`, and network policies that may restrict UI ingress. Rancher-Proxy service labeling integrates with Rancher cluster-service discovery.

Risks: OpenShift route mode renders `image: ""` if no oauth-proxy repository is configured, which is invalid at runtime. The oauth proxy uses a literal cookie secret placeholder and a SAR requiring delete on Longhorn settings, so production OpenShift deployments need careful auth validation. LoadBalancer fields are referenced even though some are not documented near the visible defaults. NodePort null rendering must be accepted by the target API server.

Test signals: render ClusterIP, Rancher-Proxy, NodePort, LoadBalancer, and OpenShift route combinations. Verify `longhorn-frontend` selects UI pods, nginx writable mounts work with restricted filesystems, oauth-proxy starts with a real image and cert secret, and ingress/HTTPRoute/network-policy combinations allow expected UI traffic only.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/deployment-ui.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/extra-objects.yaml -->
# sources/control-plane/longhorn/chart/templates/extra-objects.yaml

Purpose: provides an escape hatch for chart consumers to append arbitrary Kubernetes manifests through `.Values.extraObjects`.

Important APIs/types/functions: Helm `range`, document separator `---`, `toYaml`, and `tpl` evaluated against the root chart context. The rendered objects can be any Kubernetes resource shape supplied by the user.

Control flow: for each entry in `extraObjects`, the template starts a new YAML document, serializes the object to YAML, and evaluates it as a template with access to chart values, release metadata, and helper functions.

State and persistence: this template itself holds no fixed state, but any supplied object can create persistent cluster resources, secrets, roles, workloads, or storage. Helm will track rendered objects as part of the release output.

Dependencies/integration: depends entirely on user-provided values and Helm's `tpl` behavior. It can integrate with any chart object by referencing names such as the release namespace, service accounts, services, labels, or secrets.

Risks: `tpl` gives user values full templating power, so malformed or unsafe extra objects can break rendering, bypass chart conventions, or introduce privileged resources. There is no schema-level guard here for namespace, labels, RBAC scope, or resource collisions.

Test signals: render with an empty list, a simple ConfigMap, a templated object referencing `release_namespace`, and an intentionally invalid object to confirm failure mode. Check that extra objects appear as separate documents and do not corrupt adjacent manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/extra-objects.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/httproute.yaml -->
# sources/control-plane/longhorn/chart/templates/httproute.yaml

Purpose: optionally exposes the Longhorn UI through Gateway API `HTTPRoute` instead of the older Ingress API.

Important APIs/types/functions: Gateway API `gateway.networking.k8s.io/v1` `HTTPRoute`, `.Values.httproute.enabled`, `parentRefs`, `hostnames`, path match `type` and `value`, annotations, labels, and backendRef to `longhorn-frontend` port 80.

Control flow: when enabled, the template renders one `longhorn-httproute`. It copies configured parent references with defaults for group and kind, optionally emits hostnames, then creates a single rule matching the configured path and forwarding to the frontend service.

State and persistence: persistent state is the HTTPRoute object. It does not create Gateways, TLS certs, or Services; those must exist separately. Runtime routing state is controlled by the installed Gateway controller.

Dependencies/integration: depends on Gateway API CRDs and a compatible Gateway controller, a `longhorn-frontend` service from `deployment-ui.yaml`, and user-provided `parentRefs` that point to existing Gateway listeners. It may coexist with, or replace, `ingress.yaml` depending on values.

Risks: rendering `gateway.networking.k8s.io/v1` fails if the cluster lacks the CRD or only supports older Gateway versions. Empty `parentRefs` may leave controller-specific route attachment behavior ambiguous. No TLS or auth is configured here, so exposure security is delegated to the Gateway.

Test signals: `helm template` with disabled/enabled routes, multiple parentRefs, cross-namespace parentRefs, hostnames, Exact and PathPrefix matching. Cluster tests should confirm Accepted/ResolvedRefs conditions and that `longhorn-frontend:80` receives traffic.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/httproute.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/ingress.yaml -->
# sources/control-plane/longhorn/chart/templates/ingress.yaml

Purpose: optionally exposes the Longhorn UI through Kubernetes `networking.k8s.io/v1` Ingress.

Important APIs/types/functions: Kubernetes `Ingress`, `.Values.ingress.enabled`, `ingressClassName`, primary host, `extraHosts`, TLS hosts and `tlsSecret`, path/pathType, annotation rendering, and backend service `longhorn-frontend` port 80.

Control flow: when enabled, the template emits a single Ingress. It conditionally adds the legacy `ingress.kubernetes.io/secure-backends` annotation, copies user annotations, sets an ingress class if supplied, emits one rule for the main host plus one rule per extra host, and optionally emits one TLS block covering the same host list.

State and persistence: persistent state is the Ingress object and any referenced TLS secret. It does not create the frontend service or ingress controller. Ingress controller runtime state decides actual load-balancer, certificates, and routing behavior.

Dependencies/integration: depends on `longhorn-frontend` from `deployment-ui.yaml`, optional TLS secrets from `tls-secrets.yaml` or external cert managers, and the selected ingress controller. Network policies for UI ingress are tied to `.Values.ingress.enabled` and `.Values.networkPolicies.type`.

Risks: default host `sslip.io` is a placeholder and may not be meaningful without a concrete IP/host strategy. `secureBackends` uses an old annotation key that may not affect modern controllers. Enabling ingress without TLS or auth can expose the Longhorn UI broadly. Extra host and TLS lists must stay aligned with certificates.

Test signals: render default disabled state, single host, extra hosts, TLS enabled, custom annotations, and custom ingressClassName. Validate with controller-specific dry runs and ensure the UI network policy admits the chosen ingress controller pods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/ingress.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/backing-image-data-source-network-policy.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/backing-image-data-source-network-policy.yaml

Purpose: optionally restricts ingress to pods labeled `longhorn.io/component: backing-image-data-source`.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, `podSelector`, `policyTypes: Ingress`, and allowed `from` pod selectors for manager, instance manager, backing image manager, and peer backing image data source pods.

Control flow: when network policies are enabled, the template emits one ingress-only policy. It allows all ports from four intra-namespace Longhorn component selectors and denies other ingress to matching backing-image data-source pods by default.

State and persistence: persistent state is the NetworkPolicy object. It does not create pods or labels; policy enforcement depends on the cluster CNI implementation.

Dependencies/integration: depends on consistent labels applied by Longhorn Manager to backing-image data-source pods and related system-managed components. It complements the instance-manager and backing-image-manager policies.

Risks: label drift immediately breaks data-source downloads or synchronization. The policy does not include namespace selectors, so sources are same-namespace pod selectors by Kubernetes semantics. It also does not specify ports, so allowed sources can reach any exposed port on selected pods.

Test signals: with network policy enabled, verify backing-image creation and recovery workflows. Confirm traffic from manager, instance-manager, backing-image-manager, and peer data-source pods succeeds, while unrelated namespace pods are denied by the CNI.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/backing-image-data-source-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/backing-image-manager-network-policy.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/backing-image-manager-network-policy.yaml

Purpose: optionally restricts ingress to pods labeled `longhorn.io/component: backing-image-manager`.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, backing-image-manager `podSelector`, ingress-only policy type, and allowed source selectors for manager, instance manager, backing image manager, and backing image data source pods.

Control flow: when enabled, one policy is rendered. It selects backing-image-manager pods and admits ingress from the Longhorn components that coordinate backing image file distribution and status.

State and persistence: the NetworkPolicy persists in the namespace and changes CNI-enforced pod connectivity. No storage state is directly stored here, but failures affect backing image files used by volume provisioning.

Dependencies/integration: depends on Longhorn's system-managed pod labels and the CNI's NetworkPolicy support. It works with the data-source and instance-manager policies to permit backing image traffic inside Longhorn.

Risks: a too-narrow selector set can break backing image operations, especially if future Longhorn components introduce new labels or paths. No port restrictions are present, so allowed pods receive broad ingress access.

Test signals: enable policies and create, sync, and delete backing images. Inspect denied traffic from unrelated pods and allowed traffic among manager, instance-manager, backing-image-manager, and data-source pods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/backing-image-manager-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/instance-manager-networking.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/instance-manager-networking.yaml

Purpose: optionally restricts ingress to `longhorn.io/component: instance-manager` pods, which host Longhorn engine and replica processes.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, instance-manager `podSelector`, ingress policy, and source selectors for manager, peer instance managers, backing-image managers, and backing-image data-source pods.

Control flow: enabling network policies renders a single ingress-only policy selecting instance-manager pods. It admits traffic from Longhorn control-plane and data-plane helper pods that need to manage or synchronize instances.

State and persistence: policy state is stored in Kubernetes. It affects runtime communication for engines/replicas and can indirectly affect volume availability and rebuilds.

Dependencies/integration: depends on Longhorn labels for instance managers and related pods, plus CNI support. It is a core piece of the chart's optional network isolation because many Longhorn data-path operations traverse instance-manager pods.

Risks: missing a required source label can interrupt volume attachment, rebuild, or backing image flows. The policy does not restrict ports, so all ports exposed by instance-manager pods are reachable from allowed selectors. NetworkPolicy behavior may be ineffective on CNIs that do not enforce it.

Test signals: exercise volume attach/detach, rebuild, snapshot, backup, and backing image paths with policies enabled. Confirm unexpected pods cannot connect to instance-manager endpoints while Longhorn-managed pods still can.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/instance-manager-networking.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/manager-network-policy.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/manager-network-policy.yaml

Purpose: optionally restricts ingress to Longhorn Manager pods labeled `app: longhorn-manager`.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, manager `podSelector`, ingress-only policy, and allowed sources including manager peers, UI, CSI plugin, Longhorn recurring job pods, Longhorn job-task pods, and driver deployer pods.

Control flow: when network policies are enabled, the template emits one policy selecting manager pods. The allowed `from` list uses pod label selectors and match expressions to admit the main actors that call the manager API.

State and persistence: persistent state is the NetworkPolicy. It protects the manager API surface but can affect Longhorn control loops and system jobs if selectors do not match running pods.

Dependencies/integration: depends on labels from manager DaemonSet, UI Deployment, CSI plugin, recurring job objects, job-task pods, and driver deployer Deployment. It integrates with services that expose manager pods, including the backend service used by UI and driver deployer.

Risks: any label change in Longhorn-managed jobs or CSI pods can block manager API access. There are no port constraints, so allowed sources can reach any manager pod port. External monitoring or support tools are not admitted unless they run under matching labels or separate policies are added.

Test signals: with policies enabled, verify UI, CSI provisioning/attach, driver deployment, recurring jobs, and Longhorn job tasks can all call the manager API. Run a negative test from an unlabeled pod and observe denial.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/manager-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/recovery-backend-network-policy.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/recovery-backend-network-policy.yaml

Purpose: optionally adds an ingress policy for Longhorn recovery backend pods.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, selector `longhorn.io/recovery-backend: longhorn-recovery-backend`, ingress policy type, and TCP port 9503.

Control flow: if network policies are enabled, one NetworkPolicy is emitted. It selects recovery backend pods and allows ingress to TCP 9503 without a source restriction.

State and persistence: policy state persists in Kubernetes. Recovery backend runtime state is outside this template, but availability of port 9503 is controlled by this rule.

Dependencies/integration: depends on the recovery backend service in `services.yaml` and labels on recovery backend pods. It relies on the CNI's interpretation of a ports-only ingress rule.

Risks: because no `from` clause is specified, any source allowed by namespace/CNI defaults can reach port 9503 on selected pods. This may be intentional for recovery paths, but it is less restrictive than the manager and backing-image policies.

Test signals: enable network policies and verify recovery backend health and recovery workflows through service port 9503. Confirm non-9503 ports are denied and decide whether arbitrary source access to 9503 is acceptable for the cluster profile.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/recovery-backend-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/ui-frontend-network-policy.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/ui-frontend-network-policy.yaml

Purpose: optionally restricts ingress to Longhorn UI pods when both network policies and chart-managed Ingress are enabled.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, `.Values.ingress.enabled`, `.Values.networkPolicies.type`, UI `podSelector`, distribution-specific source selectors for `rke1`, `rke2`, and `k3s`, and TCP ports 8000/80 for the k3s/Traefik path.

Control flow: the template renders only when policies are enabled, ingress is enabled, and `type` is non-empty. It selects UI pods and then chooses exactly one source selector block based on the distribution type. The k3s branch also emits port constraints for 8000 and 80.

State and persistence: persistent state is the NetworkPolicy. It controls which ingress-controller pods can reach Longhorn UI pods behind the frontend service.

Dependencies/integration: depends on ingress controller namespace labels and pod labels matching Rancher/Kubernetes distribution conventions. It is coupled to `ingress.yaml`, not `httproute.yaml`, and to the UI labels in `deployment-ui.yaml`.

Risks: unsupported or mistyped distribution values render a policy with an ingress item but no `from` content, which can produce invalid or overly broad/empty behavior depending on YAML output and API validation. Only k3s adds port restrictions; rke1/rke2 allow all UI pod ports from matching controllers. Custom ingress controllers are not supported by this template.

Test signals: render for `k3s`, `rke2`, `rke1`, empty, and invalid types. In-cluster, verify the selected ingress controller reaches the UI while unrelated pods cannot, and add custom-policy coverage for non-default ingress controllers.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/ui-frontend-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/webhook-network-policy.yaml -->
# sources/control-plane/longhorn/chart/templates/network-policies/webhook-network-policy.yaml

Purpose: optionally adds ingress policy for Longhorn admission webhook pods.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, selector `longhorn.io/admission-webhook: longhorn-admission-webhook`, ingress policy type, and TCP port 9502.

Control flow: when network policies are enabled, the template emits one policy that selects admission webhook pods and allows ingress on TCP 9502 without restricting sources.

State and persistence: persistent state is a NetworkPolicy object. It affects Kubernetes API server or aggregator reachability to the webhook service, but webhook configuration objects are defined elsewhere.

Dependencies/integration: depends on the webhook service in `services.yaml`, labels on webhook pods, and CNI policy enforcement. It is deliberately less source-restrictive because API server source addresses are cluster-dependent.

Risks: open source access to port 9502 is broader than component-specific policies. Tightening it incorrectly could break API server admission calls because API server traffic may not carry pod labels or may originate from host network addresses.

Test signals: enable policies and create/update Longhorn CRs that trigger admission. Verify webhook service access from the API server and denial of non-9502 ports on webhook pods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/network-policies/webhook-network-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/postupgrade-job.yaml -->
# sources/control-plane/longhorn/chart/templates/postupgrade-job.yaml

Purpose: runs a Helm post-upgrade hook job that invokes `longhorn-manager post-upgrade` after chart upgrade.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, Helm hook annotations `post-upgrade` and `hook-delete-policy`, `activeDeadlineSeconds: 900`, `backoffLimit: 1`, manager image command, `POD_NAMESPACE`, timezone env, image pull secrets, priority class, service account, tolerations, and node selectors.

Control flow: Helm creates the job after an upgrade. The pod runs the manager image with `post-upgrade`, restarts on failure, and is deleted before future hook creation or after success according to hook policy.

State and persistence: the hook job is temporary cluster state, but the command can perform persistent Longhorn upgrade migrations or cleanup. Successful hook resources are deleted, so logs may be transient.

Dependencies/integration: depends on the manager image, `longhorn-service-account`, RBAC permissions, namespace fieldRef, private registry configuration, and manager upgrade implementation. Scheduling follows manager toleration and node-selector values.

Risks: failure blocks or degrades Helm upgrade flows, and hook deletion can remove diagnostics after success. `activeDeadlineSeconds` may be too short on very large or unhealthy clusters. Image pull or scheduling failures prevent post-upgrade reconciliation.

Test signals: `helm upgrade --dry-run` should render the hook; real upgrade tests should verify the job starts, completes within deadline, uses expected image pull secrets, and leaves Longhorn resources in the target version state.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/postupgrade-job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/preupgrade-job.yaml -->
# sources/control-plane/longhorn/chart/templates/preupgrade-job.yaml

Purpose: conditionally runs Longhorn's pre-upgrade checker as a Helm pre-upgrade hook before chart upgrade proceeds.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, Helm `pre-upgrade` hook annotations, `.Values.preUpgradeChecker.jobEnabled`, `.Values.preUpgradeChecker.upgradeVersionCheck`, manager command `pre-upgrade`, privileged security context, hostPath mount `/proc`, `LONGHORN_DISTRO`, `POD_NAMESPACE`, image pull secrets, service account, tolerations, and node selectors.

Control flow: the template renders only when both pre-upgrade checker flags are true. Helm creates the hook before upgrade; the pod runs `longhorn-manager pre-upgrade`, mounts host `/proc`, restarts on failure, and has a 900 second active deadline with one retry.

State and persistence: the job is temporary, but it reads live cluster/host state and can prevent unsafe upgrade progression. It does not persist chart-managed objects beyond hook lifecycle.

Dependencies/integration: depends on manager image compatibility with the old cluster, RBAC from `longhorn-service-account`, host `/proc` access, and Longhorn Manager's pre-upgrade checks. The value comments note GitOps tools may need this disabled.

Risks: privileged host `/proc` access broadens security requirements. GitOps controllers that cannot handle blocking Helm hooks may fail unless the job is disabled. Disabling the job also disables a safety check that Longhorn recommends keeping enabled.

Test signals: render enabled and disabled combinations, run upgrades across supported versions, confirm the hook fails on intentionally unsafe preconditions, and verify Argo CD/GitOps flows when `jobEnabled` is false.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/preupgrade-job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/priorityclass.yaml -->
# sources/control-plane/longhorn/chart/templates/priorityclass.yaml

Purpose: creates the `longhorn-critical` PriorityClass used by Longhorn workloads to reduce eviction risk under node pressure.

Important APIs/types/functions: Kubernetes `scheduling.k8s.io/v1` `PriorityClass`, `globalDefault: false`, `preemptionPolicy: PreemptLowerPriority`, value `1000000000`, chart labels, and the name referenced from `values.yaml` via the `defaultSettings.priorityClass` anchor and component priority defaults.

Control flow: the template always renders one PriorityClass with a fixed name and high numeric priority.

State and persistence: PriorityClass is cluster-scoped persistent scheduling policy. Deleting or renaming it affects pods that reference `longhorn-critical`.

Dependencies/integration: component templates such as UI, driver, and hook jobs conditionally set `priorityClassName` from values that default to this name. Longhorn default settings can also propagate priority to system-managed components.

Risks: very high priority with preemption can evict lower-priority workloads to preserve Longhorn availability. Name collisions occur if multiple releases install the same chart into one cluster. Cluster-scoped resource ownership can be awkward for namespace-scoped Helm releases.

Test signals: render and install into clusters with and without existing `longhorn-critical`; confirm pods using default priorities schedule; test uninstall/upgrade ownership behavior for the cluster-scoped object.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/priorityclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/psp.yaml -->
# sources/control-plane/longhorn/chart/templates/psp.yaml

Purpose: optionally creates legacy PodSecurityPolicy permissions for privileged Longhorn pods on Kubernetes versions that still support PSP.

Important APIs/types/functions: `policy/v1beta1` `PodSecurityPolicy`, namespace `Role`, `RoleBinding`, `.Values.enablePSP`, privileged and allowPrivilegeEscalation flags, `SYS_ADMIN`, hostPID, hostPath volumes, and subjects `longhorn-service-account` plus `default`.

Control flow: when `enablePSP` is true, the template emits the PSP, a Role granting `use` on that PSP, and a RoleBinding to the Longhorn and default service accounts in the release namespace.

State and persistence: PSP and RBAC objects persist in the cluster/namespace and govern pod admission for matching service accounts. PSP itself is cluster-scoped, while the role and binding are namespace-scoped.

Dependencies/integration: depends on Kubernetes PSP API availability, which was removed in Kubernetes 1.25. It supports Longhorn workloads needing privileged operations, hostPID, capabilities, and hostPath volumes.

Risks: enabling this on modern clusters fails because `policy/v1beta1/PodSecurityPolicy` is gone. Granting the `default` service account use of a privileged PSP expands privilege beyond Longhorn-managed pods. PSP is deprecated and should not be confused with Pod Security Admission labels.

Test signals: render with `enablePSP` false and true; install only on a PSP-capable cluster; verify Longhorn privileged pods admit; confirm modern clusters require the value off or replacement Pod Security Admission configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/psp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/registry-secret.yaml -->
# sources/control-plane/longhorn/chart/templates/registry-secret.yaml

Purpose: optionally creates a Docker registry pull secret for Longhorn images from `.Values.privateRegistry`.

Important APIs/types/functions: Kubernetes `Secret` of type `kubernetes.io/dockerconfigjson`, `.Values.privateRegistry.createSecret`, `.Values.privateRegistry.registrySecret`, Helm `fail` for non-string secret names, `template "secret"`, labels, and release namespace.

Control flow: if secret creation is enabled and a registry secret name is provided, the template validates that the name is a string, then emits a Secret whose `.dockerconfigjson` is generated by the chart helper.

State and persistence: persistent state is a namespaced Secret containing registry credentials. Workload templates reference this or global image pull secrets through `imagePullSecrets`.

Dependencies/integration: depends on `values.yaml` private registry fields for registry URL, user, password, and secret name, plus helper template implementation. It integrates with image pull secret rendering in UI, driver, and hook job templates.

Risks: credentials are stored base64-encoded in Kubernetes Secret data and need normal secret-management controls. If `registrySecret` is used as a list for imagePullSecrets, this template fails because it requires a string when creating a secret. Missing or malformed helper output breaks image pulls.

Test signals: render with create disabled, enabled with string secret, and enabled with invalid non-string secret. Validate decoded `.dockerconfigjson` and run an image pull from the private registry.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/registry-secret.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/role.yaml -->
# sources/control-plane/longhorn/chart/templates/role.yaml

Purpose: grants Longhorn Manager broad namespace-scoped permissions over core, apps, batch, policy, coordination, RBAC, and discovery resources.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `Role`, resource groups `""`, `apps`, `batch`, `policy`, `coordination.k8s.io`, `rbac.authorization.k8s.io`, and `discovery.k8s.io`, all with wildcard verbs.

Control flow: the template always renders one Role named by `include "longhorn.name"` in the release namespace. Rules are static and not value-gated.

State and persistence: the Role persists namespace-scoped authorization policy. It does not bind itself until `rolebinding.yaml` links it to `longhorn-service-account`.

Dependencies/integration: required by Longhorn Manager, driver deployer, upgrade hooks, and uninstall job to create and mutate pods, services, configmaps, PVCs, workloads, jobs, leases, local RBAC, and endpoint slices.

Risks: wildcard verbs across many namespace resources are powerful; compromise of the bound service account gives extensive namespace control. The role is namespace-scoped, so any cluster-scoped permissions Longhorn needs must come from other templates not in this work item.

Test signals: use `kubectl auth can-i --as system:serviceaccount:<ns>:longhorn-service-account` for core Longhorn operations. Run install, upgrade, CSI deployment, recurring jobs, and uninstall to catch missing resource verbs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/rolebinding.yaml -->
# sources/control-plane/longhorn/chart/templates/rolebinding.yaml

Purpose: binds the chart's namespace Role to `longhorn-service-account`.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `RoleBinding`, `roleRef` to the Role named by `include "longhorn.name"`, and a ServiceAccount subject in the release namespace.

Control flow: the template always renders one RoleBinding. Kubernetes then grants the service account all permissions defined by `role.yaml`.

State and persistence: persistent namespace RBAC binding state. It is the connection point that makes the broad Role effective for Longhorn Manager and related jobs.

Dependencies/integration: depends on `serviceaccount.yaml` creating `longhorn-service-account` and `role.yaml` creating the referenced Role. Workloads using this service account include driver deployer and upgrade/uninstall jobs.

Risks: if the namespace helper changes or a subchart uses namespaceOverride unexpectedly, subject and role namespaces must remain aligned. Any over-permission in the Role is inherited here.

Test signals: template namespace override cases and verify RoleBinding subject namespace. Use `kubectl auth can-i` as the service account after install.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/rolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/serviceaccount.yaml -->
# sources/control-plane/longhorn/chart/templates/serviceaccount.yaml

Purpose: creates service accounts for Longhorn core workloads, UI, and support bundle operations.

Important APIs/types/functions: Kubernetes `ServiceAccount`, names `longhorn-service-account`, `longhorn-ui-service-account`, and `longhorn-support-bundle`, shared `.Values.serviceAccount.annotations`, OpenShift OAuth redirect annotation, and release namespace helper.

Control flow: the template always emits three ServiceAccounts. For the UI service account, if OpenShift and route mode are enabled, it adds `serviceaccounts.openshift.io/oauth-redirectreference.primary`, creating an annotations map if one was not already supplied.

State and persistence: persistent service account identity in the release namespace. Tokens and projected credentials are managed by Kubernetes. Annotations affect OpenShift OAuth integration.

Dependencies/integration: `longhorn-service-account` is bound by `rolebinding.yaml` and used by driver deployer and hook jobs. `longhorn-ui-service-account` is used by the UI Deployment and OpenShift oauth proxy. `longhorn-support-bundle` is used by support bundle components elsewhere in the chart.

Risks: shared annotations apply to all three service accounts, which can be too broad for IAM or workload-identity integrations. OpenShift route annotation assumes the route name `longhorn-ui`, while the route value is configurable, creating a mismatch if `.Values.openshift.ui.route` is changed.

Test signals: render with and without annotations, OpenShift disabled, and OpenShift route renamed. Verify RoleBinding targets only the core service account and UI OAuth redirects match the actual Route name.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/serviceaccount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/servicemonitor.yaml -->
# sources/control-plane/longhorn/chart/templates/servicemonitor.yaml

Purpose: optionally creates a Prometheus Operator ServiceMonitor for scraping Longhorn Manager metrics.

Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor`, `.Values.metrics.serviceMonitor.enabled`, additional labels, annotations, `sampleLimit`, selector `app: longhorn-manager`, namespace selector, endpoint port `manager`, interval, scrapeTimeout, relabelings, and metricRelabelings.

Control flow: when enabled, the template emits one ServiceMonitor in the release namespace. Optional scrape fields are rendered only when non-empty; `sampleLimit` uses a `with` block, so zero omits the field.

State and persistence: persistent CRD state consumed by Prometheus Operator. It does not itself scrape metrics; Prometheus instances select ServiceMonitors based on labels and operator configuration.

Dependencies/integration: depends on Prometheus Operator CRDs, a manager Service with port named `manager`, labels from manager service templates outside this subset, and any Prometheus selector conventions supplied via additional labels.

Risks: installing without the ServiceMonitor CRD fails. Incorrect additional labels can make Prometheus ignore the monitor. Endpoint port name must match the manager service. Aggressive intervals or missing sample limits can increase Prometheus load.

Test signals: render disabled/enabled, custom labels and annotations, interval/timeout, relabeling arrays, metric relabeling arrays, and nonzero sampleLimit. In-cluster, verify Prometheus target discovery and scrape success.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/servicemonitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/services.yaml -->
# sources/control-plane/longhorn/chart/templates/services.yaml

Purpose: creates ClusterIP services for Longhorn admission webhook and recovery backend components.

Important APIs/types/functions: Kubernetes `Service`, names `longhorn-admission-webhook` and `longhorn-recovery-backend`, selectors `longhorn.io/admission-webhook` and `longhorn.io/recovery-backend`, service ports 9502/9503, and targetPort names `admission-wh` and `recov-backend`.

Control flow: the template always emits two services separated by a YAML document boundary. Each service selects pods by Longhorn-managed labels and exposes one named port.

State and persistence: persistent service objects provide stable DNS and virtual IPs for webhook and recovery backend traffic. No endpoint state is stored here beyond Kubernetes-managed endpoint slices.

Dependencies/integration: depends on workloads outside this subset that create pods with matching labels and named container ports. Network policy templates for webhook and recovery backend use the same labels and ports.

Risks: label or targetPort-name drift yields services with no ready endpoints or broken port mapping. These services are always rendered even if corresponding pods are disabled elsewhere, which can confuse health checks unless endpoints are validated.

Test signals: after install, check service endpoints/endpointslices for both services, validate port names match containers, and exercise webhook admission and recovery backend calls through service DNS.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/services.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/storageclass.yaml -->
# sources/control-plane/longhorn/chart/templates/storageclass.yaml

Purpose: optionally creates a ConfigMap containing the default Longhorn StorageClass manifest for Longhorn Manager or install logic to apply.

Important APIs/types/functions: Kubernetes `ConfigMap`, `.Values.persistence.createStorageClass`, embedded `storageclass.yaml`, StorageClass `storage.k8s.io/v1`, provisioner `driver.longhorn.io`, default-class annotation, volume expansion, reclaim policy, volume binding mode, replica count, stale replica timeout, filesystem/mkfs parameters, migratable, NFS options, backing image parameters, recurring job selector, data locality, disk/node/share-manager selectors, tolerations, unmap behavior, revision counter, data engine, and backup target name.

Control flow: if enabled, the template emits one ConfigMap. Inside it, StorageClass parameters are always or conditionally inserted based on persistence values. The actual StorageClass is not a top-level resource in this template; it is stored as a YAML string.

State and persistence: the ConfigMap persists desired StorageClass YAML. The eventual StorageClass influences persistent volume provisioning, reclaim behavior, replica count, data engine, and backup target linkage.

Dependencies/integration: depends on Longhorn Manager or install routines that read the `longhorn-storageclass` ConfigMap and create/update the real StorageClass. It ties directly to values in `values.yaml` and to CSI driver deployment from `deployment-driver.yaml`.

Risks: because the StorageClass is embedded YAML, template quoting mistakes can produce a ConfigMap that renders but later fails when applied. `recurringJobSelector` stringification of a list is sensitive to JSON/YAML formatting. Backing image parameters are not quoted, so null or complex strings must be tested carefully. The `dataEngine` parameter is nested under the `disableRevisionCounter` condition, so disabling that value can also omit dataEngine.

Test signals: render with createStorageClass false/true, custom annotations, backing image enabled, recurring job selector, selectors/tolerations, v2 data engine, and empty optional fields. Parse the embedded `storageclass.yaml` and validate it with `kubectl apply --dry-run=server`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/tls-secrets.yaml -->
# sources/control-plane/longhorn/chart/templates/tls-secrets.yaml

Purpose: optionally creates TLS secrets for chart-managed UI Ingress.

Important APIs/types/functions: Kubernetes `Secret` type `kubernetes.io/tls`, `.Values.ingress.enabled`, `.Values.ingress.secrets`, secret `name`, `key`, `certificate`, `b64enc`, release namespace, and chart labels.

Control flow: if ingress is enabled, the template iterates over configured secrets and emits one TLS secret per entry, followed by a YAML document separator. Certificate and key values are base64-encoded directly from values.

State and persistence: persistent Kubernetes Secret state stores TLS private keys and certificates. Ingress objects can reference these secrets through `.Values.ingress.tlsSecret`.

Dependencies/integration: depends on `ingress.yaml` when TLS is enabled, and on users supplying correctly paired PEM key/certificate content. It may coexist with cert-manager or external secret management if no inline secrets are provided.

Risks: storing PEM material in Helm values exposes secrets in release history unless mitigated. A mismatch between secret names here and `ingress.tlsSecret` leaves Ingress without the intended certificate. Empty or malformed certificate/key values still render base64 strings but fail controller validation.

Test signals: render with ingress disabled, ingress enabled with no secrets, and one or more secrets. Decode generated data and validate certificate/key pair; verify Ingress TLS uses the expected secret name.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/tls-secrets.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/uninstall-job.yaml -->
# sources/control-plane/longhorn/chart/templates/uninstall-job.yaml

Purpose: runs a Helm pre-delete hook job that invokes `longhorn-manager uninstall --force` before chart deletion.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, Helm hook annotations `pre-delete` and hook delete policy, manager image command `uninstall --force`, env `LONGHORN_NAMESPACE`, image pull secrets, priority class, service account, restartPolicy `Never`, tolerations, and node selectors.

Control flow: Helm creates the job before release deletion. The pod runs the manager uninstall command using the current namespace from fieldRef, does not restart, and is cleaned up before hook creation or after success according to hook policy.

State and persistence: the job is temporary, but the command intentionally mutates and removes Longhorn-managed state. It may interact with Longhorn's deleting confirmation setting and CR cleanup behavior.

Dependencies/integration: depends on manager image, `longhorn-service-account`, RBAC, private registry settings, and live Longhorn resources. Scheduling follows manager placement values.

Risks: `--force` makes the hook powerful; accidental Helm deletion can trigger destructive cleanup if Longhorn safeguards are satisfied. RestartPolicy `Never` plus backoffLimit means failures may require manual intervention. Image pull failure during uninstall can leave resources behind.

Test signals: uninstall dry-run rendering, controlled uninstall in a disposable cluster with and without attached volumes, image pull secret validation, and verification that expected CRs/finalizers are removed or preserved according to Longhorn uninstall policy.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/uninstall-job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/validate-psp-install.yaml -->
# sources/control-plane/longhorn/chart/templates/validate-psp-install.yaml

Purpose: contains a disabled Helm validation block intended to fail rendering when PSP is enabled on clusters without the PSP API.

Important APIs/types/functions: commented Helm `lookup`, `.Values.enablePSP`, `.Capabilities.APIVersions.Has "policy/v1beta1/PodSecurityPolicy"`, and `fail`.

Control flow: because every line is commented, the template currently emits no resources and performs no validation. If uncommented, it would first check cluster RBAC lookup availability, then fail when PSP is requested but unavailable.

State and persistence: no Kubernetes state is created. Its only intended effect would be render-time validation.

Dependencies/integration: relates to `psp.yaml` and Kubernetes version compatibility. The use of `lookup` would require Helm rendering against a live cluster rather than purely offline templating.

Risks: keeping the block commented means `enablePSP: true` can render an unsupported `policy/v1beta1` resource and fail later at install time. Un-commenting it would make offline template rendering and restricted RBAC contexts more complex.

Test signals: verify current `helm template` output contains no objects from this file. If validation is re-enabled, test offline rendering, live clusters with and without PSP API, and users lacking permission for the `lookup` call.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/templates/validate-psp-install.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/values.yaml -->
# sources/control-plane/longhorn/chart/values.yaml

Purpose: provides the default configuration surface for the Longhorn Helm chart. It defines global image and scheduling defaults, network policy mode, component images, service exposure, StorageClass defaults, upgrade-checker controls, CSI options, Longhorn default settings, backupstore defaults, private registry settings, component-specific placement/resources/logging, ingress/HTTPRoute/OpenShift/metrics options, PSP toggles, coverage, and arbitrary extra objects.

Important APIs/types/functions: YAML values consumed by all chart templates. Important anchors include `defaultSettings.priorityClass: &defaultPriorityClassNameRef "longhorn-critical"` reused by `longhornManager`, `longhornDriver`, and `longhornUI`. Value groups include `global`, `networkPolicies`, `image.longhorn`, `image.csi`, `image.openshift`, `service`, `persistence`, `preUpgradeChecker`, `csi`, `defaultSettings`, `defaultBackupStore`, `privateRegistry`, component sections, `ingress`, `httproute`, `enablePSP`, `namespaceOverride`, `serviceAccount`, `metrics.serviceMonitor`, `openshift`, `enableGoCoverDir`, and `extraObjects`.

Control flow: values do not execute themselves but drive conditional rendering across templates. Null `~` values frequently mean "do not render this setting, let Longhorn defaults apply." Boolean and string defaults selectively render Services, Jobs, ConfigMaps, Ingress, HTTPRoute, NetworkPolicy, Registry Secret, PSP, ServiceMonitor, and StorageClass payloads.

State and persistence: Helm stores these values in release state, and rendered objects create persistent Kubernetes state. Longhorn Setting CRs can persist values independently after Helm changes. StorageClass, backup, data engine, replica, scheduling, network, and uninstall-confirmation values can materially affect persistent Longhorn data and workloads.

Dependencies/integration: this file is the primary integration contract for the chart templates in this work item and for other Longhorn templates outside it. It depends on helper templates for image registry precedence, labels, namespace override, secret generation, time zone env, and multi-type setting rendering. It also documents external dependencies such as Prometheus Operator CRDs, Gateway API CRDs, OpenShift routes/oauth proxy, ingress controllers, private registries, and Kubernetes/Longhorn feature support.

Risks: the value surface is large and mixes nulls, booleans, quoted booleans, JSON strings, arrays, and maps. Mis-typed settings can render valid YAML that Longhorn later rejects. Several defaults expose powerful behavior: high PriorityClass, privileged components, broad RBAC, optional network policies off by default, optional UI exposure, and destructive uninstall hooks. Experimental V2 data engine/SPDK settings require careful hardware and workload validation. Inline secrets for registry or TLS can leak through Helm release history.

Test signals: schema/lint tests should cover type expectations for every section. Render matrix tests should include default install, private registry, Windows/Rancher cluster placement, PSP on/off, network policies by type, ingress/HTTPRoute, OpenShift route, ServiceMonitor, StorageClass variants, V2 data engine, backupstore defaults, and extra objects. Upgrade tests should confirm settings that persist outside Helm are documented and reset procedures work.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/azurite/azurite-backupstore.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/azurite/azurite-backupstore.yaml

Purpose: provides a Kustomize base for a test Azure Blob-compatible backupstore using Azurite plus a placeholder Longhorn credential secret.

Important APIs/types/functions: Kubernetes `Secret` `azblob-secret` in `longhorn-system`, `apps/v1` `Deployment` `longhorn-test-azblob` in `default`, container image `mcr.microsoft.com/azure-storage/azurite:3.33.0`, container port 10000, and `Service` `azblob-service` with `sessionAffinity: ClientIP`.

Control flow: applying the manifest creates an empty credential secret for Longhorn and a single Azurite pod exposed by a ClusterIP service on port 10000. Users or tests must populate secret data and configure Longhorn's backup target to point at the service.

State and persistence: the Azurite deployment has no volume, so blob data is container-local/ephemeral and lost when the pod is replaced. The secret is persistent but initially has empty data.

Dependencies/integration: depends on the Azurite image, Kubernetes DNS for `azblob-service.default`, and Longhorn backup target configuration using Azure-compatible credentials in `longhorn-system`. The paired kustomization includes this file.

Risks: this is not production durable because no persistent volume backs Azurite. Empty secret data means Longhorn backups will fail until credentials/certs are populated. Service lives in `default` while the Longhorn secret lives in `longhorn-system`, so namespace assumptions are fixed.

Test signals: `kubectl apply -k` should create the deployment, service, and secret. Populate secret data, set Longhorn backup target to the Azurite endpoint, create a backup, restore it, and verify data disappears after deleting/recreating the Azurite pod.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/azurite/azurite-backupstore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/azurite/kustomization.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/azurite/kustomization.yaml

Purpose: Kustomize entry point for the Azurite backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` with one resource, `azurite-backupstore.yaml`.

Control flow: `kubectl apply -k` or `kustomize build` reads this file and includes the Azurite manifest as the complete resource set for the base.

State and persistence: no runtime state is stored here; it determines which resources Kustomize emits.

Dependencies/integration: depends on the adjacent Azurite manifest path. It can be overlaid by higher-level Kustomize directories for namespace, patches, or secret data.

Risks: with only a single resource and no namespace transformer, the hard-coded namespaces in the resource file remain authoritative. Renaming or moving the manifest breaks the base.

Test signals: run `kustomize build sources/control-plane/longhorn/deploy/backupstores/base/azurite` and verify it emits the secret, deployment, and service from the resource file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/azurite/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/cifs/cifs-backupstore.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/cifs/cifs-backupstore.yaml

Purpose: provides a Kustomize base for a test CIFS/Samba backupstore and placeholder credentials in both Longhorn and workload namespaces.

Important APIs/types/functions: two `Secret` objects named `cifs-secret` in `longhorn-system` and `default`, `Deployment` `longhorn-test-cifs`, image `chanow/samba:latest`, ports 139/445, env vars `EXPORT_PATH`, `CIFS_DISK_IMAGE_SIZE_MB`, `CIFS_USERNAME`, `CIFS_PASSWORD`, privileged security context with `SYS_ADMIN` and `DAC_READ_SEARCH`, `emptyDir` volume mounted at `/opt/backupstore`, Samba args, and headless `Service` `longhorn-test-cifs-svc`.

Control flow: applying the manifest creates empty secrets, starts one privileged Samba container, reads username/password from the default-namespace secret, exports `/opt/backupstore` as share `backupstore`, and exposes SMB ports through a headless service.

State and persistence: backup data is stored on `emptyDir`, so it is ephemeral per pod lifecycle. Secrets persist but start empty and must be populated with base64 credentials.

Dependencies/integration: depends on the Samba image behavior and secret keys `CIFS_USERNAME` and `CIFS_PASSWORD`. Longhorn must be configured to use the CIFS endpoint and the `longhorn-system` credential secret. The default namespace secret is needed by the Samba server pod itself.

Risks: `chanow/samba:latest` and `imagePullPolicy: Always` make test behavior non-reproducible. The container is privileged with elevated capabilities. Empty credentials block startup or login. Headless service and SMB ports may behave differently across clusters and network policies.

Test signals: populate both secrets, apply the kustomization, confirm Samba listens on 139/445, configure Longhorn CIFS backup target, create/restore a backup, and verify data loss after pod recreation due to `emptyDir`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/cifs/cifs-backupstore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/cifs/kustomization.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/cifs/kustomization.yaml

Purpose: Kustomize entry point for the CIFS backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` referencing `cifs-backupstore.yaml`.

Control flow: Kustomize includes the single CIFS manifest when building or applying this base.

State and persistence: no runtime state is stored directly. It controls resource inclusion for the CIFS test backupstore.

Dependencies/integration: depends on the adjacent CIFS manifest. Overlays can patch image, namespaces, secrets, service type, or persistence.

Risks: hard-coded namespaces in the included resource remain unless overlays patch them. Moving the resource file breaks the kustomization.

Test signals: run `kustomize build` for the directory and ensure the output includes both secrets, the Samba deployment, and the headless service.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/cifs/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/minio/kustomization.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/minio/kustomization.yaml

Purpose: Kustomize entry point for the MinIO backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` referencing `minio-backupstore.yaml`.

Control flow: Kustomize includes the MinIO manifest as the entire base output.

State and persistence: no runtime state is stored here. Resource inclusion determines whether MinIO test backupstore objects are emitted.

Dependencies/integration: depends on the adjacent MinIO manifest and any overlays that populate secrets or persistence.

Risks: the base inherits hard-coded namespaces and empty secrets from the resource file. Renames or path changes require updating the kustomization.

Test signals: run `kustomize build sources/control-plane/longhorn/deploy/backupstores/base/minio` and verify the output includes the MinIO secrets, deployment, and service.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/minio/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/minio/minio-backupstore.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/minio/minio-backupstore.yaml

Purpose: provides a Kustomize base for a test S3-compatible backupstore using MinIO plus placeholder AWS-style credentials/certificates.

Important APIs/types/functions: `Secret` `minio-secret` in `default` and `longhorn-system`, `Deployment` `longhorn-test-minio`, image `minio/minio:RELEASE.2022-02-01T18-00-14Z`, `emptyDir` storage, certificate secret volume keys `AWS_CERT` and `AWS_CERT_KEY`, env keys `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, command creating `/storage/backupbucket` and certificate symlinks, container port 9000, and `Service` `minio-service`.

Control flow: applying the manifest creates empty secrets, starts MinIO with a pre-created `backupbucket`, mounts TLS material from the secret, reads root credentials from the same secret, and exposes port 9000 through a service with ClientIP session affinity.

State and persistence: object data is stored on `emptyDir` and is lost with pod replacement. Secrets are persistent but initially empty and must contain credentials and TLS certificate data.

Dependencies/integration: depends on the pinned MinIO image, secret keys, Kubernetes DNS for `minio-service.default`, and Longhorn backup target configuration using the `longhorn-system` secret. The server pod reads credentials from the `default` secret.

Risks: empty secret data prevents container startup or TLS setup. The old MinIO image may have compatibility or security issues. Ephemeral storage makes this useful for tests only. TLS symlink setup assumes the secret keys exist and match MinIO cert naming requirements.

Test signals: populate both namespace secrets with access key, secret key, cert, and cert key; apply the base; verify MinIO health and bucket creation; configure Longhorn S3 backup target; run backup/restore; recreate the pod to confirm ephemeral data behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/minio/minio-backupstore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/nfs/kustomization.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/nfs/kustomization.yaml

Purpose: Kustomize entry point for the NFS backupstore base.

Important APIs/types/functions: `kustomize.config.k8s.io/v1beta1` `Kustomization` referencing `nfs-backupstore.yaml`.

Control flow: Kustomize builds or applies the adjacent NFS manifest as the base's resource set.

State and persistence: no runtime state is stored directly. It only controls inclusion of NFS test backupstore resources.

Dependencies/integration: depends on the adjacent NFS manifest and optional overlays for persistence, namespaces, or image pinning.

Risks: hard-coded namespaces and ephemeral storage from the resource file remain unless patched by overlays. Moving the manifest path breaks the base.

Test signals: run `kustomize build sources/control-plane/longhorn/deploy/backupstores/base/nfs` and verify the output includes the NFS deployment and service.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/nfs/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/nfs/nfs-backupstore.yaml -->
# sources/control-plane/longhorn/deploy/backupstores/base/nfs/nfs-backupstore.yaml

Purpose: provides a Kustomize base for a test NFS backupstore using the Longhorn NFS backupstore image.

Important APIs/types/functions: `Deployment` `longhorn-test-nfs` in `default`, image `longhornio/nfs-backupstore:latest`, env vars `EXPORT_ID`, `EXPORT_PATH`, `PSEUDO_PATH`, `NFS_DISK_IMAGE_SIZE_MB`, command that chmods `/opt/backupstore` and starts NFS while teeing `/var/log/ganesha.log`, privileged security context with `SYS_ADMIN` and `DAC_READ_SEARCH`, `emptyDir` volumes for backup data and ganesha data, liveness probe checking the log, and headless `Service` `longhorn-test-nfs-svc`.

Control flow: applying the manifest starts one privileged NFS/Ganesha pod, initializes the export path, runs `/opt/start_nfs.sh`, and exposes a headless service. The liveness probe fails if the log reports no export entries.

State and persistence: backup data lives on an `emptyDir` and is lost when the pod is deleted or rescheduled. Ganesha runtime data is also ephemeral. No credential secret is created for NFS.

Dependencies/integration: depends on the `longhornio/nfs-backupstore:latest` image and its startup script. Longhorn must be configured with an NFS backup target pointing to the headless service/export path.

Risks: `latest` with `Always` image pulls is non-reproducible. Privileged NFS server pods may be blocked by cluster policy. The service exposes only a placeholder port 1234, while NFS may rely on pod networking and image-specific behavior, so consumers need the documented endpoint pattern. Ephemeral storage makes it unsuitable for durable backups.

Test signals: apply the base, inspect pod logs for exported path, verify liveness remains healthy, configure Longhorn NFS backup target, run backup/restore, and confirm backup loss after pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/backupstores/base/nfs/nfs-backupstore.yaml -->
