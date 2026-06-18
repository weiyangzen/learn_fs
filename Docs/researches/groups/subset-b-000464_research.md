# Research: subset-b-000464

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/labels.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/labels.go

## Purpose
`labels.go` centralizes small label helpers used by Rook operator resources. It parses user label strings, applies Kubernetes recommended application labels, and determines which node label should be treated as the node hostname.

## Important APIs, Types, and Functions
`ParseStringToLabels()` converts comma-separated `key=value` input into a `map[string]string`, accepting key-only and empty-value forms. `AddRecommendedLabels()` mutates an existing label map with `app.kubernetes.io/*` keys and `rook.io/operator-namespace`. `LabelHostname()` returns `ROOK_CUSTOM_HOSTNAME_LABEL` when set, otherwise `corev1.LabelHostname`.

## Control Flow, State, and Persistence
The file has no persistence. State is read from environment variables: `PodNamespaceEnvVar` for operator namespace labels and `ROOK_CUSTOM_HOSTNAME_LABEL` for hostname matching. `ParseStringToLabels()` uses simple split logic and logs when a label contains more than one `=`.

## Dependencies and Integration Points
Node selection in `node.go` depends on `LabelHostname()`. Resource builders throughout the operator can call `AddRecommendedLabels()` before creating Kubernetes objects. The label parser is a utility for CLI/config strings.

## Risks
`ParseStringToLabels()` does not trim whitespace and only keeps text before the second `=`, so values containing `=` are truncated. `AddRecommendedLabels()` assumes the input map is non-nil and will panic for nil maps. Operator namespace labeling depends on the environment being populated by the downward API.

## Test Signals
`labels_test.go` covers key/value, key-only, empty value, multi-label, and empty input parsing. It does not cover whitespace, duplicate keys, multiple `=`, custom hostname labels, or nil label maps.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/labels_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/labels_test.go

## Purpose
This test file validates the string-to-label parser in `labels.go`.

## Important APIs, Types, and Functions
`TestParseStringToLabels()` defines a map of raw selector strings to expected maps and asserts `ParseStringToLabels()` output with testify.

## Control Flow, State, and Persistence
The test is table-like but iterates over a Go map, so execution order is intentionally unspecified. It has no external state and no fake Kubernetes dependencies.

## Dependencies and Integration Points
It imports only `testing` and `github.com/stretchr/testify/assert`. The tested behavior feeds any operator path that accepts label selectors from string configuration.

## Risks
Coverage is narrow. It does not assert warning behavior for too many `=` characters, whitespace handling, duplicate keys, or invalid Kubernetes label syntax. Because the cases are map entries, subtest names are not used and a failure is less localized than a named table.

## Test Signals
Signals are positive parsing for `key=value`, `key=`, `key`, comma-separated pairs, and empty input. A useful additional signal would be explicit cases for `key=a=b`, ` key = value `, and repeated keys.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/labels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/name.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/name.go

## Purpose
`name.go` converts numeric daemon indexes to compact alphabetic names and back. Rook uses this for Ceph daemon IDs such as monitor names.

## Important APIs, Types, and Functions
`IndexToName(index int)` maps zero-based indexes to base-26 lowercase sequences: `0 -> a`, `25 -> z`, `26 -> aa`. `NameToIndex(name string)` is the inverse and rejects non-lowercase alphabetic characters. `maxPerChar` is the fixed alphabet size.

## Control Flow, State, and Persistence
There is no persistent state. `IndexToName()` repeatedly prepends calculated runes and subtracts one after division to model spreadsheet-style base-26 names. `NameToIndex()` computes a positional factor and validates each rune.

## Dependencies and Integration Points
The only dependency is `fmt` for formatting and errors. Higher-level operator code can rely on stable daemon IDs that remain compact while scaling past 26 entries.

## Risks
Negative indexes are not rejected by `IndexToName()` and can produce unexpected rune output. `NameToIndex("")` returns zero because no characters are processed. Only lowercase ASCII letters are valid, which is intentional but should be documented for callers.

## Test Signals
`name_test.go` verifies round-trip conversion across one-, two-, and three-letter boundaries. Missing signals include invalid names, empty names, and negative indexes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/name_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/name_test.go

## Purpose
This file confirms that daemon name/index conversion remains stable.

## Important APIs, Types, and Functions
`TestConvertDaemonID()` enumerates expected names from `a` through representative multi-character values. `testConvertDaemonName()` asserts both `IndexToName(index)` and `NameToIndex(name)`.

## Control Flow, State, and Persistence
The tests are deterministic and have no environment or filesystem state. Each case checks a bidirectional invariant for a known point in the sequence.

## Dependencies and Integration Points
It uses testify assertions. The signal protects monitor and daemon naming behavior used by Rook orchestration code.

## Risks
The test file only covers valid lowercase names and non-negative indexes. It does not lock down behavior for invalid characters, uppercase names, empty strings, or negative indexes.

## Test Signals
Strong signals are boundary values `z -> 25`, `aa -> 26`, `az -> 51`, `ba -> 52`, `za -> 676`, and `aaa -> 702`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/name_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/network.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/network.go

## Purpose
`network.go` provides Multus and IP-address helpers for Rook-managed Kubernetes resources. It applies network attachment annotations, parses Multus network status annotations, parses `ip --json address show`, and classifies endpoint address families.

## Important APIs, Types, and Functions
`ApplyMultus()` computes public and, for `rook-ceph-osd`, cluster network selections from `cephv1.NetworkSpec` and writes `k8s.v1.cni.cncf.io/networks`. `ParseNetworkStatusAnnotation()` unmarshals Multus status JSON. `FindNetworkStatusByInterface()` selects a status by interface name. `LinuxIpAddrResult` and `LinuxIpAddrInfo` model the limited JSON fields Rook consumes. `ParseLinuxIpAddrOutput()` validates non-empty JSON. `GetIpAddressType()` returns Kubernetes discovery IPv4 or IPv6 address type and rejects mixed families.

## Control Flow, State, and Persistence
The functions are stateless and mutate only the provided `ObjectMeta`. `ApplyMultus()` always appends public network first, then cluster network for OSDs, preserving a stable annotation order independent of selector map order.

## Dependencies and Integration Points
It depends on Rook Ceph API network helpers, the network-attachment-definition client API, Kubernetes EndpointSlice address types, and `net/netip`. It integrates with pod/service metadata creation and endpoint generation for Multus environments.

## Risks
Only app label `rook-ceph-osd` receives the cluster network, so new cluster-network consumers require code changes. An absent `app` label is treated as unknown and public-only. `GetIpAddressType()` infers family from the first address and validates the rest; invalid or scoped addresses produce errors.

## Test Signals
`network_test.go` covers short and JSON Multus selector syntax, public/cluster ordering, empty and malformed `ip` JSON, IPv4, IPv6, mixed-family, and empty address lists. It does not cover `ParseNetworkStatusAnnotation()` or `FindNetworkStatusByInterface()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/network_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/network_test.go

## Purpose
This test file validates Multus annotation generation and IP parsing/classification behavior.

## Important APIs, Types, and Functions
`TestApplyMultus()` drives `ApplyMultus()` with unknown selectors, public/cluster selectors, JSON selectors, mixed selector formats, OSD labels, and non-OSD metadata. `TestParseLinuxIpAddrOutput()` uses a realistic mixed IPv4/IPv6 JSON fixture. `TestGetIpAddressType()` checks endpoint address type classification.

## Control Flow, State, and Persistence
All tests are local and deterministic. Multus tests create `cephv1.NetworkSpec` values and inspect metadata annotations. IP parser tests unmarshal a static fixture and a truncated variant.

## Dependencies and Integration Points
The tests depend on Rook Ceph network selector parsing, network-attachment-definition types, Kubernetes discovery address constants, and testify.

## Risks
The test intentionally expects unknown network selectors to result in an empty annotation instead of an error, which may hide misconfiguration depending on caller expectations. No test verifies Multus status annotation parsing or interface lookup.

## Test Signals
Strong signals include stable public-before-cluster ordering, JSON and short selector compatibility, empty raw IP output errors, syntax errors, IPv4-only and IPv6-only address typing, and mixed-family rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/node.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/node.go

## Purpose
`node.go` contains Rook's Kubernetes node eligibility, hostname, taint/toleration, affinity, and node-list matching helpers. It is central to deciding where Ceph storage daemons can run.

## Important APIs, Types, and Functions
`ValidNode()` and `GetValidNodes()` combine schedulability, placement, and readiness checks. Hostname helpers include `NodeWithHostnameExists()`, `GetNodeNameFromHostname()`, `GetNodeHostName()`, `GetNodeHostNameLabel()`, and `GetNodeHostNames()`. Placement helpers include `NodeMeetsPlacementTerms()`, `NodeMeetsAffinityTerms()`, `NodeIsTolerable()`, and `NodeIsReady()`. Matching helpers include `GetKubernetesNodesMatchingRookNodes()`, `GetNotReadyKubernetesNodes()`, and `RookNodesMatchingKubernetesNodes()`. `GenerateNodeAffinity()` accepts JSON, YAML, or legacy semicolon/comma label syntax.

## Control Flow, State, and Persistence
The file performs read-only Kubernetes API calls via `clientset.CoreV1().Nodes()`. It logs skipped nodes grouped by reason. `scheduleAlways` can override unschedulable and not-ready states. Hostname matching uses `LabelHostname()`, falling back to node names if hostname labels are missing.

## Dependencies and Integration Points
It depends on Rook Ceph CRD placement and storage specs, Kubernetes node/label/selection APIs, fake or real Kubernetes clients, `sigs.k8s.io/yaml`, and `logr` toleration matching. It feeds OSD scheduling, node validation, and CRD-driven affinity generation.

## Risks
`GetNodeHostNames()` reads the hostname label without checking presence, yielding empty values. `GenerateNodeAffinity()` accepts multiple input grammars, which increases ambiguity. Preferred affinity terms are ignored for eligibility, as intended. `scheduleAlways` can allow not-ready nodes, so callers must use it deliberately.

## Test Signals
`node_test.go` covers valid-node filtering, `scheduleAlways`, required affinity, well-known taint ignoring, readiness states, rook/kubernetes node matching, custom hostname labels, JSON/YAML affinity parsing, and not-ready listing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/node_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/node_test.go

## Purpose
This file exercises node eligibility and conversion helpers against fake Kubernetes clients and synthetic nodes.

## Important APIs, Types, and Functions
`createNode()` seeds fake nodes. `TestValidNode()` covers ready, not-ready, `scheduleAlways`, and node affinity. `TestNodeIsTolerable()` covers explicit and well-known taints. `TestNodeIsReady()` checks condition semantics. Matching tests cover Rook node specs against Kubernetes nodes. `TestGenerateNodeAffinity()` covers legacy, JSON, and YAML input. `TestGetNotReadyKubernetesNodes()` checks ready-state filtering.

## Control Flow, State, and Persistence
Tests create in-memory fake clientsets. One test uses `t.Setenv("ROOK_CUSTOM_HOSTNAME_LABEL", ...)` to validate custom hostname resolution. There is no persistent cluster state.

## Dependencies and Integration Points
The tests use Rook Ceph API types, `operator/test` fake-client helpers, Kubernetes fake clientsets, and testify. They protect storage scheduling decisions used by CephCluster reconciliation.

## Risks
There is a small helper bug in `taints()` that appends to the parameter slice while iterating; current call patterns still work but the helper is confusing. Tests do not directly cover API list failures, hostname lookup helpers, or all node selector operators.

## Test Signals
High-value signals are `scheduleAlways` behavior, known-taint bypass, missing hostname fallback, custom hostname label override, and YAML/JSON affinity compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/options.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/options.go

## Purpose
`options.go` defines reusable wait/retry options for Kubernetes utility operations.

## Important APIs, Types, and Functions
`WaitOptions` carries `Wait`, `RetryCount`, `RetryInterval`, and `ErrorOnTimeout`. The unexported methods `retryCountOrDefault()` and `retryIntervalOrDefault()` select explicit values or caller-provided defaults.

## Control Flow, State, and Persistence
The struct is pure in-memory configuration. No function performs waiting itself; consumers decide how to apply these values.

## Dependencies and Integration Points
The only dependency is `time.Duration`. Delete/update helpers elsewhere in `k8sutil` can accept or compose these options to control polling behavior.

## Risks
The defaulting methods have pointer receivers and will panic if called on a nil `*WaitOptions`. Callers must guard nil options before defaulting. Because the type does not enforce valid combinations, `Wait=false` with retry fields set is possible.

## Test Signals
No direct test file is mapped for this source. Useful tests would cover defaulting, zero values, nil-option handling by callers, and timeout behavior in consumers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pod.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/pod.go

## Purpose
`pod.go` provides common pod-spec, environment, lookup, toleration, anti-affinity, deletion, and scheduling helpers for Rook operator code.

## Important APIs, Types, and Functions
Environment helpers create downward-API env vars: `ConfigOverrideEnvVar()`, `PodIPEnvVar()`, `NamespaceEnvVar()`, `NameEnvVar()`, `NodeEnvVar()`, and `ConfigDirEnvVar()`. Container helpers include `GetContainerImage()`, `GetSpecContainerImage()`, and `GetContainerByName()`. Pod status helpers include `GetRunningPod()`, `PodsRunningWithLabel()`, `PodsWithLabelAreAllRunning()`, `GetPodPhaseMap()`, and `IsPodScheduled()`. Spec mutators include `AddUnreachableNodeToleration()`, `ClusterDaemonEnvVars()`, `SetNodeAntiAffinityForPod()`, `ForceDeletePodIfStuck()`, and `RemoveDuplicateEnvVars()`.

## Control Flow, State, and Persistence
Some functions are pure spec builders; others read environment variables or Kubernetes pods/nodes. `ForceDeletePodIfStuck()` only force-deletes terminating pods on not-ready nodes and suppresses delete errors after logging. `RemoveDuplicateEnvVars()` keeps the first occurrence by name.

## Dependencies and Integration Points
It integrates with Kubernetes `PodSpec`, Rook `clusterd.Context`, Ceph placement application, and node readiness helpers. Downward-API env names are shared with operator manifests.

## Risks
`SetNodeAntiAffinityForPod()` assumes `pod.Affinity` is non-nil; callers must initialize it or use placement helpers first. `IsPodScheduled()` inspects only the first matching pod. `ForceDeletePodIfStuck()` treats delete failures as non-fatal, which preserves reconciliation but can hide stuck pods.

## Test Signals
`pod_test.go` covers container lookup mutation, phase maps, unreachable toleration replacement/defaulting, anti-affinity counts after placement, and pod scheduling detection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pod_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/pod_test.go

## Purpose
This file validates selected pod utilities in `pod.go`.

## Important APIs, Types, and Functions
`TestGetContainerByName()` covers missing and found containers and verifies the returned pointer mutates the source slice element. `TestGetPodPhaseMap()` groups pod names by phase. `TestAddUnreachableNodeToleration()` checks default, env override, replacement positions, and invalid env fallback. `TestPodSpecPlacement()` checks anti-affinity counts after applying placement. `TestIsMonScheduled()` checks pod scheduling via label selectors.

## Control Flow, State, and Persistence
Tests use fake clientsets from `operator/test`, local pod specs, and `t.Setenv()` for toleration seconds. Kubernetes state is in-memory only.

## Dependencies and Integration Points
The tests use Rook Ceph placement, pod anti-affinity APIs, Kubernetes fake clients, and testify. They protect operator scheduling behavior for mons and other pods.

## Risks
The anti-affinity helper assumes initialized affinity state, but the tests rely on `Placement.ApplyToPodSpec()` to set that up. `ForceDeletePodIfStuck()`, duplicate env removal, running-pod environment lookup, and pod label counting are not covered here.

## Test Signals
Useful signals include idempotent unreachable toleration replacement, invalid env fallback to five seconds, pointer semantics for container lookup, and first-pod scheduling behavior in `IsPodScheduled()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pod_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/prometheus.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/prometheus.go

## Purpose
`prometheus.go` builds and reconciles Prometheus Operator `ServiceMonitor` resources for Rook metrics endpoints.

## Important APIs, Types, and Functions
`getMonitoringClient()` creates a Prometheus monitoring clientset from `clusterd.Context.KubeConfig`. `GetServiceMonitor()` returns a ServiceMonitor template with `team=rook`, namespace selector, `app` and `rook_cluster` match labels, one `/metrics` endpoint, `10s` interval, `HonorLabels`, and a relabel rule setting `cluster` to the namespace. `CreateOrUpdateServiceMonitor()` creates on not found or updates the existing spec and labels.

## Control Flow, State, and Persistence
The file persists state by creating or updating Kubernetes custom resources. On update, it retains the existing object metadata except labels and spec. It returns errors for client creation, get, create, and update failures.

## Dependencies and Integration Points
It depends on Prometheus Operator API/client packages, Rook `clusterd.Context`, Kubernetes API errors, and pointer helpers. It integrates Rook services with Prometheus scraping when the CRD/client is available.

## Risks
The client is constructed internally, making unit testing update paths harder. If the Prometheus CRD is absent or RBAC is missing, create/update fails. Only labels and spec are updated, so annotations or owner references from the desired definition are not reconciled.

## Test Signals
`prometheus_test.go` covers the static ServiceMonitor template. It does not cover client creation, create-or-update behavior, not-found branching, or error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/prometheus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/prometheus_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/prometheus_test.go

## Purpose
This test validates the ServiceMonitor object template generated by `GetServiceMonitor()`.

## Important APIs, Types, and Functions
`TestGetServiceMonitor()` asserts name, namespace, endpoint port, interval, labels, namespace selector, service selector, endpoints, and relabel replacement.

## Control Flow, State, and Persistence
The test is pure object construction with no Kubernetes client or CRD persistence.

## Dependencies and Integration Points
It depends on Prometheus Operator monitoring API types and testify. The signal protects service monitor shape used by Rook metrics integration.

## Risks
The create/update reconciliation path is untested. The test checks presence but not the full selector contents beyond a few fields, and it does not cover owner references or annotations.

## Test Signals
Key signals are `10s` scrape interval, `/metrics` endpoint indirectly through endpoint presence, namespace relabeling to `cluster`, and expected port propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/prometheus_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pvc.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/pvc.go

## Purpose
`pvc.go` conditionally expands persistent volume claims when the desired storage request is larger than the current request and the storage class permits expansion.

## Important APIs, Types, and Functions
`ExpandPVCIfRequired(ctx, client, desiredPVC, currentPVC) bool` compares `ResourceStorage` requests, validates `StorageClassName`, fetches the `StorageClass`, checks `AllowVolumeExpansion`, updates `currentPVC.Spec.Resources.Requests`, and calls `client.Update()`.

## Control Flow, State, and Persistence
The function mutates the in-memory `currentPVC` and persists it through the controller-runtime client only for expansions. Missing requests, missing storage class, storage class lookup failures, disabled expansion, update failures, equal sizes, and shrink attempts all return false after logging.

## Dependencies and Integration Points
It uses Kubernetes core PVC types, storage class types, controller-runtime client, and namespaced object keys. It is intended for reconcile loops where PVC expansion should not fail the whole reconcile on update errors.

## Risks
Errors are logged but not returned, so callers only get a boolean. Shrink requests are ignored. The `pvcBacked` style of device logic is not relevant here; expansion depends entirely on storage class policy and API update success.

## Test Signals
`pvc_test.go` covers equal, larger, smaller, allowed, and disallowed expansion cases using a fake controller-runtime client. Missing storage class name, storage class get failures, and update failures are not directly covered.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pvc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pvc_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/pvc_test.go

## Purpose
This test verifies conditional PVC expansion behavior.

## Important APIs, Types, and Functions
`TestExpandPVCIfRequired()` creates a desired/current PVC and storage class in a fake controller-runtime client, varies current and desired sizes, toggles `AllowVolumeExpansion`, calls `ExpandPVCIfRequired()`, then re-reads the PVC.

## Control Flow, State, and Persistence
All persistence is in the fake client object store. The same PVC object is reused across table cases with request size and storage-class expansion flags updated before each run.

## Dependencies and Integration Points
It uses Kubernetes PVC/storage-class APIs, resource quantity parsing, controller-runtime fake client, and testify.

## Risks
The assertion uses string comparison (`tc.currentPVCSize <= tc.desiredPVCSize`) to decide expected behavior, which happens to work for these values but is not a general quantity comparison. The test ignores the boolean return from `ExpandPVCIfRequired()`.

## Test Signals
Signals cover no-op equal size, successful growth when allowed, shrink ignored, and growth blocked when storage class expansion is false.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/pvc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/resources.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/resources.go

## Purpose
`resources.go` groups owner-reference helpers, resource requirement merge logic, and YAML parsers for container resource settings.

## Important APIs, Types, and Functions
`OwnerInfo` abstracts owner reference setting from either a live owner object/scheme or a raw `OwnerReference`. `SetOwnerReference()` appends non-duplicate owner refs. `SetControllerReference()` validates namespace/controller ownership and sets controller plus default `BlockOwnerDeletion`. `GetUID()` exposes owner UID. `MergeResourceRequirements()` lets the first requirements override the second when present. `SetOwnerRefsWithoutBlockOwner()` copies owner refs without controller/block flags. `ContainerResource`, `YamlToContainerResourceArray()`, and `YamlToContainerResource()` parse YAML into Kubernetes resource requirements.

## Control Flow, State, and Persistence
Functions mutate Kubernetes object metadata or return parsed objects in memory. Namespace validation prevents namespaced owners from owning cluster-scoped or cross-namespace resources. Duplicate detection compares group, kind, and name rather than UID.

## Dependencies and Integration Points
It depends on controller-runtime `controllerutil`, Kubernetes metadata/runtime/schema/resource APIs, and YAML-to-JSON conversion. It integrates with most resource builders that need garbage collection ownership and configurable requests/limits.

## Risks
`SetControllerReference()` can append the same controller ref more than once after validation if called repeatedly with the same raw owner reference. Duplicate owner comparison ignores UID. YAML parsing relies on Kubernetes resource quantity unmarshal errors for validation.

## Test Signals
`resources_test.go` covers merge behavior, YAML parsing success/failure, namespaced owner validation, controller conflict validation, and owner-reference duplicate handling for non-controller refs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/resources_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/resources_test.go

## Purpose
This file tests owner-reference and resource parsing utilities.

## Important APIs, Types, and Functions
`TestMergeResourceRequirements()` validates first-over-second semantics. `TestYamlToContainerResourceArray()` and `TestYamlToContainerResource()` validate YAML conversion. `TestValidateOwner()` checks namespace constraints. `TestValidateController()` checks same and conflicting controllers. `TestSetOwnerReference()` checks append and non-duplication behavior.

## Control Flow, State, and Persistence
Tests operate on in-memory Kubernetes objects and resource quantities. No fake client is required.

## Dependencies and Integration Points
The tests use Kubernetes core metadata/resource APIs and testify. They protect owner-reference invariants used for Kubernetes garbage collection.

## Risks
The YAML invalid data cases rely on duplicate malformed keys producing errors; more semantic invalid cases are not covered. Controller reference append duplication is not explicitly asserted. Owner comparison by group/kind/name rather than UID is indirectly accepted.

## Test Signals
High-value signals include cross-namespace owner rejection, cluster-scoped object rejection for namespaced owners, default controller validation, and resource request/limit fallback behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/secret.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/secret.go

## Purpose
`secret.go` contains create/update and ownership-gated delete/update helpers for Kubernetes Secrets.

## Important APIs, Types, and Functions
`CreateOrUpdateSecret()` creates a secret and updates it on `AlreadyExists`. `DeleteSecretIfOwnedBy()` deletes only when the existing secret's controller owner matches the provided owner. `UpdateSecretIfOwnedBy()` fetches the latest secret, verifies both existing and desired controller ownership, copies data/stringData/labels/annotations, and updates. `IsSameOwnerReference()` compares owner references by API group, kind, and name.

## Control Flow, State, and Persistence
The functions persist Kubernetes Secret changes through `clientset.CoreV1().Secrets(namespace)`. Delete ignores not-found and skips unowned or differently owned secrets. Update returns errors for missing existing secret, missing owner references, conflicting owners, and update failures.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 secrets, API error helpers, schema parsing, and client-go. It protects user-created secrets from accidental operator deletion or mutation.

## Risks
Owner matching ignores UID, so a recreated owner with the same group/kind/name is treated as the same. `UpdateSecretIfOwnedBy()` has a typo in one error message ("founf"). `CreateOrUpdateSecret()` updates the whole provided secret, so callers must preserve fields they intend to keep.

## Test Signals
`secret_test.go` covers owner comparison, deletion for not found/get error/unowned/different owner/matching owner/delete error, and update success/no owner/different owner/not found.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/secret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/secret_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/secret_test.go

## Purpose
This file validates owner-reference comparison and ownership-safe secret delete/update behavior.

## Important APIs, Types, and Functions
`TestIsSameOwnerReference()` checks matching and mismatched refs. `TestDeleteSecretIfOwnedBy()` uses fake-client reactors to simulate get/delete outcomes. `TestUpdateSecretIfOwnedBy()` creates fake secrets and validates update success and rejection cases.

## Control Flow, State, and Persistence
Tests run against `k8s.io/client-go/kubernetes/fake`. Delete tests intercept get and delete actions. Update tests persist fake secrets, mutate local objects, and re-read from the fake store.

## Dependencies and Integration Points
It uses Kubernetes metadata/errors/runtime/schema test APIs, fake clientsets, `ptr.To(true)` for controller refs, and testify.

## Risks
The "owned by caller, deletion succeeds" table entry uses a secret owner name that does not match the `owner` variable, so it may not actually assert a delete unless reactors mask the mismatch. Tests do not inspect fake actions to prove delete was called in all expected cases.

## Test Signals
Important signals are not-found delete idempotence, unowned secret preservation, different-owner preservation, delete error propagation, and update rejection for unowned or differently owned secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/secret_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/service.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/service.go

## Purpose
`service.go` manages Kubernetes Service create/update operations and multi-cluster ServiceExport lookup/export utilities.

## Important APIs, Types, and Functions
`CreateOrUpdateService()` creates a service or delegates to `UpdateService()` on already-exists. `UpdateService()` preserves immutable `ClusterIP` and uses the existing `ResourceVersion` before update. `ParseServiceType()` maps strings to Kubernetes service types. `IsServiceExported()` checks MCS `ServiceExport` existence. `ExportService()` creates a ServiceExport and resolves its clusterset DNS name. `verifyExportedService()` reports invalid status conditions. `GetExportedServiceIP()` retries DNS lookup.

## Control Flow, State, and Persistence
Service functions persist through client-go core services. MCS functions construct a versioned client from `clusterd.Context.KubeConfig`, create ServiceExports, and perform DNS resolution with 20 retries at five-second intervals.

## Dependencies and Integration Points
It depends on Kubernetes core services, API errors, Rook cluster context, MCS API clients, and `net.LookupIP`. It integrates Rook services with Kubernetes multi-cluster service discovery.

## Risks
`GetExportedServiceIP()` can block for roughly 100 seconds on DNS failure. `ExportService()` relies on DNS name format and only verifies ServiceExport status after DNS resolution fails. Tests cover only `ParseServiceType`; create/update and MCS paths need integration coverage.

## Test Signals
`service_test.go` checks valid and invalid service type strings. Additional signals should cover ClusterIP preservation, resource version propagation, ServiceExport already-exists behavior, invalid status conditions, and DNS retry behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/service_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/service_test.go

## Purpose
This test validates service type string parsing.

## Important APIs, Types, and Functions
`TestParseServiceType()` checks `ClusterIP`, `NodePort`, `LoadBalancer`, and `ExternalName`, plus invalid strings such as empty input, lowercase `nodeport`, and arbitrary values.

## Control Flow, State, and Persistence
The test is pure and has no Kubernetes client state.

## Dependencies and Integration Points
It uses Kubernetes core/v1 service type constants and testify. This protects config/CRD parsing paths that convert strings to `ServiceType`.

## Risks
The rest of `service.go` has no mapped unit coverage here. Update semantics around immutable `ClusterIP`, MCS client creation, ServiceExport status, and DNS lookup are untested.

## Test Signals
Signal is a strict, case-sensitive parser that returns the empty service type for invalid input.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/status.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/status.go

## Purpose
`status.go` defines shared string constants for Ceph-related custom resource status values.

## Important APIs, Types, and Functions
Constants are `ReadyStatus`, `FailedStatus`, `ReconcilingStatus`, `ReconcileFailedStatus`, and `EmptyStatus`.

## Control Flow, State, and Persistence
There is no control flow. These constants are persisted indirectly when reconciler code writes CR status fields.

## Dependencies and Integration Points
The file has no imports. It integrates with Rook status reconciliation and any tests or UIs that compare status strings.

## Risks
String constants must remain stable for external consumers. There are no typed enums, so callers can still write arbitrary statuses.

## Test Signals
No direct tests are mapped. Signals are primarily downstream controller tests that assert status transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/taints.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/taints.go

## Purpose
`taints.go` identifies Kubernetes-managed taints that Rook may choose to ignore when evaluating node placement.

## Important APIs, Types, and Functions
`WellKnownTaints` lists node not-ready, unreachable, unschedulable, pressure, network unavailable, external cloud provider, and shutdown taints. `TaintIsWellKnown()` checks whether a `v1.Taint` key is in that list.

## Control Flow, State, and Persistence
The logic is a simple in-memory linear scan over a package-level slice. There is no external state.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 taint constants and cloud-provider taint constants. `NodeIsTolerable()` in `node.go` uses it when `ignoreWellKnownTaints` is true.

## Risks
The well-known list can drift as Kubernetes adds taints. Effects and values are ignored; only the key matters. Linear scan is fine for the small list.

## Test Signals
Coverage is indirect through `node_test.go`, which creates all `WellKnownTaints` and checks toleration behavior with and without ignore mode. There is no standalone test for `TaintIsWellKnown()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/taints.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/test/deployment.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/test/deployment.go

## Purpose
This test helper provides a stub for deployment update-and-wait behavior used by Rook unit tests.

## Important APIs, Types, and Functions
`UpdateDeploymentAndWaitStub()` returns a function matching the production update signature plus a pointer to a slice of deployments passed to it. `DeploymentNamesUpdated()` maps that slice to deployment names. `ClearDeploymentsUpdated()` resets it.

## Control Flow, State, and Persistence
The stub appends received deployment pointers to a captured slice and always returns nil. State is held in the returned slice pointer and is controlled by the test.

## Dependencies and Integration Points
It depends on Rook `clusterd.Context`, Ceph `client.ClusterInfo`, and Kubernetes apps/v1 deployments so it can be assigned where production `UpdateDeploymentAndWait` is expected.

## Risks
The stub stores pointers without deep-copying, despite the comment describing a copy. Later mutations to deployment objects can affect recorded values. It does not simulate errors, resource versions, rollout waits, or upgrade checks.

## Test Signals
No direct tests are mapped. Downstream unit tests can assert which deployments were requested for update and clear the recorder between phases.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/test/deployment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/tolerations.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/tolerations.go

## Purpose
`tolerations.go` parses raw YAML configuration into Kubernetes toleration arrays.

## Important APIs, Types, and Functions
`YamlToTolerations(raw string) ([]v1.Toleration, error)` returns an empty slice for empty input, converts YAML to JSON, and unmarshals into `[]v1.Toleration`.

## Control Flow, State, and Persistence
The function is pure and has no persistence. Errors from YAML conversion or JSON unmarshal are returned directly.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 toleration types and `k8s.io/apimachinery/pkg/util/yaml`. It integrates with CRD/operator configuration paths that accept tolerations as YAML text.

## Risks
No semantic validation beyond Kubernetes JSON unmarshal occurs. Unknown YAML fields may be ignored depending on Kubernetes type behavior, so malformed but structurally valid input can pass.

## Test Signals
No direct mapped test file covers this helper. Useful signals would include empty input, valid key/effect/operator/tolerationSeconds YAML, invalid YAML, and unexpected field behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/tolerations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/volume.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/volume.go

## Purpose
`volume.go` converts arbitrary filesystem paths into Kubernetes DNS-1123-compatible volume names.

## Important APIs, Types, and Functions
`PathToVolumeName(path string) string` lowercases ASCII letters, preserves digits and lowercase letters, replaces all other runes with hyphens, trims leading/trailing hyphens, and truncates names longer than 63 characters with beginning/end samples plus an eight-character hash from `Hash()`.

## Control Flow, State, and Persistence
The function is pure. Long-name handling uses `validation.DNS1123LabelMaxLength` and a stable hash to reduce collisions.

## Dependencies and Integration Points
It depends on Kubernetes validation constants and package-level `Hash()` from `k8sutil.go`. It integrates with pod volume construction where host paths or arbitrary names must become legal Kubernetes volume names.

## Risks
Consecutive invalid characters become consecutive hyphens and are not collapsed. Inputs containing only invalid/trimmed characters can produce an empty string. Non-ASCII letters are converted to hyphens rather than transliterated.

## Test Signals
`volume_test.go` covers slashes, casing, digits, punctuation, currency/full-width symbols, and long-name hashing. Empty and all-invalid inputs are not covered.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/volume_test.go -->
# sources/control-plane/rook/pkg/operator/k8sutil/volume_test.go

## Purpose
This file validates path-to-volume-name sanitization and truncation.

## Important APIs, Types, and Functions
`TestPathToVolumeName()` enumerates path inputs and expected Kubernetes volume names.

## Control Flow, State, and Persistence
The test is pure and deterministic. The long-name case locks down the current hash suffix for a fixed input.

## Dependencies and Integration Points
It uses Go testing only. It protects volume naming for pod specs derived from paths.

## Risks
The test does not cover empty strings, paths made entirely of separators, names exactly at 63 characters, or possible collision behavior. Long-name expectation will change if `Hash()` changes.

## Test Signals
Signals include trimming leading/trailing hyphens, lowercase conversion, numeric preservation, broad symbol replacement, Unicode-to-hyphen handling, and long-name sample/hash formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/k8sutil/volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/client.go -->
# sources/control-plane/rook/pkg/operator/test/client.go

## Purpose
`client.go` provides reusable fake Kubernetes client helpers for Rook operator unit tests.

## Important APIs, Types, and Functions
`New()` creates a fake clientset with ready nodes. `AddReadyNode()` and `AddSomeReadyNodes()` seed nodes with hostname labels, ready conditions, and internal IPs. `SetFakeKubernetesVersion()` configures fake discovery version info. `NewComplexClientset()` adds a generateName reactor. `PrependComplexJobReactor()` mirrors job-to-pod creation/deletion and optional node assignment. `PrependFailReactor()` injects failures. `FakeOperatorPod()`, `FakeReplicaSet()`, and `FakeCustomisePodCreate()` build common test objects.

## Control Flow, State, and Persistence
All state is in client-go fake object trackers and reactors. `pickNodeIdx` is package-global and advances round-robin across calls. Reactors mutate objects before default handling or manipulate the tracker directly to avoid fake-client locks.

## Dependencies and Integration Points
It depends on Kubernetes fake clientsets, testing reactors, metadata accessors, UUID/base32 generation, and core/apps/batch APIs. It is used broadly by operator unit tests that need more realistic fake cluster behavior.

## Risks
`AddReadyNode()` logs already-exists but still panics because the panic is unconditional after the log. Global `pickNodeIdx` can leak ordering between tests. Generated names are random, so tests should not assert exact suffixes. Reactor logic only approximates Kubernetes behavior.

## Test Signals
No direct tests are mapped for this helper. Downstream tests exercise ready-node creation, job pod creation/deletion, version discovery, and failure reactors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/containers.go -->
# sources/control-plane/rook/pkg/operator/test/containers.go

## Purpose
`containers.go` implements assertion helpers for container specs used by Rook unit tests.

## Important APIs, Types, and Functions
`ContainersTester` wraps a container list. `ResourceLimitExpectations` defines optional expected CPU/memory limits and requests. `PodSpecTester.Containers()` gathers init and normal containers. `AssertArgReferencesMatchEnvVars()` ensures `$(ENV)` references in args have corresponding env vars. `AssertResourceSpec()` checks resource strings. `RunFullSuite()` runs both checks. `argEnvReferences()` and `varNames()` extract references and env names.

## Control Flow, State, and Persistence
The helpers operate in memory and report through `testing.T` assertions. Arg references are deduplicated via a map and extracted with a regular expression.

## Dependencies and Integration Points
It depends on Kubernetes container types, testify, and regexp. It integrates with `PodSpecTester` and `PodTemplateSpecTester` full-suite checks.

## Risks
The regex recognizes only names starting with ASCII letters and followed by alphanumerics/underscore, which aligns with common env names but excludes some invalid or unusual references. Resource checks apply expectations to every container in the set.

## Test Signals
No direct tests are mapped. Downstream pod-template tests using `RunFullSuite()` validate arg/env consistency and resource settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/env.go -->
# sources/control-plane/rook/pkg/operator/test/env.go

## Purpose
`env.go` provides a small test helper for finding an environment variable in a Kubernetes env var list.

## Important APIs, Types, and Functions
`GetEnv(name string, envs []v1.EnvVar) (*v1.EnvVar, error)` returns the first env var whose `Name` matches or a sentinel env var plus an error.

## Control Flow, State, and Persistence
The helper scans a slice and returns a pointer to the range variable copy, not the original slice element. It has no persistence.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 env vars. Tests for operator-generated pod specs use it to assert downward API or literal env values.

## Risks
Because it returns a pointer to a copy, callers cannot use the result to mutate the original env list. The error message says "volume mount" instead of "env var", which can confuse failures.

## Test Signals
`env_test.go` covers found, missing, empty list, and empty-name env var cases.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/env_test.go -->
# sources/control-plane/rook/pkg/operator/test/env_test.go

## Purpose
This file tests the `GetEnv()` helper.

## Important APIs, Types, and Functions
`TestGetEnv()` uses table cases for one-item lists, empty lists, multi-item lists, empty-name lookup misses, and empty-name lookup hits.

## Control Flow, State, and Persistence
The test is pure and uses reflect deep equality on returned env vars for successful cases.

## Dependencies and Integration Points
It depends on Kubernetes env var types and Go testing/reflect. It protects operator pod-spec assertion helpers.

## Risks
The test deliberately ignores returned values on error, so the sentinel env var is not locked down. It does not expose the pointer-to-copy mutation limitation.

## Test Signals
Signals include first-match lookup and correct error reporting for absent env names.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/env_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/podspec.go -->
# sources/control-plane/rook/pkg/operator/test/podspec.go

## Purpose
`podspec.go` builds a test wrapper around Kubernetes `PodSpec` objects for common Rook pod-spec assertions.

## Important APIs, Types, and Functions
`PodSpecTester` stores `testing.T` and a pod spec pointer. `PodTemplateSpecTester.Spec()` creates a pod-spec tester from a template. `NewPodSpecTester()` constructs one directly. `AssertVolumesAndMountsMatch()` checks that all container mounts have corresponding volumes and all volumes are used. `RunFullSuite()` also delegates to container assertions. `allContainers()` concatenates init and normal containers.

## Control Flow, State, and Persistence
The helpers are in-memory assertion wrappers. `allContainers()` uses `append(p.InitContainers, p.Containers...)`, which can reuse the init-container backing array.

## Dependencies and Integration Points
It depends on Kubernetes pod spec types and the local volume/container test helpers. It is part of the operator test library used by daemon/deployment spec tests.

## Risks
Because full-suite checks require every volume to be mounted somewhere, shared optional volumes must be included carefully. Resource expectations apply to all containers through `ContainersTester`.

## Test Signals
No direct tests are mapped for this file. It is exercised indirectly by downstream operator pod-template spec tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/podspec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/podtemplatespec.go -->
# sources/control-plane/rook/pkg/operator/test/podtemplatespec.go

## Purpose
`podtemplatespec.go` wraps Kubernetes `PodTemplateSpec` objects with reusable Rook test assertions.

## Important APIs, Types, and Functions
`PodTemplateSpecTester` stores `testing.T` and a template pointer. `NewPodTemplateSpecTester()` constructs the wrapper. `AssertLabelsContainRookRequirements()` delegates to the package-level label assertion. `RunFullSuite()` checks labels and then runs pod-spec/container/volume checks.

## Control Flow, State, and Persistence
The file has no persistence. It composes other assertion helpers and reports through `testing.T`.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 pod templates and local test helpers. It is used by operator tests for Deployments, DaemonSets, Jobs, and other template-bearing resources.

## Risks
The label requirements are currently minimal, checking only `app=<appName>`. The full suite can fail on intentionally unused volumes or per-container resource differences unless tests choose expectations carefully.

## Test Signals
No direct tests are mapped. Downstream full-suite tests provide signal that generated pod templates include expected labels, volume mounts, env references, and resources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/podtemplatespec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/spec.go -->
# sources/control-plane/rook/pkg/operator/test/spec.go

## Purpose
`spec.go` provides generic assertion helpers for operator-generated CLI arguments and Kubernetes labels.

## Important APIs, Types, and Functions
`ArgumentsMatchExpected(actualArgs, expectedArgs)` verifies that expected argument groups appear exactly once and that no extra actual arguments remain. `AssertLabelsContainRookRequirements()` asserts an `app=<appName>` label is present. A package logger supports debug output.

## Control Flow, State, and Persistence
`ArgumentsMatchExpected()` joins args into one string, searches for each expected group with `strings.Count`, removes matched text once, and errors on missing, duplicate, empty expected, or leftover actual args. There is no persistence.

## Dependencies and Integration Points
It depends on capnslog, testify, and testing. It is used by operator unit tests that validate generated command args and resource labels.

## Risks
String-search matching can create false positives when one argument group is a substring of another or when argument values contain spaces. It cannot support duplicate identical flag/value groups by design.

## Test Signals
`spec_test.go` covers short flags, long flags with `=`, long flags with values, out-of-order values, missing/extra args, empty expected args, and duplicates.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/spec_test.go -->
# sources/control-plane/rook/pkg/operator/test/spec_test.go

## Purpose
This file tests the generic argument matching helper used by operator tests.

## Important APIs, Types, and Functions
`oneExp()` and `act()` are small test-data builders. `TestArgumentsMatchExpected()` enumerates passing and failing argument-list scenarios for `ArgumentsMatchExpected()`.

## Control Flow, State, and Persistence
The test is table-driven and pure. It checks only whether an error is returned.

## Dependencies and Integration Points
It depends on the local `spec.go` helper and Go testing. Passing tests improve confidence in downstream generated command-line assertions.

## Risks
The test does not include substring collision cases such as `--foo` and `--foobar`, nor arguments containing spaces. It also does not assert detailed error messages.

## Test Signals
Signals include exact order for multi-token flags, detection of missing values, duplicate flag instances, and rejection of extra actual args.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/volumes.go -->
# sources/control-plane/rook/pkg/operator/test/volumes.go

## Purpose
`volumes.go` provides reusable volume and volume-mount assertions for Rook pod spec tests.

## Important APIs, Types, and Functions
Simple helpers include `VolumeExists()`, `VolumeIsEmptyDir()`, `VolumeIsHostPath()`, and `VolumeMountExists()`. Human-readable helpers format volumes/mounts for assertion messages. `VolumesSpec`, `MountsSpec`, and `VolumesAndMountsTestDefinition` model full checks, and `TestMountsMatchVolumes()` verifies every mount has a volume and every volume is used. Internal `getVolume()` and `getMount()` perform lookup.

## Control Flow, State, and Persistence
The helpers scan slices and report errors or `testing.T` assertions. Lookups return pointers to range variable copies, so they are read-only for practical purposes.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 volume types and testify. It integrates with `PodSpecTester.AssertVolumesAndMountsMatch()`.

## Risks
The full match test treats any unused volume as an error, which is good for strict specs but can be too strict for conditional templates. It recognizes EmptyDir and HostPath specifically; other volume sources are shown generically.

## Test Signals
`volumes_test.go` covers existence, EmptyDir/HostPath type checks, wrong HostPath paths, dual-source errors, and missing mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/volumes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/volumes_test.go -->
# sources/control-plane/rook/pkg/operator/test/volumes_test.go

## Purpose
This file tests basic volume and volume-mount assertion helpers.

## Important APIs, Types, and Functions
`TestVolumeExists()`, `TestVolumeIsEmptyDir()`, `TestVolumeIsHostPath()`, and `TestVolumeMountExists()` cover success and failure cases. `vols()` is a small slice builder.

## Control Flow, State, and Persistence
Tests are table-driven and pure. They assert only the presence or absence of errors.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 volume types and Go testing. These tests protect the helper library used by many operator pod-spec tests.

## Risks
Human-readable formatting and full `VolumesAndMountsTestDefinition.TestMountsMatchVolumes()` are not directly tested. Pointer-to-copy behavior of `getVolume()` and `getMount()` is not covered.

## Test Signals
Signals include correct detection of missing volumes/mounts, wrong source type, wrong HostPath path, and invalid dual EmptyDir/HostPath sources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/test/volumes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/dependents/dependents.go -->
# sources/control-plane/rook/pkg/util/dependents/dependents.go

## Purpose
`dependents.go` models resources that block deletion and builds standard Ceph CR status conditions for blocked deletion scenarios.

## Important APIs, Types, and Functions
Condition builders are `DeletionBlockedDueToDependentsCondition()`, `DeletionBlockedDueToNonEmptyPoolCondition()`, and `DeletionBlockedDueToNonEmptyRadosNSCondition()`. `DependentList` stores plural resource kinds to dependent names. Methods include `NewDependentList()`, `Empty()`, `Add()`, `PluralKinds()`, `OfKind()`, and `StringWithHeader()`.

## Control Flow, State, and Persistence
Conditions are returned in memory for callers to persist to CR status. `DependentList` stores state in a map. `StringWithHeader()` sorts formatted kind groups alphabetically for deterministic messages.

## Dependencies and Integration Points
It depends on Rook Ceph condition constants and Kubernetes core condition statuses. Reconciler code can use it to report deletion blockers on Ceph resources.

## Risks
Dependent names are not deduplicated or sorted within a kind. `PluralKinds()` returns map iteration order, so callers should not rely on ordering. Condition timestamps are not set here.

## Test Signals
`dependents_test.go` covers empty, single-kind, multi-dependent, multi-kind, missing-kind, string formatting, and alphabetical kind ordering. Condition builders are not directly tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/dependents/dependents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/dependents/dependents_test.go -->
# sources/control-plane/rook/pkg/util/dependents/dependents_test.go

## Purpose
This test validates `DependentList` storage and formatting behavior.

## Important APIs, Types, and Functions
`TestDependentList()` uses nested subtests for empty lists, one resource, multiple dependents, and multiple resource kinds. Local helpers check substring count and relative ordering.

## Control Flow, State, and Persistence
The tests operate on in-memory lists. They use `ElementsMatch()` where ordering is not guaranteed and explicit index comparison for formatted kind ordering.

## Dependencies and Integration Points
It depends on testify and strings. It protects deletion-blocking message generation used by Ceph resource reconcilers.

## Risks
Condition helper functions in `dependents.go` are untested. Name ordering within a kind is not asserted as sorted, only as containing expected names.

## Test Signals
Signals include empty detection, adding multiple names under the same plural kind, missing kind returning an empty list, header formatting with args, and deterministic alphabetical kind output.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/dependents/dependents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/display/bytes.go -->
# sources/control-plane/rook/pkg/util/display/bytes.go

## Purpose
`bytes.go` formats byte counts for display and converts between bytes and megabytes.

## Important APIs, Types, and Functions
Constants define binary units from `KiB` through `EiB`. `BytesToString()` chooses the largest unit threshold and formats two decimals for units larger than bytes. `BToMb()` rounds bytes to MiB. `MbTob()` multiplies MiB by 1024 squared.

## Control Flow, State, and Persistence
The functions are pure. `BToMb()` uses floating-point division and `math.Round()`.

## Dependencies and Integration Points
It depends on `fmt` and `math`. It integrates with CLI/status display paths that need human-readable storage sizes.

## Risks
`BToMb()` rounds rather than floors, which may surprise capacity calculations if used beyond display. `BytesToString()` reports binary units but `BToMb()` names the unit `Mb`, which can be ambiguous. Very large values are capped by uint64 and formatted as EiB.

## Test Signals
`bytes_test.go` checks one value per unit, zero, max uint64, and 50 MiB round-trip conversions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/display/bytes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/display/bytes_test.go -->
# sources/control-plane/rook/pkg/util/display/bytes_test.go

## Purpose
This file validates byte formatting and byte/MiB conversion helpers.

## Important APIs, Types, and Functions
`TestBytesToString()` asserts formatted strings for byte, KiB, MiB, GiB, TiB, PiB, EiB, zero, max uint64, `BToMb()`, and `MbTob()`.

## Control Flow, State, and Persistence
The test is pure and deterministic.

## Dependencies and Integration Points
It uses `math.MaxUint64` and testify. It protects user-facing size display.

## Risks
Boundary values just below each unit threshold are not covered. Rounding behavior in `BToMb()` is covered only for an exact 50 MiB value.

## Test Signals
Signals include two-decimal binary formatting and max uint64 rendering as `16.00 EiB`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/display/bytes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/error.go -->
# sources/control-plane/rook/pkg/util/error.go

## Purpose
`error.go` aggregates multiple errors into a single human-readable error message.

## Important APIs, Types, and Functions
`AggregateErrors(errs []error, format string, args ...interface{}) error` returns nil for no errors or an `errors.Errorf` with a formatted header and one indented line per error.

## Control Flow, State, and Persistence
The function is pure. It discards wrapped error structure and keeps only `err.Error()` text in the aggregate message.

## Dependencies and Integration Points
It depends on `fmt` and `github.com/pkg/errors`. Reconciler paths can use it to report multiple validation or cleanup failures together.

## Risks
Structured error identity is lost, so `errors.Is`/`As` cannot inspect original causes through the aggregate. Nil entries in a non-empty slice would panic when calling `err.Error()`.

## Test Signals
No direct mapped tests. Useful signals would cover empty lists, formatting args, multiple errors, nil error entries, and wrapped error identity expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/error.go -->
# sources/control-plane/rook/pkg/util/exec/error.go

## Purpose
`exec/error.go` defines Ceph CLI error wrapping and exit-status extraction for exec failures.

## Important APIs, Types, and Functions
`CephCLIError` stores an underlying error and command output; its `Error()` returns the output text. `ExitStatus(err)` recognizes `*os/exec.ExitError`, `k8s.io/client-go/util/exec.CodeExitError`, nested `CephCLIError`, and `syscall.Errno`.

## Control Flow, State, and Persistence
The logic is pure. `CephCLIError` recursively delegates status extraction to its wrapped `err`.

## Dependencies and Integration Points
It depends on Go `os/exec`, `syscall`, and Kubernetes client-go exec errors. Ceph command wrappers can preserve output while still allowing callers to branch on exit code.

## Risks
`CephCLIError` fields are unexported, so only package-local constructors or literals can create rich values. `Error()` hides the underlying error. `ExitStatus()` returns zero with `false` for unknown errors, which callers must check carefully.

## Test Signals
`error_test.go` covers unknown errors, `ExitError`, nested `CephCLIError`, and `CephCLIError` with unknown wrapped errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/error_test.go -->
# sources/control-plane/rook/pkg/util/exec/error_test.go

## Purpose
This file tests exit status extraction in the exec package.

## Important APIs, Types, and Functions
`TestExitStatus()` passes unknown errors, a synthetic `*exec.ExitError`, and `CephCLIError` wrappers to `ExitStatus()`.

## Control Flow, State, and Persistence
The test is table-driven and pure. The synthetic `os.ProcessState` returns status zero in this setup.

## Dependencies and Integration Points
It depends on Go `errors`, `os`, `os/exec`, and testing. It protects command-error handling used by Ceph wrappers.

## Risks
It does not cover `kexec.CodeExitError` or `syscall.Errno`, both supported by `ExitStatus()`. Synthetic `ProcessState` limits realism for nonzero exit codes.

## Test Signals
Signals include recursive status extraction through `CephCLIError` and false for unsupported error types.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/exec.go -->
# sources/control-plane/rook/pkg/util/exec/exec.go

## Purpose
`exec.go` implements Rook's local command execution abstraction, output capture, timeout handling, logging, and generic exit-code extraction.

## Important APIs, Types, and Functions
`Executor` defines command execution methods. `CommandExecutor` implements them. Methods include `ExecuteCommand()`, `ExecuteCommandWithEnv()`, `ExecuteCommandWithOutput()`, `ExecuteCommandWithCombinedOutput()`, `ExecuteCommandWithTimeout()`, and `ExecuteCommandWithStdin()`. `IsTimeout()` detects timeout errors. Internal helpers start commands, log stdout/stderr, run output-capturing commands, and append stderr details for output-only failures. `ExtractExitCode()` handles Go exec errors, Kubernetes exec errors, status errors, and some string-form errors.

## Control Flow, State, and Persistence
Commands are executed as OS subprocesses. Timeout execution sends interrupt on the first timeout tick and kill on the next. Output is trimmed. `logOutput()` may adjust capnslog repo logger level to show child process logs. There is no filesystem persistence except whatever commands perform.

## Dependencies and Integration Points
It depends on Go `os/exec`, capnslog, Kubernetes API/status and utils exec errors. It is a shared boundary for Rook's system and Ceph command invocations.

## Risks
Timeout handling uses repeated `time.After(timeout)`, so total kill time can be about twice the timeout. Environment override replaces the process environment instead of appending. `ExtractExitCode()` string parsing is fragile but useful as fallback. Logging command args can expose sensitive values if callers pass secrets.

## Test Signals
`exec_test.go` covers error text extraction, exit-code extraction variants, fake timeout detection, stdin/nil-stdin command execution, command failure, and timeout.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/exec_pod.go -->
# sources/control-plane/rook/pkg/util/exec/exec_pod.go

## Purpose
`exec_pod.go` executes commands in Kubernetes containers through the pod exec API and can copy local files into containers.

## Important APIs, Types, and Functions
`ExecOptions` describes command, namespace, pod, container, stdin, capture flags, and whitespace preservation. `RemotePodCommandExecutor` holds a Kubernetes clientset and REST config. `ExecWithOptions()` builds a pod exec request and streams via SPDY. `ExecCommandInContainerWithFullOutput()` finds the first pod with `app=<label>` and executes a command. `ExecCommandInContainerWithFullOutputWithTimeout()` prefixes commands with `timeout <seconds>`. `CopyLocalFileToContainer()` streams a local file to `cat - > dstPath` in the container.

## Control Flow, State, and Persistence
Exec streams are remote Kubernetes API calls. File copy reads a local file and writes remote container filesystem state. Output is trimmed unless `PreserveWhitespace` is true.

## Dependencies and Integration Points
It depends on client-go REST, pod exec parameter encoding, `remotecommand.NewSPDYExecutor`, Kubernetes pod listing, and shell availability in target containers. It supports Ceph commands from pods when the operator lacks direct network access.

## Risks
`CopyLocalFileToContainer()` interpolates `dstPath` into a shell command, so callers must not pass untrusted paths. The first matching pod is always chosen. Timeout behavior depends on the container having a `timeout` binary. SPDY exec requires RBAC and API server support.

## Test Signals
No direct mapped tests cover this file. Integration tests should cover no matching pod, stdout/stderr capture, whitespace preservation, timeout prefixing, RBAC failures, and file copy error reporting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/exec_pod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/exec_test.go -->
# sources/control-plane/rook/pkg/util/exec/exec_test.go

## Purpose
This file tests local exec helper behavior and exit-code extraction.

## Important APIs, Types, and Functions
`Test_assertErrorType()` checks stderr extraction for known exec error types. `TestMockExecHelperProcess()` exposes the helper process from `exec/test`. `TestExtractExitCode()` covers multiple error implementations and fallback string parsing. `TestFakeTimeoutError()` checks timeout detection. `TestExecuteCommandWithTimeout()` runs real simple commands.

## Control Flow, State, and Persistence
Tests execute local commands such as `cat`, `echo`, `false`, and `sleep`. The mock helper process relaunches the test binary with environment variables to simulate stdout/stderr/exit code.

## Dependencies and Integration Points
It depends on `exec/test` mock helpers, Kubernetes status/errors, Kubernetes utils exec errors, and testify. It protects command execution paths used by sys and Ceph utilities.

## Risks
Tests assume Unix-like commands are available. Timeout tests can be timing-sensitive on loaded systems. Remote pod exec is not covered.

## Test Signals
Signals include stdin capture, nil stdin output, nonzero exit errors, timeout errors, and exit code extraction from Go, Kubernetes, status, and string-form errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/log.go -->
# sources/control-plane/rook/pkg/util/exec/log.go

## Purpose
`exec/log.go` defines the package logger for exec utilities.

## Important APIs, Types, and Functions
The package variable `logger` is a capnslog package logger named `github.com/rook/rook`, subsystem `exec`.

## Control Flow, State, and Persistence
There is no control flow. The logger participates in global capnslog state configured elsewhere.

## Dependencies and Integration Points
It depends on capnslog and is used by local and remote exec helpers for command/debug/error logging.

## Risks
Package-level logging can expose command args or output if callers pass sensitive data. Logging behavior depends on global capnslog configuration.

## Test Signals
No direct tests are mapped. Logging behavior is indirectly exercised by exec tests and runtime command paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/test/mockexec.go -->
# sources/control-plane/rook/pkg/util/exec/test/mockexec.go

## Purpose
`mockexec.go` provides a mock implementation of the exec `Executor` interface and a helper process pattern for realistic exec errors in tests.

## Important APIs, Types, and Functions
`MockExecutor` exposes function fields for each executor method. Its methods call configured functions or return zero values. `MockExecCommandReturns()` reruns the current test binary with environment variables controlling stdout, stderr, and return code. `TestMockExecHelperProcess()` implements the helper process. `FakeTimeoutError()` builds an error string recognized by `exec.IsTimeout()`.

## Control Flow, State, and Persistence
Mock methods are in-memory callbacks. The helper process uses environment variables and exits with a requested code. It writes stderr before stdout by design.

## Dependencies and Integration Points
It depends on Go `os/exec`, `os`, `testing`, and time. It is used by sys tests and exec tests to simulate command behavior without invoking real system tools.

## Risks
`ExecuteCommandWithStdin()` checks `MockExecuteCommand` but calls `MockExecuteCommandWithStdin`, so if only stdin callback is set and `MockExecuteCommand` is nil, it returns nil without invoking the callback. `ExecuteCommandWithTimeout()` passes `time.Second` to the callback instead of the caller's timeout. Helper-process env values are raw strings, so embedded newlines or special values need care.

## Test Signals
The helper process is imported by `exec_test.go`. Sys tests use `MockExecutor` callbacks to control `lsblk`, `udevadm`, and other command outputs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/exec/test/mockexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/file.go -->
# sources/control-plane/rook/pkg/util/file.go

## Purpose
`file.go` provides small file utilities for logging file contents and creating temporary files with content.

## Important APIs, Types, and Functions
`WriteFileToLog(logger, path)` reads a cleaned path and logs contents or a warning. `CreateTempFile(content)` creates an unnamed temp file in the default temp directory and writes the provided content with mode `0400`.

## Control Flow, State, and Persistence
`WriteFileToLog()` performs read-only filesystem access. `CreateTempFile()` persists a temp file and returns the open file handle; callers are responsible for closing and removing it.

## Dependencies and Integration Points
It depends on `os`, `filepath`, capnslog, and pkg/errors. It integrates with code that needs to expose generated config files in logs or pass temp config files to subprocesses.

## Risks
Logging full file contents can leak secrets if called on sensitive files. `CreateTempFile()` uses `os.WriteFile()` after `os.CreateTemp()`, leaving the original file descriptor open and requiring caller cleanup. Temp files are created in the system default directory.

## Test Signals
No direct mapped tests. Useful signals would cover write/read mode, cleanup responsibility, read failures, and logging redaction expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/flags/flags.go -->
# sources/control-plane/rook/pkg/util/flags/flags.go

## Purpose
`flags.go` contains helpers for Cobra/pflag command validation, environment-backed flag defaults, and safe flag display.

## Important APIs, Types, and Functions
`VerifyRequiredFlags()` checks named string flags and returns a formatted missing-flags error. `SetFlagsFromEnv()` maps each flag to `PREFIX_FLAG_NAME` with uppercase and hyphens converted to underscores, setting values when env vars are non-empty. `GetFlagsAndValues()` returns `--name=value` strings and redacts values whose flag names match a regex filter.

## Control Flow, State, and Persistence
The functions mutate a `pflag.FlagSet` or build in-memory output. Environment variables are read at call time. Invalid env-derived flag values are logged via a package-level logger but not returned.

## Dependencies and Integration Points
It depends on Cobra, pflag, capnslog, regexp, os, and strings. Operator commands use these helpers for required configuration and diagnostics.

## Risks
`VerifyRequiredFlags()` only handles string flags. `SetFlagsFromEnv()` ignores empty env vars, so env cannot set a flag to empty. Regex errors in `GetFlagsAndValues()` are ignored, potentially disabling redaction for invalid filters.

## Test Signals
`flags_test.go` covers required string flags and redaction by flag-name regex. Env-backed setting and invalid regex behavior are not covered.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/flags/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/flags/flags_test.go -->
# sources/control-plane/rook/pkg/util/flags/flags_test.go

## Purpose
This file tests required string flag validation and flag value rendering/redaction.

## Important APIs, Types, and Functions
`TestStringFlags()` creates a Cobra command with two string flags and checks missing/both/none error messages. `TestGetFlagsAndValues()` verifies rendered `--flag=value` output and redaction for a flag name matching `secret`.

## Control Flow, State, and Persistence
Tests mutate an in-memory Cobra flag set. No environment variables are used.

## Dependencies and Integration Points
It depends on Cobra and testify. It protects CLI validation and logging output.

## Risks
`SetFlagsFromEnv()` has no coverage. Non-string required flags, invalid flag names, and invalid exclude regex are not covered.

## Test Signals
Signals include comma formatting for multiple missing flags, singular error formatting, complete success with nil error, and value masking as `*****`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/flags/flags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/log/log.go -->
# sources/control-plane/rook/pkg/util/log/log.go

## Purpose
`log.go` wraps capnslog calls with namespace or namespaced-name prefixes.

## Important APIs, Types, and Functions
`NamedInfo()`, `NamedWarning()`, `NamedError()`, `NamedDebug()`, and `NamedTrace()` prefix with `types.NamespacedName.String()`. `NamespacedInfo()`, `NamespacedWarning()`, `NamespacedError()`, `NamespacedDebug()`, and `NamespacedTrace()` prefix messages with `[namespace]` and format the message.

## Control Flow, State, and Persistence
The functions are thin logging wrappers. They do not return errors or persist data beyond log output.

## Dependencies and Integration Points
It depends on capnslog and Kubernetes `types.NamespacedName`. Reconciler code can use it to make logs easier to correlate with namespaces/resources.

## Risks
Formatting is performed before passing to capnslog, so format-string mistakes happen inside `fmt.Sprintf`. Sensitive args are logged as provided. The `namespace` parameter can be a full namespaced name when using `Named*`.

## Test Signals
No direct mapped tests. Useful coverage would need a log capture mechanism to assert prefixes and formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/log/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/logging.go -->
# sources/control-plane/rook/pkg/util/logging.go

## Purpose
`logging.go` configures Rook's global capnslog log level with special handling for trace-level logging.

## Important APIs, Types, and Functions
`DefaultLogLevel` is `capnslog.INFO`. `SetGlobalLogLevel(userLogLevelSelection, logger)` maps user `TRACE` to `DEBUG`, maps `TRACE_INSECURE` to real `TRACE`, parses the level, defaults invalid values to INFO, rejects levels more verbose than TRACE, and calls `capnslog.SetGlobalLogLevel()`.

## Control Flow, State, and Persistence
The function mutates global logging state in capnslog. It logs parse/defaulting decisions with the provided logger.

## Dependencies and Integration Points
It depends on capnslog. Operator startup and CLI paths can use it to apply user-selected logging while avoiding accidental trace logs that may reveal secrets.

## Risks
Global log level changes affect all package loggers in-process, including tests. The string handling is case-sensitive through capnslog parsing and the explicit `TRACE`/`TRACE_INSECURE` checks.

## Test Signals
`logging_test.go` covers supported levels, invalid input defaulting, and the special trace mappings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/logging_test.go -->
# sources/control-plane/rook/pkg/util/logging_test.go

## Purpose
This file tests global log-level selection behavior.

## Important APIs, Types, and Functions
`TestSetGlobalLogLevel()` passes INFO, DEBUG, WARNING, ERROR, TRACE, TRACE_INSECURE, and INVALID to `SetGlobalLogLevel()` and uses `logger.LevelAt()` to verify desired and next-more-verbose visibility.

## Control Flow, State, and Persistence
The test mutates capnslog global state for each subtest. It does not restore a previous global level at the end.

## Dependencies and Integration Points
It depends on capnslog and testify. It protects operator logging configuration.

## Risks
Because logging state is global, parallel tests could interfere if added. The test does not cover lowercase/mixed-case inputs.

## Test Signals
Signals include TRACE being downgraded to DEBUG, TRACE_INSECURE enabling real TRACE, and invalid input defaulting to INFO.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/logging_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/retry.go -->
# sources/control-plane/rook/pkg/util/retry.go

## Purpose
`retry.go` provides generic retry loops with fixed delay or timeout semantics.

## Important APIs, Types, and Functions
`Retry(maxRetries, delay, f)` retries a function returning error until success or retry count is exceeded. `RetryFunc` returns `(done bool, err error)`. `RetryWithTimeout(f, period, timeout, description)` polls until done, timeout, or a terminal error with `done=true`.

## Control Flow, State, and Persistence
Both functions sleep using `time.After()`. `RetryWithTimeout()` starts a timeout channel once and intentionally calls `f()` one final time after timeout to avoid edge races. Errors during non-done polling are logged and retried.

## Dependencies and Integration Points
It depends on time, fmt, pkg/errors, and the package logger from `file.go`. It is used by reconciliation paths waiting for Kubernetes or Ceph state.

## Risks
There is no context cancellation. `Retry()` treats `maxRetries` as retries after the first attempt, so total attempts are `maxRetries + 1`. `RetryWithTimeout()` can run slightly longer than timeout and period and can block indefinitely if `f()` blocks.

## Test Signals
No direct mapped tests. Useful tests would cover attempt counts, terminal error behavior, timeout final retry, and zero/negative timing values.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/device.go -->
# sources/control-plane/rook/pkg/util/sys/device.go

## Purpose
`device.go` discovers, classifies, parses, and evaluates local block devices for Rook/Ceph OSD provisioning.

## Important APIs, Types, and Functions
Constants define device types such as `disk`, `part`, `crypt`, `lvm`, `mpath`, and `loop`. Data types include `CephVolumeInventory`, `CephVolumeLVMList`, `Partition`, and `LocalDisk`. Discovery functions include `ListDevices()`, `GetDevicePartitions()`, `GetDeviceProperties()`, `GetDevicePropertiesFromPath()`, `GetUdevInfo()`, `GetDeviceFilesystems()`, `GetDiskUUID()`, `ListDevicesChild()`, and `IsDeviceEncrypted()`. Classification functions include `IsLV()`, `GetDiskDeviceType()`, `GetDiskDeviceClass()`, `CheckIfDeviceAvailable()`, and `GetLVName()`. Parsers include `parseUUID()`, `parseKeyValuePairString()`, `parseFS()`, and `parseUdevInfo()`.

## Control Flow, State, and Persistence
The file shells out through `exec.Executor` to `lsblk`, `udevadm`, `sgdisk`, `dmsetup`, and `ceph-volume`. It parses text or JSON output and returns in-memory structs. Availability checks select Ceph inventory or LVM list logic based on `IsLV()`.

## Dependencies and Integration Points
It depends on Rook exec abstraction, Google UUID parsing, Go `os/exec.LookPath`, environment variables for crush class override, and host storage tools. It integrates with OSD device discovery and provisioning.

## Risks
Parsing is mostly ad hoc and can break on spaces or unexpected quoting in `lsblk`/`udevadm` output. `CheckIfDeviceAvailable()` accepts `pvcBacked` but does not use it. Host command availability and permissions are required. `IsDeviceEncrypted()` compares exact output to `crypt`, so trailing newlines can affect results depending on executor trimming.

## Test Signals
`device_test.go` covers UUID parsing, filesystem parsing, partition parsing including LVM child names, child listing, disk type, and env override for device class. Ceph-volume availability, LV name parsing, encryption detection, and command failures have limited or no coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/device.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/device_test.go -->
# sources/control-plane/rook/pkg/util/sys/device_test.go

## Purpose
This file tests block-device parsing and classification helpers.

## Important APIs, Types, and Functions
Fixtures model `udevadm` and `lsblk` output. `TestFindUUID()` validates GPT UUID parsing. `TestParseFileSystem()` and `TestParseUdevInfo()` parse udev data. `TestGetPartitions()` uses a mock executor to simulate several `lsblk`/`udevadm` sequences. `TestListDevicesChildListDevicesChild()` checks child splitting. `TestGetDiskDeviceType()` and `TestGetDiskDeviceClass()` check classification and env override.

## Control Flow, State, and Persistence
Tests are pure except for `t.Setenv()` and mock executor callback state. `TestGetPartitions()` uses a run counter to return different outputs across sequential command calls.

## Dependencies and Integration Points
It depends on `util/exec/test.MockExecutor`, testify, and sys parsers. It protects host-device discovery logic without requiring real disks.

## Risks
The run-counter mock makes `TestGetPartitions()` order-sensitive and hard to extend. Command failure paths, malformed JSON from ceph-volume, `GetLVName()`, and availability checks are not covered.

## Test Signals
Signals include preserving partition labels from udev, calculating unused space, treating Ceph LVM names as partitions, child device splitting, rotational/nvme/ssd classification, and crush class env override.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/device_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/log.go -->
# sources/control-plane/rook/pkg/util/sys/log.go

## Purpose
`sys/log.go` defines the package logger for system utility code.

## Important APIs, Types, and Functions
The package variable `logger` is a capnslog logger named `github.com/rook/rook`, subsystem `sys`.

## Control Flow, State, and Persistence
There is no control flow. Logging behavior follows capnslog global state.

## Dependencies and Integration Points
It depends on capnslog and is used by device parsing/discovery code.

## Risks
System utility logs can include host command output and device metadata. Verbosity is controlled globally.

## Test Signals
No direct tests are mapped. Device tests indirectly exercise code paths that log through this logger.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/parse.go -->
# sources/control-plane/rook/pkg/util/sys/parse.go

## Purpose
`parse.go` provides a small grep-like helper for finding the first matching line in text.

## Important APIs, Types, and Functions
`Grep(input, searchFor string) string` returns an empty string for empty input or pattern, otherwise scans lines and returns the first line whose content matches the regular expression.

## Control Flow, State, and Persistence
The function is pure. It ignores regex compilation/matching errors by treating them as no match.

## Dependencies and Integration Points
It depends on regexp and strings. System parsing code can use it to extract specific lines from command output.

## Risks
Invalid regex patterns are silently ignored. The function returns only the first match and preserves original whitespace. Callers needing literal matching must escape regex characters.

## Test Signals
`parse_test.go` covers empty inputs, single-line prefix and substring matching, and multi-line first-match behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/parse_test.go -->
# sources/control-plane/rook/pkg/util/sys/parse_test.go

## Purpose
This file tests the `Grep()` helper.

## Important APIs, Types, and Functions
`TestGrep()` delegates to `testGrep()` for empty input/patterns, single-line matches, anchored regexes, and multi-line matches.

## Control Flow, State, and Persistence
The test is pure and deterministic.

## Dependencies and Integration Points
It depends on testify. It protects command-output parsing helpers that need first matching lines.

## Risks
Invalid regex handling is not tested. Multiple matching lines are only indirectly covered by expecting the first `test` line in a multi-line fixture.

## Test Signals
Signals include substring matching, start anchors, no-match empty result, preserved leading whitespace, and first-line-wins behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/util/sys/parse_test.go -->
