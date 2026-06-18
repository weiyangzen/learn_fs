# Research Report: subset-b-000447

This grouped report covers the requested Rook source files for subset `subset-b-000447`. Each file section is source-tree aligned and bounded for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/discover/discover.go -->
# sources/control-plane/rook/pkg/daemon/discover/discover.go

Purpose: implements the `discover` daemon package that discovers local block devices on a Kubernetes node and publishes their JSON representation to a per-node ConfigMap. It supports both periodic probing and udev-triggered probing, with optional `ceph-volume inventory` enrichment.

Important APIs/types/functions: `Run()` is the package entry point and reads `NODE_NAME`/pod namespace env vars, computes the local device ConfigMap name, does an initial `updateDeviceCM()`, then loops on SIGTERM, probe interval, and coalesced udev events. `CephVolumeInventory` models selected JSON fields from `ceph-volume inventory`. `DeviceListsEqual()` unmarshals two serialized `[]sys.LocalDisk` values and delegates to `checkDeviceListsEqual()`. `probeDevices()` calls `clusterd.DiscoverDevices()`, enriches each disk with partitions/filesystem/empty state, and optionally embeds raw ceph-volume inventory JSON. `getCephVolumeInventory()` returns a map keyed by `/dev/<name>` path. `rawUdevBlockMonitor()`, `udevBlockMonitor()`, and `matchUdevEvent()` implement udev monitoring and regex filtering.

Control flow: startup validates the `clusterd.Context`, initializes global process state, and updates the ConfigMap immediately. Udev monitoring runs in a goroutine that shells out to `stdbuf -oL udevadm monitor -u -s block`, filters `add`/`remove` block events, and suppresses noisy device mapper/rbd/nbd events by default or by `DISCOVER_DAEMON_UDEV_BLACKLIST`. `udevBlockMonitor()` debounces multiple raw events into one probe per configured period. Each probe discovers devices, marshals JSON, gets or creates the ConfigMap, and updates only when `DeviceListsEqual()` decides the observed device set changed in a way relevant to storage consumers.

State and persistence: the file uses package globals for node name, namespace, ConfigMap name/cache, last serialized device list, udev debounce period, and ceph-volume mode. Persistent state is the Kubernetes ConfigMap `local-device-<node>` containing key `devices`; owner references are copied from the running discover pod when the ConfigMap is first created. Equality intentionally ignores USB devices and treats some transitions asymmetrically: non-empty to empty and partition removal are important, while empty to non-empty and partition creation are not.

Dependencies and integration points: integrates with `clusterd` and `pkg/util/sys` for device discovery and with Kubernetes CoreV1 ConfigMaps. It shells out to system tools through Rook's executor path and directly uses `exec.Command` for `udevadm`. Consumers elsewhere in Rook depend on the ConfigMap data shape and `DeviceListsEqual()` behavior to decide if device changes should trigger storage work.

Risks: package globals make tests and repeated invocations stateful. The udev monitor uses regexes from an environment variable, so invalid regexes disable monitoring. `checkMatchingDevice()` falls back to device name, which can be unstable across reboots, but avoids missed matches when UUID/serial are missing. `updateDeviceCM()` caches the ConfigMap pointer and could be sensitive to stale resource versions after external edits. `getCephVolumeInventory()` logs but continues if an individual device has no inventory record, so missing ceph-volume data is non-fatal.

Test signals: `discover_test.go` covers probing with mocked `lsblk`/udev outputs, udev match filtering, device-list equality semantics, and ceph-volume inventory parsing/error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/discover/discover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/discover/discover_test.go -->
# sources/control-plane/rook/pkg/daemon/discover/discover_test.go

Purpose: unit tests the discover daemon's device probing, udev filtering, equality heuristics, and ceph-volume inventory parsing using mocked executors and synthetic device data.

Important APIs/types/functions: `TestProbeDevices()` exercises `probeDevices()` through `clusterd.DiscoverDevices()` and `sys` helpers by matching expected executor arguments. `TestMatchUdevMonitorFiltering()` verifies `matchUdevEvent()` emits add/remove and rejects change/device-mapper events. `TestDeviceListsEqual()` directly covers `checkDeviceListsEqual()`. `TestGetCephVolumeInventory()` covers `getCephVolumeInventory()` with normal, empty, error, and partial JSON output.

Control flow: tests build `exectest.MockExecutor` functions that return canned command output based on argument patterns. The probe test simulates one disk with a filesystem and one partitioned disk, validating that parent disk filtering and partition emptiness are represented as expected. Inventory tests sequence executor returns with a `run` counter to validate multiple scenarios through one test body.

State and persistence behavior: no Kubernetes state is persisted in these tests; they focus on pure and executor-backed logic. The tests do mutate global package state indirectly through shared package functions and assume no parallel execution. Environment state is not heavily manipulated here except through command mocking.

Dependencies and integration points: the test relies on Rook's `exectest.MockExecutor`, `clusterd.Context`, `sys.LocalDisk`, and `testify/assert`. It validates the discover package's assumptions about lower-level Linux command parsers without invoking real system commands.

Risks: `TestGetCephVolumeInventory()` depends on exact JSON marshaling order for expected strings; changes to struct fields or Go JSON output would require updates. The mock executor pattern in `TestProbeDevices()` silently returns empty output for unexpected calls, which can hide missing assertion coverage unless downstream behavior fails.

Test signals: coverage is strong for core equality rules, default udev matching, basic probing, and inventory parsing. It does not directly test `Run()`, ConfigMap create/update behavior, signal handling, or udev debounce timing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/discover/discover_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/client-daemonset.yaml -->
# sources/control-plane/rook/pkg/daemon/multus/client-daemonset.yaml

Purpose: Go template for Multus validation client DaemonSets. Each rendered DaemonSet simulates one Ceph daemon/client type per selected node and checks connectivity to the validation web server over one or more Multus-attached networks.

Important APIs/types/functions: consumed by `templates.go` via embedded variable `clientDaemonSet` and rendered from `clientTemplateConfig`. Template fields include `.NodeType`, `.ClientType`, `.ClientID`, `.NetworksAnnotationValue`, `.Placement`, `.NginxImage`, and `.NetworkNamesAndAddresses`.

Control flow: `ValidationTest.startClients()` renders one DaemonSet per desired OSD and non-OSD client slot. The pod template annotates `k8s.v1.cni.cncf.io/networks` so Multus attaches public and/or cluster networks. For each requested target address, it creates a container with an exec readiness probe running `curl --insecure <addr>:8080`; readiness is therefore the validation signal used by the state machine.

State and persistence behavior: resources are Kubernetes DaemonSets that persist until owner ConfigMap deletion or explicit cleanup. Labels encode app, node type, client type, and client ID for selection and expected-count calculations.

Dependencies and integration points: depends on Nginx image containing `curl`, Multus network annotations, Kubernetes DaemonSet scheduling, node selectors/tolerations from `PlacementConfig`, and readiness probe behavior. It integrates with `clientAppLabel()` and `numPodsReadyWithLabel()` in Go code.

Risks: if the configured image lacks `curl`, validation fails as a networking symptom. `successThreshold: 12`, `failureThreshold: 1`, and `periodSeconds: 5` intentionally make readiness sensitive; slow or bursty networks may look flaky. Empty placement can schedule broadly, so node type definitions must be accurate. Address formatting for IPv6 is handled before template rendering in Go.

Test signals: no direct YAML test; coverage comes indirectly through template rendering paths and validation workflow logic. No test asserts exact security context, readiness probe settings, or annotation rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/client-daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/config.go -->
# sources/control-plane/rook/pkg/daemon/multus/config.go

Purpose: defines the user-facing configuration model and defaults for Rook's Multus validation test, plus helpers for YAML rendering, parsing, validation, and node placement heuristics.

Important APIs/types/functions: `ValidationTestConfig` contains namespace, service account, public/cluster NAD names, timeouts, host-check mode, image, and node type definitions. `NodeConfig`, `PlacementConfig`, and `TolerationType` model daemon counts and scheduling constraints. Constructors include `NewDefaultValidationTestConfig()`, `NewDedicatedStorageNodesValidationTestConfig()`, and `NewArbiterValidationTestConfig()`. `ToYAML()`, `String()`, `ValidationTestConfigFromYAML()`, `Validate()`, `TotalDaemonsPerNode()`, `TotalOSDsPerNode()`, `TotalOtherDaemonsPerNode()`, and `BestNodePlacementForServer()` are the main methods.

Control flow: package init sets `DefaultValidationNamespace` from the pod namespace env var when available. Constructors populate conservative default node profiles. `ToYAML()` renders the embedded `config.yaml` template with comments rather than relying on YAML library comment support. `Validate()` accumulates all user errors before returning one combined error, checking required network input, duration floors, image, OSD coverage, and RFC 1123 node type keys. `BestNodePlacementForServer()` picks the node type with the most OSDs, breaking ties by total daemon count, so the web server lands on a node likely to have both networks and enough resources.

State and persistence behavior: no Kubernetes persistence; configuration is in-memory and serializable to YAML. Defaults are mutable package vars, and namespace defaulting depends on process environment.

Dependencies and integration points: integrates with `k8sutil.PodNamespaceEnvVar`, Kubernetes `corev1.Toleration`, Kubernetes DNS validation helpers, and `gopkg.in/yaml.v2`. The resulting config is embedded into `ValidationTest`, which drives template rendering and the validation state machine.

Risks: `TolerationType.ToJSON()` renders tolerations inline in YAML, so invalid or surprising JSON/YAML interoperability would affect config rendering. `Validate()` requires at least one OSD-bearing node type, which intentionally disallows pure client-only tests. `BestNodePlacementForServer()` is heuristic and may be wrong for clusters where OSD count does not imply both NADs are available.

Test signals: `config_test.go` covers YAML round trips with comments and full nested config, plus server-placement heuristic cases.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/config.yaml -->
# sources/control-plane/rook/pkg/daemon/multus/config.yaml

Purpose: human-readable Go template used by `ValidationTestConfig.ToYAML()` to emit a documented Multus validation config file.

Important APIs/types/functions: embedded as `ConfigYaml` in `config.go` and rendered with a `ValidationTestConfig`. It references scalar fields such as `.Namespace`, `.PublicNetwork`, `.ClusterNetwork`, `.ResourceTimeout`, `.FlakyThreshold`, `.HostCheckOnly`, and `.NginxImage`, then iterates `.NodeTypes`, placement selectors, and tolerations.

Control flow: the template outputs comments explaining each parameter and renders node type entries from the config map. Tolerations are emitted via `$toleration.ToJSON`, relying on the custom method in `TolerationType`.

State and persistence behavior: it is a static embedded template; rendered YAML can be persisted by users as CLI/tool configuration, but this file itself has no runtime state.

Dependencies and integration points: tightly coupled to `ValidationTestConfig` field names and Go template execution in `loadTemplate()`. The comments describe operational expectations for Rook-Ceph clusters, CSI daemon counts, and host-check-only mode.

Risks: map iteration order for `NodeTypes`, node selectors, and tolerations from Go maps may make rendered output order nondeterministic for map-backed fields. Template indentation must remain valid YAML for empty maps/slices. Documentation comments can drift from validation logic if fields or defaults change.

Test signals: `TestValidationTestConfig_YAML` confirms rendered YAML contains comments and round-trips into an equivalent config for representative empty, default, and full configs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/config_test.go -->
# sources/control-plane/rook/pkg/daemon/multus/config_test.go

Purpose: validates the Multus validation config model's YAML rendering/parsing and web server placement heuristic.

Important APIs/types/functions: `TestValidationTestConfig_YAML()` exercises `ToYAML()` and `ValidationTestConfigFromYAML()`. `TestValidationTestConfig_BestNodePlacementForServer()` tests `BestNodePlacementForServer()` across empty, worker-only, OSD, and tie-breaking scenarios.

Control flow: YAML tests iterate empty, default, and full configs, asserting comments are present and round-tripped structs are equal. Placement tests construct node type maps and compare returned `PlacementConfig` or expected error.

State and persistence behavior: no external state; tests are pure except for default constructors that may reflect package-level defaults already initialized from environment.

Dependencies and integration points: uses `testify/assert`, Go `reflect.DeepEqual`, and `time.Duration` fields. It indirectly covers `config.yaml` compatibility with `gopkg.in/yaml.v2`.

Risks: the "full config" uses node type identifiers like `osdOnlyNodes` that are not RFC 1123 compatible, but the test only round-trips YAML and does not call `Validate()`. There is no direct coverage for validation error aggregation or default namespace env behavior.

Test signals: strong for serialization stability and placement selection; missing for `Validate()`, dedicated storage/arbiter constructors, and toleration JSON failure behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/host-daemonset.yaml -->
# sources/control-plane/rook/pkg/daemon/multus/host-daemonset.yaml

Purpose: template for host-network checker DaemonSets that validate whether Kubernetes hosts can reach the web server's Multus public-network address.

Important APIs/types/functions: embedded as `hostCheckerDaemonSet` and rendered by `generateHostCheckerDaemonSet()` from `hostCheckerTemplateConfig`. Uses `.NodeType`, `.Placement`, `.NginxImage`, and `.PublicNetworkAddress`.

Control flow: `startHostCheckers()` creates one DaemonSet per node type after the web server is running and a public network address has been discovered. Each pod uses `hostNetwork: true` and a readiness probe that curls the server public address on port 8080. The state machine waits for all host checker pods to become Running, then Ready.

State and persistence behavior: rendered DaemonSets are owned by the validation owner ConfigMap and deleted before client tests unless host-check-only mode exits after this phase.

Dependencies and integration points: depends on host-network permission policy, node placement constraints, Nginx image with `curl`, and the public NAD being routable from host networking. Selected by `hostCheckerAppLabel()`.

Risks: host-network pods may be blocked by Pod Security admission or service account permissions. Failures can indicate host routing/firewall problems rather than Multus attachment problems. The readiness probe assumes `curl` availability.

Test signals: no direct template assertions. Runtime logic includes suggestions for host checker failures in `validation.go`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/host-daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/image-pull-daemonset.yaml -->
# sources/control-plane/rook/pkg/daemon/multus/image-pull-daemonset.yaml

Purpose: template for image-puller DaemonSets used to pre-pull the Nginx image and discover how many nodes match each configured node type.

Important APIs/types/functions: embedded as `imagePullDaemonSet` and rendered by `generateImagePullDaemonSet()` from `imagePullTemplateConfig`. Labels include app and node type for expected-count calculations.

Control flow: `startImagePullers()` creates one DaemonSet per node type at the start of validation. The state machine lists these DaemonSets, waits for scheduled counts to stabilize, verifies no node type overlap, then waits for all puller pods to run before deleting the puller DaemonSets.

State and persistence behavior: resources are temporary and owner-referenced to the validation owner ConfigMap. Their scheduled pod counts become in-memory expected-count state used later to calculate host checker and client expectations.

Dependencies and integration points: depends on Kubernetes DaemonSet scheduling, node selector/toleration correctness, and image pull success. It intentionally does not attach Multus networks, so failures isolate Kubernetes/image issues.

Risks: overlapping node type placements are detected later by pod node names, not by template rendering. Read-only root filesystem and non-root security context rely on image compatibility. If image pullers cannot schedule, validation cannot infer expected client counts.

Test signals: indirect unit coverage for per-node type count helpers in `resources_test.go`; no direct YAML rendering assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/image-pull-daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/nginx-config.yaml -->
# sources/control-plane/rook/pkg/daemon/multus/nginx-config.yaml

Purpose: template for the ConfigMap mounted into the validation web server pod, configuring Nginx to respond on port 8080 with the connecting client's remote address.

Important APIs/types/functions: embedded as `nginxConfigTemplate` and rendered by `generateWebServerConfigMap()`. It produces ConfigMap `multus-validation-test-web-server-conf` with key `server.conf`.

Control flow: `startWebServer()` creates this ConfigMap before creating the web server pod to avoid initial mount failures. The Nginx server listens on IPv4 and IPv6 and returns `$remote_addr` as plain text for any path.

State and persistence behavior: temporary Kubernetes ConfigMap owned by the validation owner ConfigMap. Its data is static for a validation run.

Dependencies and integration points: consumed by `nginx-pod.yaml` via a ConfigMap volume at `/etc/nginx/conf.d`. The returned client address is mostly diagnostic; readiness checks only require HTTP success.

Risks: if Nginx image path or config include conventions differ, the mounted config may not be loaded. The template has no dynamic fields today but still goes through template rendering.

Test signals: no direct test for ConfigMap content or server response; rendering errors would surface when template parsing/unmarshaling is exercised indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/nginx-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/nginx-pod.yaml -->
# sources/control-plane/rook/pkg/daemon/multus/nginx-pod.yaml

Purpose: template for the single validation web server pod that attaches to the configured public and cluster Multus networks and serves a simple Nginx endpoint.

Important APIs/types/functions: embedded as `nginxPodTemplate` and rendered by `generateWebServerPod()` from `webServerTemplateConfig`. Uses `.NetworksAnnotationValue`, `.Placement`, and `.NginxImage`.

Control flow: `startWebServer()` renders the pod using the best node placement from config, owner-references it, and creates it after the Nginx ConfigMap. `getWebServerInfo()` later reads its Multus network status and readiness before clients and host checkers are started.

State and persistence behavior: a single Kubernetes Pod owned by the validation owner ConfigMap. It persists for the duration of the validation and is removed during cleanup.

Dependencies and integration points: depends on Multus network annotation, Nginx image UID/GID 101 behavior, ConfigMap volume from `nginx-config.yaml`, emptyDir mounts for Nginx writable paths, and Kubernetes readiness probe. It integrates with `getNetworksFromPod()` to discover public and cluster IPs.

Risks: the YAML says `apiVersion: apps/v1` for `kind: Pod`; Kubernetes Pods normally use `apiVersion: v1`, so this template is risky unless unmarshaled object creation normalizes or tests do not exercise API server validation. Network annotation must be non-empty for configured networks. Security settings assume the Nginx unprivileged image layout.

Test signals: no direct test validates the rendered Pod against Kubernetes API validation. Runtime failures would surface as web server creation/readiness errors in the validation workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/nginx-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/resources.go -->
# sources/control-plane/rook/pkg/daemon/multus/resources.go

Purpose: implements Kubernetes resource creation, inspection, expected-count tracking, and cleanup helpers for the Multus validation test.

Important APIs/types/functions: `podNetworkInfo` records web server node/public/cluster addresses. `createOwningConfigMap()` creates the owner ConfigMap used as a garbage-collection root. `startWebServer()`, `getWebServerInfo()`, `startImagePullers()`, `startHostCheckers()`, and `startClients()` create or inspect validation resources. `perNodeTypeCount` plus `Increment()`, `Total()`, and `Equal()` model scheduled counts. `getImagePullPodCountPerNodeType()`, `ensureOneImagePullPodPerNode()`, `getNumRunningPods()`, `numPodsReadyWithLabel()`, `getPodsWithLabel()`, and `cleanUpTestResources()` support state-machine polling and cleanup.

Control flow: the validation run first creates an owner ConfigMap, then the web server and image pullers. Image puller DaemonSet status establishes the expected number of nodes per node type. Host checker and client DaemonSets are generated per node type, with expected pod counts derived from image-puller scheduling. Cleanup deletes the owner ConfigMap with foreground propagation, best-effort deletes client pods, and polls until the owner disappears.

State and persistence behavior: all validation resources are owner-referenced to a single ConfigMap named `multus-validation-test-owner`; deletion of that ConfigMap is the intended cleanup mechanism. `perNodeTypeCount` is in-memory state passed through validation states. Resource status is read from Kubernetes DaemonSets and Pods.

Dependencies and integration points: uses Kubernetes typed clients for CoreV1 and AppsV1, API errors, owner references, DeleteCollection, and polling utilities. It depends on template generation functions in `templates.go` and pod/network helpers in `util.go`.

Risks: creating a fixed owner ConfigMap name means only one validation run per namespace can proceed; stale resources block later runs. `ensureOneImagePullPodPerNode()` detects overlapping node type definitions only after pods exist. Cleanup's best-effort client pod deletion uses foreground delete options with default grace for the owner, and CNI IPAM exhaustion is a noted concern. `getImagePullPodCountPerNodeType()` requires exactly one DaemonSet per node type and nonzero scheduling.

Test signals: `resources_test.go` covers `perNodeTypeCount` helper behavior. Resource creation, cleanup, owner references, and Kubernetes API interactions are not directly unit tested in this file's companion test.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/resources_test.go -->
# sources/control-plane/rook/pkg/daemon/multus/resources_test.go

Purpose: tests the small `perNodeTypeCount` map helper used by the Multus validation state machine for expected pod counts per node type.

Important APIs/types/functions: `Test_perNodeTypeCount_Increment()`, `Test_perNodeTypeCount_Equal()`, and `Test_perNodeTypeCount_Total()` cover mutation, equality, and aggregate count behavior.

Control flow: each test table initializes a map pointer, calls the relevant method, and compares to expected maps or values. Equality tests cover empty maps, differing keys, matching keys with differing values, and multiple-key cases.

State and persistence behavior: purely in-memory tests. The methods mutate only the receiver map and do not interact with Kubernetes.

Dependencies and integration points: uses `testify/assert` for comparisons. The helper under test feeds image-puller stabilization, host-checker expectations, and client expected pod counts in `validation.go`.

Risks: tests do not cover nil map pointers or nil map values; current production paths initialize maps before use. The broader correctness of scheduled-count discovery is not covered here.

Test signals: good confidence in basic count math, but limited coverage of resource-listing functions that produce these counts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/statemachine.go -->
# sources/control-plane/rook/pkg/daemon/multus/statemachine.go

Purpose: provides a generic polling state-machine runner for Multus validation states with per-state timeout handling, suggestion accumulation, and context cancellation behavior.

Important APIs/types/functions: `validationState` interface requires `Run(ctx, vsm)`. `validationStateMachine` stores current state, timer, owner refs, results, last suggestions/error, and done flag. Methods are `SetNextState()`, `Exit()`, `Run()`, `resetTimer()`, and `exitContextCanceled()`.

Control flow: `Run()` creates a timer with `vt.ResourceTimeout`, loops until context cancellation, timeout, or `Exit()`, resets the timer whenever the state changes, runs the current state's `Run()`, records latest suggestions/error, and sleeps two seconds between iterations. A timeout returns the last error wrapped with a validation timeout and adds the last suggestions to results.

State and persistence behavior: no external persistence. It carries in-memory execution state and references to Kubernetes owner refs for downstream states. State transitions are explicit via `SetNextState()`, and completion is explicit via `Exit()`.

Dependencies and integration points: used by `ValidationTest.Run()` in `validation.go`. Depends on `ValidationTestResults` suggestion collection and `meta.OwnerReference` for states that create resources.

Risks: `resetTimer()` drains `timer.C` when `Stop()` returns false; if the timer has fired but the channel was already drained, this pattern can block in some timer misuse scenarios, though here it is used inside one loop. The `default` select branch plus sleep means it polls rather than blocking on state-specific watches. On context cancellation, the last error may be nil, so wrapping `%w` with nil can produce less actionable output.

Test signals: no direct state-machine unit tests. Behavior is indirectly exercised only if validation workflow tests exist elsewhere; this subset does not include them.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/statemachine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/templates.go -->
# sources/control-plane/rook/pkg/daemon/multus/templates.go

Purpose: embeds Multus validation YAML templates and renders them into typed Kubernetes Pod, ConfigMap, and DaemonSet objects.

Important APIs/types/functions: embedded templates are `nginxPodTemplate`, `nginxConfigTemplate`, `imagePullDaemonSet`, `hostCheckerDaemonSet`, and `clientDaemonSet`. Template config structs model web server, image puller, host checker, and client inputs. Generation methods include `generateWebServerPod()`, `generateWebServerConfigMap()`, `generateImagePullDaemonSet()`, `generateHostCheckerDaemonSet()`, and `generateClientDaemonSet()`. Helpers include label/name functions, `generateNetworksAnnotationValue()`, `applyServiceAccountToPodSpec()`, and `loadTemplate()`.

Control flow: each generator renders a text/template, unmarshals YAML into the corresponding Kubernetes API type, applies service account where relevant, and returns the object to resource creation helpers. Client template config builds the set of target server addresses and wraps IPv6 addresses in brackets before templates append `:8080`.

State and persistence behavior: no persistent state; outputs are in-memory Kubernetes objects later created by `resources.go`. Template strings are embedded at compile time.

Dependencies and integration points: depends on `text/template`, Kubernetes API structs, Kubernetes YAML unmarshaler, and `ValidationTest` config. Labels produced here are consumed by selectors in `resources.go` and state machine logic in `validation.go`.

Risks: templates are only parsed at runtime, so syntax errors surface when a validation path renders them. YAML API version/kind mismatches may not be caught until object creation. `generateNetworksAnnotationValue()` returns comma-separated network names, so names containing unexpected commas would break annotation semantics. Map iteration in templates can affect deterministic output ordering.

Test signals: no direct tests of rendered Kubernetes objects in this subset. `config_test.go` indirectly tests `loadTemplate()` for the config template only.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/templates.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/util.go -->
# sources/control-plane/rook/pkg/daemon/multus/util.go

Purpose: supplies logging abstraction and low-level pod/network utility functions for Multus validation.

Important APIs/types/functions: `Logger` is a minimal interface with info/debug/warning formatting methods. `SimpleStderrLogger` implements it to stderr. `getNetworksFromPod()` extracts desired public/cluster IP addresses from a pod's Multus network status. `podIsRunning()`, `podIsReady()`, and `networkNamespacedName()` are status/parsing helpers.

Control flow: `getNetworksFromPod()` calls the network-attachment-definition client utility to parse pod network status, validates that attached networks and IPs exist, parses each network name relative to the pod namespace, matches desired public/cluster `NamespacedName`s, accumulates debugging suggestions for missing or malformed data, and returns addresses only when all desired networks are present. `networkNamespacedName()` reuses `ParseNetworkAnnotation()` because the desired private parser is not exported.

State and persistence behavior: no persistence. Suggestions are returned as slices for accumulation in validation results.

Dependencies and integration points: uses `github.com/k8snetworkplumbingwg/network-attachment-definition-client/pkg/utils`, Kubernetes Pod status, and `types.NamespacedName`. It is central to `getWebServerInfoState`, because web server network discovery gates later validation phases.

Risks: `getNetworksFromPod()` reads `net.IPs[0]` after appending a suggestion for no IP but without continuing, so a network attachment with zero IPs can panic. If `networkNamespacedName()` returns an error, `nsName` remains zero-value but code still compares it after adding a suggestion. The helper treats any IP as sufficient and does not distinguish IPv4/IPv6 preferences.

Test signals: no direct tests in this subset for network parsing, no-IP behavior, or readiness helpers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/validation.go -->
# sources/control-plane/rook/pkg/daemon/multus/validation.go

Purpose: implements the public Multus validation test orchestration and all concrete validation state-machine states.

Important APIs/types/functions: `ValidationTest` combines a Kubernetes client, logger, and `ValidationTestConfig`. `ValidationTestResults` stores debugging suggestions and renders `SuggestedDebuggingReport()`. States include `getExpectedNumberOfImagePullPodsState`, `ensureNodeTypesDoNotOverlapState`, reusable `verifyAllPodsRunningState`, `deleteImagePullersState`, `getWebServerInfoState`, `startHostCheckersState`, `verifyAllHostCheckersReadyState`, `deleteHostCheckersState`, `startClientsState`, and `verifyAllClientsReadyState`. Public methods are `Run()` and `CleanUp()`.

Control flow: `Run()` validates config, short-circuits host-check-only mode when no public network is configured, creates the owner ConfigMap, starts the web server and image pullers, then starts the state machine. The state machine stabilizes expected image-puller counts, verifies non-overlapping node types, waits for image pullers, deletes them, discovers web server Multus addresses, optionally starts host checkers, validates host reachability, starts Multus clients, waits for Running then Ready, and exits. Client readiness timing is tracked to flag flaky networks when readiness spreads beyond `FlakyThreshold`.

State and persistence behavior: Kubernetes resources are persisted during a run via helpers in `resources.go`, and in-memory state carries expected counts, web server network info, and suggestion history. Cleanup delegates to owner ConfigMap deletion. Suggestions describe likely root causes and are returned whether the test fails or succeeds with flakiness.

Dependencies and integration points: depends on Kubernetes client-go, `types.NamespacedName`, templates/resources helpers, network parsing helpers, and config validation. Intended callers can use the library with their own logger or default stderr logger.

Risks: the workflow is sensitive to accurate DaemonSet scheduled counts and timing thresholds. Fixed owner resource names prevent concurrent tests in one namespace. Some errors call `Exit()` immediately while others keep polling; incorrect classification can either fail too early or wait until timeout. `podSchedulerDebounceTime` must remain below state timeout. Flakiness detection starts when ready count first increases and may warn even when slow scheduling, not network, is the cause.

Test signals: this subset has no direct tests for the full state machine. Related tests cover config, count helpers, and templates indirectly, leaving resource orchestration and suggestion paths mostly integration-tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/multus/validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/util/cmdreporter.go -->
# sources/control-plane/rook/pkg/daemon/util/cmdreporter.go

Purpose: implements a small command runner intended for Kubernetes Jobs that executes a command and stores stdout, stderr, and return code in a ConfigMap for the operator to read.

Important APIs/types/functions: constants define app label and ConfigMap data keys. `CmdReporter` holds Kubernetes client, command, args, ConfigMap name/namespace, and context. `NewCmdReporter()` validates construction. `CommandToCmdReporterFlagArgument()` and `CmdReporterFlagArgumentToCommand()` JSON-encode/decode Kubernetes-style command/args. `Run()` orchestrates command execution and ConfigMap persistence. `runCommand()` executes and captures output. `saveToConfigMap()` creates or updates the ConfigMap.

Control flow: `Run()` executes the command first; nonzero exit codes are captured as retcodes and are not returned as errors if the process ran to completion. Then it saves results to a ConfigMap. `runCommand()` tees stdout and stderr to buffers and container stdout, builds args from `cmd[1:] + args`, and extracts Unix exit status from `exec.ExitError`. `saveToConfigMap()` creates a new labeled ConfigMap if absent, or updates an existing ConfigMap only if the app label is absent/empty or already `rook-cmd-reporter`.

State and persistence behavior: persistent output is a ConfigMap with `stdout`, `stderr`, and `retcode`. Existing values are overwritten with warnings. The app label is used as a safety boundary to avoid modifying ConfigMaps owned by other apps.

Dependencies and integration points: uses `os/exec`, Kubernetes CoreV1 ConfigMaps, Rook's `k8sutil.AppAttr`, and capnslog. Intended integration is with job templates that pass a serialized command through a flag and then read the result ConfigMap.

Risks: stderr is teed to `os.Stdout` instead of `os.Stderr`, which may be intentional but can confuse log streams. If an existing ConfigMap has nil `Labels` or nil `Data`, assigning into maps can panic; code assumes maps are initialized when existing. Return-code parsing is Unix-specific through `syscall.WaitStatus`. Command logging includes command and args, so callers must avoid passing secrets as args.

Test signals: `cmdreporter_test.go` covers JSON round trip, constructor validation, command execution/retcode capture, ConfigMap creation, and refusal to overwrite ConfigMaps with another app label.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/util/cmdreporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/util/cmdreporter_test.go -->
# sources/control-plane/rook/pkg/daemon/util/cmdreporter_test.go

Purpose: tests command reporter serialization, constructor validation, execution capture, and ConfigMap safety behavior.

Important APIs/types/functions: `TestCommandMarshallingUnmarshalling()` covers command JSON helpers. `TestNew()` covers `NewCmdReporter()`. `TestRunner_Run()` uses a helper process to exercise `Run()`, `runCommand()`, and `saveToConfigMap()`. `mockExecCommand()` and `TestCmdReporterHelperProcess()` implement the fake command process.

Control flow: tests replace package variable `execCommand` with `mockExecCommand`, which re-invokes the test binary with `GO_WANT_HELPER_PROCESS=1`. Environment variables control fake stdout, stderr, retcode, and printed command. The tests verify generated ConfigMap data and app-label conflict behavior with fake Kubernetes clients.

State and persistence behavior: uses in-memory fake Kubernetes clientsets. Environment variables and package-level `execCommand` are mutated and restored around tests.

Dependencies and integration points: uses `client-go` fake clientset, `testify/assert`, OS process re-exec testing pattern, and Rook `k8sutil.AppAttr` constants.

Risks: tests assume Unix-like process exit behavior and environment variable isolation. Existing ConfigMaps in tests always initialize `Labels` and `Data`, so nil-map edge cases in production are not covered. Stderr teeing to stdout is not explicitly asserted.

Test signals: good coverage for expected command and ConfigMap workflow, including nonzero retcodes as successful reporter runs and app-label protection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/util/cmdreporter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/client/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/client/controller.go

Purpose: implements the controller-runtime reconciler for `CephClient` custom resources, creating/updating Ceph auth clients and associated Kubernetes Secrets, handling deletion, status, and CephX key rotation.

Important APIs/types/functions: `ReconcileCephClient` stores controller client, scheme, cluster context/info, operator context, and event recorder. `Add()`, `newReconciler()`, and `add()` register the controller and watches for `CephClient` and owned Secrets. `Reconcile()` wraps `reconcile()` with reporting. Core methods include `createOrUpdateClient()`, `reconcileCephClientSecret()`, `deleteClient()`, `ValidateClient()`, `genClientEntity()`, `getClientName()`, `generateClientName()`, `updateStatus()`, `generateStatusInfo()`, and `generateCephUserSecretName()`.

Control flow: reconcile fetches the CR, adds finalizer, initializes status when absent, waits for a ready CephCluster, loads cluster info, handles deletion by deleting the Ceph auth entity and removing finalizer, validates caps/name, detects monitor Ceph version, determines whether CephX key rotation is needed, creates or updates the auth user and secret, and updates CR status to Ready with cephx status and secret info. Secret reconciliation handles create, update-if-owned, or delete-if-owned when `RemoveSecret` is set.

State and persistence behavior: persistent state includes Ceph auth users/caps/keys, Kubernetes Secrets containing the key under client name plus CSI `userID`/`userKey`, finalizers on `CephClient`, and status fields including phase, observed generation, info, and CephX status. `RemoveSecret` allows auth user management without preserving the generated Secret.

Dependencies and integration points: integrates with controller-runtime, Rook Ceph client command helpers (`AuthGetKey`, `AuthGetOrCreateKey`, `AuthUpdateCaps`, `AuthRotate`, `AuthDelete`), cluster readiness/load helpers, keyring rotation helpers, Kubernetes Secret ownership helpers, and reporting/events.

Risks: caps are generated from a Go map, so command argument order is nondeterministic. `ValidateClient()` rejects reserved names but does not deeply validate cap syntax. `createOrUpdateClient()` calls `AuthGetKey()` and falls back to `AuthGetOrCreateKey()` on any error, so non-not-found errors may be treated as create attempts. Secret update/delete safety depends on owner reference helpers. Status updates use retry but may leave failure status if create/update fails after partial Ceph auth changes.

Test signals: `controller_test.go` covers validation, entity generation, reconcile success/wait paths, status info, custom secret names, secret ownership behavior, and end-to-end key rotation scenarios with mocked Ceph commands.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/client/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/client/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/client/controller_test.go

Purpose: tests the CephClient controller's validation, auth entity generation, reconciliation behavior, secret status/ownership semantics, and CephX key rotation.

Important APIs/types/functions: `TestValidateClient()`, `TestGenerateClient()`, `TestCephClientController()`, `TestBuildUpdateStatusInfo()`, `TestRemoveSecretUpdateStatusInfo()`, `TestCustomSecretname()`, `TestReconcileCephClient_reconcileCephClientSecret()`, and `TestKeyRotation()` cover the main controller helpers and paths.

Control flow: tests use fake controller-runtime clients, fake Kubernetes clientsets, fake Rook clientsets, and mocked executors for Ceph commands. `TestCephClientController()` progresses from no cluster to not-ready cluster to ready cluster and verifies status/secret creation. Secret reconciliation table tests pre-create ownership variants and assert create/update/delete/error behavior. Key rotation subtests share state to model first reconcile, no-op reconcile, brownfield unknown status, requested rotations, and no extra rotation.

State and persistence behavior: fake Kubernetes state includes CephClient CRs, CephCluster CRs, mon secrets, and generated client secrets. `TestKeyRotation()` intentionally mutates the same CR and fake clients across subtests.

Dependencies and integration points: tests exercise integration between controller-runtime fake client, client-go fake clientset, Rook Ceph fake clientsets, `exectest.MockExecutor`, status reporting, and keyring rotation helpers.

Risks: shared subtest state in `TestKeyRotation()` means subtests are order-dependent and cannot run independently. Some tests use map-based caps and assert by string containment rather than exact command order, matching production nondeterminism. Fake clients may not enforce all Kubernetes API validation and owner-reference constraints.

Test signals: broad coverage of high-risk controller behavior, especially secret ownership and CephX rotation. Deletion finalizer path and reserved-name validation are less deeply exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/client/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus.go

Purpose: periodically checks Ceph cluster health, updates `CephCluster.status`, manages selected Ceph health settings, records cluster version, and force-deletes stuck Rook pods on NotReady nodes during unhealthy states.

Important APIs/types/functions: `cephStatusChecker` stores Rook context, cluster info, interval, controller client, and external flag. `newCephStatusChecker()` constructs it with env/CR interval overrides. `checkCephStatus()` runs the monitoring loop. `checkStatus()` calls Ceph status and status update logic. `configureHealthSettings()` handles insecure global ID warnings. `updateCephStatus()` writes status and daemon versions. `toCustomResourceStatus()` converts Ceph CLI status into CR status. `updateClusterCephVersion()`, `cephStatusOnError()`, `forceDeleteStuckRookPodsOnNotReadyNodes()`, and `getRookPodsOnNode()` support auxiliary behavior.

Control flow: the checker immediately checks status, then loops until its internal context is canceled or monitoring map entry is removed. On Ceph command errors, it writes `HEALTH_ERR` with the error message unless the operator is still initializing. On non-OK health, it attempts stuck pod cleanup. Status conversion updates health, details, timestamps, capacity, previous health, and FSID. Version update is performed separately by the cluster controller.

State and persistence behavior: persistent state is `CephCluster.status.cephStatus` and `status.cephVersion`. Capacity is preserved when Ceph reports zero total bytes and prior capacity exists. `LastChanged` and `PreviousHealth` track health transitions. Force deletion mutates Kubernetes Pod state only for matching Rook pods that are stuck on NotReady nodes.

Dependencies and integration points: integrates with Ceph client command helpers (`StatusWithUser`, `GetAllCephDaemonVersions`), Rook status reporting, Kubernetes clients, cluster health routine tracking, version labeling, and k8sutil node/pod helpers.

Risks: periodic loop uses `time.After()` each iteration, which is simple but not externally jittered. `configureHealthSettings()` calls `config.DisableInsecureGlobalID()` based on health checks and ignores its return, so failure is not surfaced. Force-deleting pods during non-OK health is powerful and depends on label matching. `toCustomResourceStatus()` timestamps use current UTC time, making tests time-sensitive.

Test signals: `cephstatus_test.go` covers status conversion, checker interval construction, insecure global ID behavior, stuck pod force deletion, and Rook pod label filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus_test.go

Purpose: tests Ceph cluster status conversion, status checker construction, insecure global ID health behavior, and stuck-pod cleanup helpers.

Important APIs/types/functions: `TestCephStatus()` covers `toCustomResourceStatus()` and `formatTime()`. `TestNewCephStatusChecker()` covers interval/external construction. `TestConfigureHealthSettings()` tests `configureHealthSettings()`. `TestForceDeleteStuckRookPodsOnNotReadyNodes()` tests force deletion behavior. `TestGetRookPodsOnNode()` tests Rook pod label filtering.

Control flow: status conversion tests mutate current/new status across health and capacity scenarios. Health-setting tests use a mocked executor to detect whether Ceph config set is attempted. Stuck-pod tests create fake nodes/pods, mark nodes NotReady, and verify only terminating matching pods are deleted. Pod label tests create many app labels and compare sorted expected names.

State and persistence behavior: uses fake Kubernetes clientsets for nodes and pods and in-memory status structs. Some time assertions compare formatted current timestamps rather than fixed clocks.

Dependencies and integration points: relies on Rook operator test clientsets, Ceph client structs, `exectest.MockExecutor`, Kubernetes API objects, and `testify/assert`.

Risks: time-based equality in capacity tests can be fragile around second boundaries. Fake clients may not fully model deletion timestamps and force deletion semantics. `TestNewCephStatusChecker()` does not cover the env var override path.

Test signals: good coverage for conversion edge cases and pod filtering. Periodic `checkCephStatus()` loop and `updateCephStatus()` API persistence are not directly tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephstatus_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephx.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/cephx.go

Purpose: implements CephCluster admin CephX keyring generation, admin key rotation, interrupted-rotation recovery, status updates, and temporary credential handling for Rook's primary `client.admin` identity.

Important APIs/types/functions: constants `adminRotatorSecretPrefix` and `adminRotatorUsername` define the temporary rotator identity. `adminKeyAccessCaps` defines full admin caps. `claimAdminRotationLock()`/`releaseAdminRotationLock()` serialize rotation per namespace. `genKeyring()` formats keyring text. `rotateAdminCephxKey()` decides and starts rotation. `recoverPriorAdminCephxKeyRotation()` resumes interrupted rotations. `entityExistsInAuthList()`, `rotateAdminCephxKeyUsingRotator()`, `finalizeAdminKeyRotation()`, `updateCephClusterAdminCephxStatus()`, `adminRotationTmpDir()`, and `minimalCopyClusterInfo()` implement the detailed workflow.

Control flow: normal rotation first validates that the active user is `client.admin`, asks keyring policy whether rotation is needed, updates status if not, then claims a namespace lock. It creates a temporary `client.admin-rotator` with full caps, stores its keyring in a Secret, writes keyring files under the operator config dir, verifies rotator permissions, rotates `client.admin`, verifies the new admin key, updates in-memory cluster info, rewrites ceph config, updates the mon access Secret, deletes the rotator auth entity, finalizes status/cleanup, and reloads the manager. Recovery checks for a persisted rotator Secret, rewrites connection config if needed, detects whether cleanup was the only interrupted step, or reruns the rotation using the stored rotator keyring.

State and persistence behavior: persistent state includes the temporary rotator auth entity, `rook-ceph-admin-rotator...` Secret, temporary keyring files under `<ConfigDir>/<namespace>/admin-rotate`, updated `rook-ceph-mon` access Secret, and `CephCluster.status.cephx.admin`. An in-memory mutex/map prevents simultaneous rotations in one operator process. Finalization deletes temp files and the rotator Secret, updates status, and triggers manager reload.

Dependencies and integration points: depends on Ceph auth helpers (`AuthList`, `AuthRotate`, `AuthDelete`, `WriteKeyring`), keyring secret store and rotation policy helpers, mon connection config writing, cluster access secret updates, status reporting, controller manager reload, and Kubernetes conflict retry.

Risks: rotation intentionally uses `context.Background()` copies so it can continue after parent reconcile cancellation; this is safer for completion but can outlive caller expectations. Recovery relies on the rotator Secret as durable marker. The in-memory lock does not coordinate across multiple operator replicas. `genKeyring()` must not log keys; callers mostly follow that. Successful rotation returns a sentinel error to restart reconcile, so callers must treat it as expected. Temp files are kept on failure for debugging, which has secret-handling implications.

Test signals: no companion `cephx_test.go` is included in this requested subset, but client controller tests cover non-admin CephClient rotation behavior. Direct admin rotation/recovery behavior should be covered elsewhere or with focused tests because it touches high-risk credential state.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/cephx.go -->
