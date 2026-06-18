# Research: subset-b-000450

Grouped research for Rook Ceph monitor, monitoring, node daemon, and OSD config files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon_test.go

## Purpose
This is the broad behavioral test suite for the Ceph monitor cluster implementation. It validates monitor startup, persisted endpoint state, EndpointSlice generation, quorum utilities, stretch cluster arbiter flows, failover/resource cleanup decisions, cephx key rotation, and floating monitor support. It also provides reusable fixtures such as `testGenMonConfig()`, `newTestStartCluster()`, `newCluster()`, and `setCommonMonProperties()` that many monitor tests depend on.

## Important APIs, Types, And Functions
The fixtures construct fake Kubernetes clientsets, controller-runtime fake clients, mock Ceph executors, and `Cluster` instances with `ClusterInfo`, monitor specs, mappings, and owner refs. Tests exercise public and package-level APIs including `Start()`, `startMon()`, `persistExpectedMonDaemonsInConfigMap()`, `persistExpectedMonDaemonsAsEndpointSlice()`, `saveMonConfig()`, `getStoredMaxMonID()`, `commitMaxMonID()`, `monInQuorum()`, `fullNameToIndex()`, `waitForQuorumWithMons()`, `monFoundInQuorum()`, `ConfigureArbiter()`, `findAvailableZone()`, `monVolumeClaimTemplate()`, `checkForExtraMonResources()`, `getMonPlacement()`, `readyToConfigureArbiter()`, `crushWeightsBalanced()`, `hasMonPathChanged()`, `isMonIPUpdateRequiredForHostNetwork()`, `RotateMonCephxKeys()`, and floating mon template helpers.

## Control Flow And State
The suite simulates monitor lifecycle paths: initial cluster bootstrap creates secrets and the first monitor deployment; restart paths re-read existing state and remain idempotent; endpoint persistence updates ConfigMaps and EndpointSlices; max monitor ID is only advanced by explicit commit; failover cleanup only removes extra monitor deployments when the expected monitor set and deployment count make that safe. The tests use fake API state as persistence: ConfigMaps store endpoint strings, scheduling mapping JSON, and max monitor IDs; EndpointSlices store IPv4/IPv6 monitor addresses; Secrets store monitor keys; Deployments represent live monitor resources. Floating monitor tests add a ConfigMap-backed parameter source and verify `startMon()` chooses the DRBD template path for the configured floating daemon.

## Dependencies And Integration Points
The tests integrate fake Kubernetes APIs, controller-runtime fake clients, Ceph client test helpers, mock command execution, Rook owner refs, Ceph version labels, CSI scheme registration, and Rook Kubernetes helpers. They are effectively integration-style unit tests for the monitor package, covering interactions with Kubernetes resources and Ceph command outputs without a real cluster.

## Risks And Test Signals
Important risk coverage includes host-network restarts, mixed IPv4/IPv6 EndpointSlices, stale service/deployment recovery, stretch arbiter CRUSH balance gates, Ceph version-dependent arbiter tolerance, skip-reconcile labels, path migration between PVC and hostPath, and cephx key rotation only on supported Ceph versions. The floating mon tests signal newer risk areas: built-in template params override ConfigMap collisions, missing ConfigMaps fail deployment, labels differ for floating vs normal mons, and canary scheduling skips floating mons. A notable residual risk is that many assertions rely on fake clients and mocked command output, so real Kubernetes immutability, scheduling, and DRBD runtime behavior are not fully exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node.go

## Purpose
This file derives monitor scheduling network information from Kubernetes `Node` objects. It turns a node into `opcontroller.MonScheduleInfo`, choosing the IP address Rook should use for monitor endpoints when host networking or node-based monitor placement is involved.

## Important APIs, Types, And Functions
`monIPAnnotation` is the annotation key `network.rook.io/mon-ip`. `getNodeInfoFromNode(n v1.Node)` returns a `MonScheduleInfo` populated with the Kubernetes node name, hostname label from `k8sutil.LabelHostname()`, and an address. Address precedence is explicit annotation, then `NodeInternalIP`, then `NodeExternalIP`.

## Control Flow And State
The function is read-only. It first creates schedule info from node metadata, then checks annotations for a custom monitor IP and returns immediately if present. If no annotation exists, it scans `n.Status.Addresses` for an internal IP and falls back to an external IP. If no usable address is found, it returns an error. No Kubernetes writes or persistent state updates happen here; persistence happens later when monitor scheduling information is saved to endpoint ConfigMaps.

## Dependencies And Integration Points
The function depends on Kubernetes core API node fields, Rook Kubernetes label helpers, and the monitor package logger. Its output feeds monitor assignment and endpoint persistence through `opcontroller.MonScheduleInfo`.

## Risks And Test Signals
The main risk is selecting the wrong address in clusters with multiple network planes; the annotation override is the escape hatch. `node_test.go` covers no-address errors, internal-IP precedence over external IP, external-only fallback, and annotation override. Hostname label absence is not treated as an error here, so downstream scheduling logic must tolerate or validate an empty hostname where required.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node_test.go

## Purpose
This test file validates node-related monitor behavior: monitor pod placement/host-network behavior, resource memory startup tolerance, and address extraction from Kubernetes nodes.

## Important APIs, Types, And Functions
Tests exercise `makeMonPod()`, `Start()`, and `getNodeInfoFromNode()`. `TestNodeAffinity` constructs mon placement affinity and labels fake nodes to reflect schedulability inputs. `TestHostNetworkSameNode` verifies that a host-networked cluster cannot place three monitors on the same node even when multiple-per-node is otherwise enabled. `TestPodMemory` runs monitor startup across several resource request/limit combinations. `TestHostNetwork` verifies DNS policy, `HostNetwork`, `--public-addr`, and absence of `--public-bind-addr` when a monitor uses host networking. `extractArgValue()` is a local helper for flag assertions.

## Control Flow And State
The tests use fake Kubernetes nodes and fake Rook cluster contexts. They mutate node labels/status and cluster specs, then inspect generated pods or cluster startup errors. They do not persist durable state beyond fake API objects. The host network test captures an important state distinction: a monitor's `UseHostNetwork` setting is preserved independently of the current cluster-level network spec.

## Dependencies And Integration Points
Dependencies include fake Kubernetes clients from Rook test helpers, Ceph client test cluster info, Rook placement/resource APIs, and monitor helpers from `mon_test.go`. The tests integrate monitor pod generation with cluster spec fields such as network, resources, and placement.

## Risks And Test Signals
The tests signal that monitor scheduling is sensitive to host networking, node label availability, and pod resource env vars. They cover the address precedence implemented in `node.go`. `TestNodeAffinity` sets up affinity-related state but contains no final assertion in the visible file, so it is more of a fixture/regression scaffold than a complete behavioral check.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate.go

## Purpose
This file defines a controller-runtime predicate used to detect meaningful monitor endpoint changes in the monitor endpoint ConfigMap. Its main use is triggering bootstrap peer token updates when monitor endpoint scheduling changes.

## Important APIs, Types, And Functions
`PredicateMonEndpointChanges[T *corev1.ConfigMap]()` returns `predicate.TypedFuncs[T]`. Create, delete, and generic events are ignored. Update events are considered only for ConfigMaps named `EndpointConfigMapName`. `wereMonEndpointsUpdated(namespace, oldCMData, newCMData)` compares the `mapping` JSON field by unmarshalling into `opcontroller.Mapping` and comparing the `Schedule` map.

## Control Flow And State
On update, the predicate casts the old and new objects to ConfigMaps, checks the name, and calls the mapping comparison helper. The helper requires both old and new `mapping` keys. It unmarshals both mappings; malformed JSON logs at debug level and returns false. If schedule lengths differ, the endpoint set changed. If lengths match, it sorts keys from the old schedule and deep-compares each old schedule entry against the corresponding new entry.

## Dependencies And Integration Points
The code depends on controller-runtime predicates/events, Rook monitor endpoint naming, `opcontroller.Mapping`, JSON decoding, sorting, `reflect.DeepEqual`, and Rook namespaced logging. It integrates with reconciler watch filters for ConfigMap updates.

## Risks And Test Signals
The comparison intentionally ignores create/delete events and malformed mapping updates, which avoids noisy reconciles but could miss repair opportunities after invalid data. A code risk is that `newKeys` is built by iterating over `oldMappingToGo.Schedule`; because the resulting `newKeys` is not used, this is harmless but misleading. The deep compare by old keys will still detect deleted/changed entries when lengths match because missing new entries compare unequal. `predicate_test.go` covers missing keys, identical content with different map order, changed monitor IP, and changed length.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate_test.go

## Purpose
This file provides focused table-driven tests for monitor endpoint mapping change detection.

## Important APIs, Types, And Functions
`TestWereMonEndpointsUpdated` calls `wereMonEndpointsUpdated("ns", oldCMData, newCMData)` directly with ConfigMap-like data maps. Test cases cover absent old mapping, absent new mapping, identical JSON content, identical schedules in different JSON/map order, same number of monitors with one changed IP address, and different schedule length.

## Control Flow And State
The tests do not create Kubernetes objects. They provide raw map data to isolate the JSON comparison helper. State is represented entirely by the `mapping` key containing serialized `opcontroller.Mapping` JSON.

## Dependencies And Integration Points
The file depends only on Go testing and package-local monitor code. It indirectly validates the data format produced by monitor endpoint persistence because it uses JSON strings shaped like `{"node":{...}}`.

## Risks And Test Signals
The tests confirm order-insensitive comparison and ensure missing mapping fields do not trigger endpoint updates. They also show that endpoint update detection is scoped to the schedule mapping, not the endpoint string. Malformed JSON is not covered here, though the implementation logs and returns false in that path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service.go

## Purpose
This file creates and exports Kubernetes Services for Ceph monitors. Monitor services provide stable ClusterIPs for monitor endpoints and optional multicluster exported addresses.

## Important APIs, Types, And Functions
`(c *Cluster) createService(mon *monConfig)` builds a `v1.Service` named after the monitor resource with labels from `c.getLabels()`, selector labels for the monitor pod, and one or two TCP service ports. `addServicePort()` from `util.go` is used for msgr1 and msgr2. `(c *Cluster) exportService(service *v1.Service, monDaemon string)` exports the service through `k8sutil.ExportService()` and removes monitor canary deployments afterward.

## Control Flow And State
`createService` sets an owner reference, adds msgr1 only when the monitor's configured port is not the default msgr2 port, always adds msgr2, and optionally pins `Spec.ClusterIP` to `mon.PublicIP` when a service is missing. This supports disaster recovery when a service was deleted but monitor endpoint state still knows the expected ClusterIP. It then calls `k8sutil.CreateOrUpdateService`. If the resulting service is nil, it logs an error and returns nil without a Kubernetes object. `exportService` defers canary cleanup until after export because multicluster DNS may require the canary pod to be running.

## Dependencies And Integration Points
The code depends on Kubernetes Services, Rook owner references, monitor labels, Rook service create/update helpers, Kubernetes API error classification, and multicluster service export. It integrates with monitor deployment startup and disaster recovery endpoint preservation.

## Risks And Test Signals
The critical risk is accidentally changing an existing ClusterIP, which Kubernetes does not allow and which would break monitor endpoints. The code only sets `ClusterIP` when the service is not found. `service_test.go` covers the disaster recovery path: existing services are not overwritten, but after deletion the expected public IP is assigned as the service ClusterIP.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service_test.go

## Purpose
This test file validates monitor service creation and ClusterIP preservation/recovery behavior.

## Important APIs, Types, And Functions
`TestCreateService` constructs a monitor `Cluster` with a fake Kubernetes client and calls `c.createService(m)` repeatedly. It inspects the returned service and deletes the fake service to simulate disaster recovery.

## Control Flow And State
The first call creates a monitor service without `PublicIP`, so the fake service has an empty ClusterIP. The second call sets `m.PublicIP` but leaves the service present, verifying the existing service's ClusterIP is not changed. The test then deletes the service and calls `createService` again, verifying `Spec.ClusterIP` is set to the expected monitor public IP when recreating a missing service.

## Dependencies And Integration Points
The test depends on Rook fake Kubernetes clientsets, monitor cluster construction, and the admin test cluster info. It validates behavior at the Kubernetes Service API object layer rather than through higher-level monitor startup.

## Risks And Test Signals
The test directly covers the disaster recovery condition documented in `service.go`. It does not assert labels/selectors/ports, so port selection and service identity rely on broader monitor tests or Kubernetes helper tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec.go

## Purpose
This file generates Kubernetes Deployment, Pod, PVC, and floating monitor resources for Ceph monitors. It is the main monitor spec construction layer, translating `CephCluster` monitor/network/storage/security/logging settings into Kubernetes workload definitions and Ceph daemon command lines.

## Important APIs, Types, And Functions
Key constants are `cephMonCommand` and `monContainerName`. `getLabels()` returns legacy and app labels plus optional PVC/zone/daemon labels. `GetFailureDomainLabel()` and `getFailureDomainName()` choose topology labels for zone or stretch cluster placement. `makeDeployment()`, `makeDeploymentPVC()`, and `makeMonPod()` build normal monitor resources. `makeChownInitContainer()`, `makeMonFSInitContainer()`, and `makeMonDaemonContainer()` build containers. Floating monitor support is implemented by `makeFloatingMonDeployment()`, `buildFloatingMonTemplateParams()`, `floatingMonMsgr2Value()`, `floatingMonTemplateToDeployment()`, and `renderFloatingMonTemplate()`. `UpdateCephDeploymentAndWait()` wraps deployment update gating with Ceph ok-to-stop/ok-to-continue checks.

## Control Flow And State
Normal deployment generation creates metadata, version/Ceph labels, owner refs, pod template, a single replica, and recreate strategy. Pod generation starts with chown and mkfs init containers, a mon daemon container, base volumes, service account, host network flag, priority class, and security context. It adds a log collector sidecar when enabled, PVC-specific unreachable-node toleration, host-network DNS policy, Multus annotations, and zone affinity when required. PVC generation applies the selected zone/default volume claim template and injects a default storage request when neither a request nor a limit is configured.

The mon daemon command always includes daemon flags, foreground mode, `--public-addr`, and `--setuser-match-path`. If the monitor is msgr2-only, it disables msgr1 and computes a bind address with IPv4/IPv6/dual-stack rules. Host-network monitors skip `--public-bind-addr`. Zone-aware monitors receive `--set-crush-location`, and arbiter zone selection records `c.arbiterMon` for later reconciliation. Probe specs are generated then overwritten by cluster health-check configuration if provided.

Floating monitor generation uses embedded DRBD YAML instead of the normal pod builder. It builds a stateful data path, merges ConfigMap parameters with built-ins, renders the template, applies owner refs/labels/annotations, and then patches resource requirements into named containers.

## Dependencies And Integration Points
This file depends on the CephCluster API, Rook controller helpers for labels, volumes, env vars, probes, and deployment updates, Kubernetes API types, embedded templates, text/template, YAML decoding, Ceph version labels, and environment variables such as the operator namespace. It integrates with monitor startup, scheduling, storage selection, log collection, network providers, stretch cluster placement, and upgrade orchestration.

## Risks And Test Signals
High-risk areas include immutable deployment selectors, host vs pod networking address selection, msgr2-only binding on IPv6/dual-stack, PVC defaults, zone affinity, arbiter location configuration, template rendering, and privileged DRBD floating monitor behavior. `spec_test.go` covers pod/deployment resource and label expectations, PVC defaults, failure-domain labels, run-as-root env handling, probes, and msgr2 bind variants. `mon_test.go` adds floating monitor parameter, label, scheduling, and update-path coverage. Residual risk remains around actual scheduler behavior, Multus runtime behavior, and DRBD mount/demote correctness because tests use fake clients and rendered object inspection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec_test.go

## Purpose
This file tests monitor Kubernetes spec generation: Deployments, pod templates, PVCs, scheduling requirements, failure-domain labels, security context, probes, and msgr2 binding behavior.

## Important APIs, Types, And Functions
`TestPodSpecs` and `testPodSpec` build clusters and monitor configs for both new-style IDs (`a`) and legacy IDs (`mon0`), with hostPath and PVC variants. They exercise `makeDeployment()` and `makeMonDaemonContainer()`. `checkMsgr2Required()` inspects command-line flags for `--ms-bind-msgr1=false` and `--public-bind-addr`. `TestDeploymentPVCSpec` covers `makeDeploymentPVC()`. `TestRequiredDuringScheduling`, `TestGetFailureDomainLabel`, and `TestMakeMonSecurityContext` cover smaller spec helpers.

## Control Flow And State
The tests create fake cluster specs with Ceph image, resources, priority classes, health-check probe overrides, network settings, and volume claim templates. They then inspect generated objects in memory. PVC tests verify default storage request injection and preservation of explicit storage limits or requests. Probe tests verify cluster-provided startup/liveness probe fields override generated defaults. Msgr2 tests mutate `monConfig.Port` and `c.spec.Network` across default, dual-stack, IPv4, and IPv6 scenarios.

## Dependencies And Integration Points
The tests depend on Rook fake clientsets, Ceph client test owner refs, operator test helpers for label/pod-template assertions, Kubernetes resource quantities, and Ceph API spec structures. They integrate normal monitor spec generation with shared Rook daemon volume/env/probe helpers.

## Risks And Test Signals
The strongest signals are around stable labels, resources, service account, priority class, probe overrides, and network-specific bind address formatting. The test explicitly catches IPv6 bracket requirements and dual-stack avoidance of forced port binding. It also confirms `ROOK_CEPH_MON_RUN_AS_ROOT=true` changes the pod security context to `RunAsUser: 0`. Runtime behavior of the generated containers is not tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/template/floating-mon-drbd-deployment.yaml -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/template/floating-mon-drbd-deployment.yaml

## Purpose
This embedded YAML template defines a DRBD-backed floating monitor Deployment. It is rendered by `spec.go` when `spec.Mon.FloatingMon` selects a monitor that should move with a DRBD device rather than use the standard monitor pod construction path.

## Important APIs, Types, And Functions
The template produces an `apps/v1` Deployment named `rook-ceph-mon-{{ .NAME }}` with labels identifying `app: rook-ceph-floating-mon`, monitor daemon IDs, cluster namespace, Ceph/Rook versions, and operator namespace. Parameters include monitor identity, namespace, cluster name, versions, FSID, Ceph image, image pull policy, public IP, priority class, host path directories, DRBD config/device/resource values, container data dir, and `ROOK_MSGR2`.

## Control Flow And State
The pod is a single-replica recreate Deployment with hostPath volumes for Rook config, mon keyring, socket, logs, crash dir, monitor data, `/dev`, DRBD config/dir, and host root. Init flow first runs a privileged DRBD utility container to set hostname and promote the DRBD resource primary. A privileged chown container mounts the DRBD device, chowns Ceph paths, and traps exit for cleanup. A privileged `init-mon-fs` container mounts the device and runs `ceph-mon --mkfs`. The main `mon` container mounts the device and runs `ceph-mon --foreground` with public address, bind address, keyring, mon host, initial members, and probes. Sidecars include a log collector and a floating-mon shutdown container whose preStop hook attempts unmount and DRBD demotion.

## Dependencies And Integration Points
The template depends on DRBD utilities, privileged containers, hostPath access, Rook/Ceph secrets, Rook config override ConfigMap, Ceph monitor env vars from `rook-ceph-config`, and mounted host directories. It integrates with `makeFloatingMonDeployment()` and receives resource requirements after YAML decoding.

## Risks And Test Signals
This is a high-risk operational template because it changes hostnames inside containers, mounts/demotes DRBD devices, uses privileged security contexts, and relies on shell lifecycle cleanup. Missing DRBD parameters or incorrect host paths can render an invalid or dangerous workload. `mon_test.go` verifies rendering, resource patching, annotations/labels, update behavior, and missing ConfigMap failures, but it does not execute the DRBD lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/template/floating-mon-drbd-deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/util.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/util.go

## Purpose
This file contains small monitor utility functions for quorum lookup, monitor ID parsing, and service port construction.

## Important APIs, Types, And Functions
`monInQuorum(monitor, quorum)` checks whether a monitor map entry's rank appears in a quorum rank slice. `getMonByID(monID, monMap)` returns the monitor map entry and in-quorum flag for a named monitor. `fullNameToIndex(name)` converts monitor names such as `rook-ceph-mon-a` or `b` into numeric indices using `k8sutil.NameToIndex()`. `addServicePort(service, name, port)` appends a TCP service port unless the port is zero.

## Control Flow And State
All functions are pure or local-object mutators. `getMonByID` scans the Ceph monitor status response and uses `slices.Contains` on quorum ranks. `fullNameToIndex` trims the monitor app prefix and separator before converting. `addServicePort` mutates only the passed `Service` object before it is submitted to Kubernetes.

## Dependencies And Integration Points
The utilities depend on Ceph client monitor status structures, Kubernetes Service types, Rook name conversion, and `intstr` target ports. They are used by monitor health/quorum code and service creation.

## Risks And Test Signals
The main risk is monitor name parsing: legacy numeric resource names are intentionally invalid for the new alphabetic index conversion path. `mon_test.go` covers `monInQuorum` and `fullNameToIndex`. Service port behavior is indirectly exercised through service and monitor startup paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring.go

## Purpose
This file manages long-running Ceph cluster health monitoring goroutines for monitors, OSDs, and cluster status. It enables or cancels daemon-specific health checks based on the `CephCluster` health-check spec.

## Important APIs, Types, And Functions
`monitorDaemonList` contains `mon`, `osd`, and `status`. `(c *ClusterController) configureCephMonitoring(cluster, clusterInfo)` reconciles enabled monitoring routines. `isMonitoringEnabled(daemon, clusterSpec)` reads daemon-specific disabled flags. `(c *ClusterController) startMonitoringCheck(cluster, clusterInfo, daemon)` starts the appropriate health checker.

## Control Flow And State
`configureCephMonitoring` loops over the daemon list, computes whether each routine should be enabled, checks `cluster.monitoringRoutines` for existing `opcontroller.ClusterHealth`, and cancels running routines when now disabled. If no routine exists and monitoring is enabled, it creates a cancellable child context from the operator manager context, stores it, and starts the appropriate goroutine. Floating monitor clusters skip mon health checks because the monitor ID is not available in this path. OSD checks are skipped for external clusters.

## Dependencies And Integration Points
The code depends on cluster-local `sync.Map`-style monitoring routine storage, Rook `ClusterHealth` contexts, monitor health checker, OSD health monitor, Ceph status checker, and CephCluster health-check spec fields. It integrates with cluster reconciliation and operator manager lifecycle cancellation.

## Risks And Test Signals
Risks include leaking goroutines if cancellation state is not maintained, failing to restart a canceled routine because the entry remains in the map, and skipping mon monitoring for floating monitors. `monitoring_test.go` only covers `isMonitoringEnabled` for monitor enabled/disabled cases, so most goroutine lifecycle behavior is not unit-tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring_test.go

## Purpose
This small test file verifies health monitoring enablement logic for Ceph monitors.

## Important APIs, Types, And Functions
`TestIsMonitoringEnabled` table-drives `isMonitoringEnabled(daemon, clusterSpec)` for daemon `mon`. It checks the default enabled state and the disabled state when `HealthCheck.DaemonHealth.Monitor.Disabled` is true.

## Control Flow And State
The test constructs in-memory `ClusterSpec` values only. It does not start monitoring goroutines, create contexts, or interact with Kubernetes.

## Dependencies And Integration Points
It depends on the Ceph API `ClusterSpec` and health-check spec types. It provides a narrow regression check for `monitoring.go`.

## Risks And Test Signals
The test confirms the default monitor health checker is enabled and that the monitor disabled flag is respected. OSD/status enablement and lifecycle behavior in `configureCephMonitoring` remain uncovered by this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/monitoring_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add.go

## Purpose
This file registers the node daemon controller. The controller watches nodes, Ceph pods, and crash collector deployments so it can reconcile node-scoped crash collector and ceph-exporter daemons.

## Important APIs, Types, And Functions
Constants define `controllerName`, `CrashCollectorAppName`, `cephExporterAppName`, `prunerName`, and `NodeNameLabel`. `Add()` constructs and registers the controller. `newReconciler()` creates a `ReconcileNode`. `add()` creates the controller-runtime controller and installs watches. `isCephPod(labels, podName)` filters Ceph workload pods.

## Control Flow And State
The controller watches node spec updates only when `Node.Spec` changes. It watches crash collector Deployments and maps them back to the node named in the pod template's `node_name` label. It watches pods and enqueues the hosting node when a Ceph pod moves nodes; the update predicate only allows node-name changes. `isCephPod` requires `rook_cluster` and excludes canary, crashcollector, and exporter pods to avoid reconciling node daemons from temporary or self-owned pods.

## Dependencies And Integration Points
The file depends on controller-runtime controller, source, handler, predicate, Kubernetes Node/Pod/Deployment APIs, Rook cluster context, and operator config. It integrates with `ReconcileNode` in `reconcile.go`.

## Risks And Test Signals
Risk centers on event filtering. If `isCephPod` is too broad, daemon pods can trigger loops; if too narrow, node daemon creation/deletion may lag. `add_test.go` covers canary exclusion and positive/negative `rook_cluster` label behavior. Crashcollector/exporter exclusion is implemented but not directly covered in the shown tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add_test.go

## Purpose
This file tests the pod classification helper used by the node daemon controller watches.

## Important APIs, Types, And Functions
`TestIsCephPod` calls `isCephPod(labels, podName)`. It checks a pod without `rook_cluster`, a monitor canary pod with `rook_cluster`, and a normal Ceph monitor pod with `rook_cluster`.

## Control Flow And State
The test mutates a label map and pod name strings in memory. No controller, manager, or Kubernetes fake client is involved.

## Dependencies And Integration Points
It depends only on package-local node daemon code and testify assertions. It validates the watch filter used before enqueueing node reconcile requests from pod events.

## Risks And Test Signals
The test confirms canary pods are intentionally ignored so crash collectors are not started before real monitors establish `ROOK_CEPH_MON_HOST`. It does not cover the explicit crashcollector/exporter self-exclusion branches or the node/deployment watch mappings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash.go

## Purpose
This file builds per-node Ceph crash collector Deployments. Crash collectors run `ceph-crash` on nodes hosting Ceph pods so crashes are posted to the Ceph cluster.

## Important APIs, Types, And Functions
Constants define crash collector cephx identity and secret names. `(r *ReconcileNode) createOrUpdateCephCrash(node, tolerations, cephCluster, cephVersion)` creates or updates a node-specific Deployment. `getCrashDirInitContainer()`, `getCrashChownInitContainer()`, `getCrashDaemonContainer()`, and `generateCrashEnvVar()` build the pod pieces.

## Control Flow And State
`createOrUpdateCephCrash` requires the Kubernetes hostname label on the node, constructs a truncated deployment name, sets controller ownership, builds base volumes and crash keyring volume, and calls `controllerutil.CreateOrUpdate`. The mutate function sets stable selector labels only on create, applies deployment labels, Ceph version and Rook version labels, and builds a pod bound to the target hostname through `NodeSelector`. The pod has crash directory and chown init containers, one `ceph-crash` container, inherited tolerations, optional host networking, priority class, empty pod security context, default service account, and crash collector annotations.

## Dependencies And Integration Points
The file depends on CephCluster API fields, Rook controller volume/env/security helpers, keyring volume helpers, Kubernetes Deployments, node labels, owner refs, and Ceph version labels. It integrates with `ReconcileNode.createOrUpdateNodeDaemons()` and the crash collector secret created in `keyring.go`.

## Risks And Test Signals
The hostname label is mandatory; missing it prevents deployment. Selector immutability is handled by setting selectors only for new objects. The crash container runs as the Ceph user because the script has no user flag. `crash_test.go` covers env var generation, create/update behavior, labels, tolerations, host network, priority class, Rook version label placement, and security context user/group.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash_test.go

## Purpose
This file tests crash collector Deployment generation for node daemons.

## Important APIs, Types, And Functions
`TestGenerateCrashEnvVar` validates `CEPH_ARGS` for `ceph-crash`. `TestCreateOrUpdateCephCrash` constructs a fake `ReconcileNode`, fake scheme/client, a node with hostname label, tolerations, a CephCluster, and a Ceph version, then calls `createOrUpdateCephCrash()`.

## Control Flow And State
The test first creates a crash collector Deployment and verifies operation result `created`, node selector, tolerations, host network false, no priority class, and Ceph user security context. It then mutates cluster labels, host network, priority class, and tolerations, calls the function again, and verifies operation result `updated` plus changed pod labels, host network, priority class, and Rook version label placement on the Deployment but not the pod template.

## Dependencies And Integration Points
The test depends on controller-runtime fake client, Rook fake clientsets, the Rook scheme, Kubernetes Deployment/Node types, and Ceph API priority/label specs. It validates the object mutation path used during node reconciliation.

## Risks And Test Signals
The test catches regressions in selector/label construction, host-network propagation, toleration propagation, and security context expectations. It does not test missing hostname label or actual `ceph-crash` execution.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter.go

## Purpose
This file builds and manages per-node `ceph-exporter` Deployments plus the metrics Service and ServiceMonitor used for Prometheus scraping.

## Important APIs, Types, And Functions
Constants define socket directory, default exporter args, default metrics port `9926`, service port name, and cephx identity/secret names. `(r *ReconcileNode) createOrUpdateCephExporter()` creates/updates node-specific exporter Deployments. Helpers include `getCephExporterChownInitContainer()`, `getExporterMetricsPort()`, `getCephExporterDaemonContainer()`, `MakeCephExporterMetricsService()`, `EnableCephExporterServiceMonitor()`, `applyCephExporterLabels()`, `deleteOrphanedExporterDeployments()`, `applyPrometheusAnnotations()`, `generateExporterEnvVar()`, and `exporterIsHost()`.

## Control Flow And State
Exporter reconciliation short-circuits when `Monitoring.MetricsDisabled` is true. Otherwise it requires the node hostname label, builds an owned Deployment, and creates or updates it. The pod uses recreate strategy, hostname node selector, chown init container, exporter container, keyring volume, default service account, optional log collector, optional host networking with corresponding DNS policy, short termination grace period, annotations, and scrape annotations unless custom exporter annotations are supplied. Container args include socket dir, metrics port, perf counter priority limit, stats period, and `--addrs ::` for dual-stack or IPv6.

`MakeCephExporterMetricsService` creates a ClusterIP Service selecting exporter app labels. `EnableCephExporterServiceMonitor` creates/updates a ServiceMonitor, applies monitoring/exporter labels, interval, selector, owner reference, and optional relabel config for `rook.io/managedBy`. `deleteOrphanedExporterDeployments` lists exporter Deployments and removes those whose `node_name` label points to a deleted node.

## Dependencies And Integration Points
The file depends on Kubernetes Deployments/Services, controller-runtime clients, Prometheus Operator ServiceMonitor APIs, Rook controller helpers, CephCluster monitoring spec, keyring volumes, Ceph version labels, and Rook logging. It integrates with node reconciliation, monitoring enablement, and Prometheus discovery.

## Risks And Test Signals
Risks include stale exporter Deployments after node deletion, port/ServiceMonitor mismatches, host-network override ambiguity, IPv6 bind behavior, selector immutability, and duplicate socket use during rolling updates. Recreate strategy and orphan cleanup address two of these. `exporter_test.go` covers create/update behavior, custom exporter args and port, log collector sidecar, IPv6 `--addrs`, metrics Service, ServiceMonitor relabel labels, and orphan deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter_test.go

## Purpose
This file tests ceph-exporter Deployment, container, Service, ServiceMonitor label, host-network, IPv6, and orphan cleanup behavior.

## Important APIs, Types, And Functions
Helpers `assertCephExporterArgs()` and `assertCephExporterArgsWithPort()` validate exporter argument order and optional IPv6 args. Tests exercise `createOrUpdateCephExporter()`, `getCephExporterDaemonContainer()`, `MakeCephExporterMetricsService()`, `applyCephExporterLabels()`, and `deleteOrphanedExporterDeployments()`.

## Control Flow And State
`TestCreateOrUpdateCephExporter` creates then updates a node-specific Deployment, verifying node selector, labels, tolerations, host network, DNS policy, service account, priority class, default args, custom perf/stats args, and custom port. `TestCephExporterLogrotateContainer` enables log collection and verifies the log collector sidecar. `TestCephExporterBindAddress` runs many network/hostNetwork combinations and verifies IPv6/dual-stack adds `--addrs ::` independently of host-network choice. `TestServiceSpec` verifies metrics Service name, port, labels, selector, and custom port. `TestApplyCephExporterLabels` verifies ServiceMonitor relabel config only when `rook.io/managedBy` is present in exporter labels. `TestDeleteOrphanedExporterDeployments` verifies no-op, preserve live-node deployments, delete missing-node deployments, skip missing `node_name`, and mixed cases.

## Dependencies And Integration Points
The tests use controller-runtime fake clients, Prometheus Operator API types, Rook fake clientsets, Kubernetes core/apps types, and Rook schemes. They validate exporter integration with Kubernetes object generation and Prometheus scrape configuration.

## Risks And Test Signals
The tests strongly cover object spec regressions and stale deployment cleanup. They do not run an actual exporter or ServiceMonitor controller. There is a minor noise signal in `TestApplyCephExporterLabels` where `fmt.Printf("Hello1")` appears to be leftover debug output.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/exporter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring.go

## Purpose
This file creates and rotates CephX keyrings and Kubernetes Secrets for node daemons: crash collector and ceph-exporter.

## Important APIs, Types, And Functions
Constants define clients and keyring templates for `client.crash` and `client.ceph-exporter`. Public functions are `CreateCrashCollectorSecret()` and `CreateExporterSecret()`. Internal helpers include `cephCrashCollectorKeyringCaps()`, `createCrashCollectorKeyring()`, `updateCrashCollectorCephxStatus()`, `createOrUpdateCrashCollectorSecret()`, `createExporterKeyringCaps()`, `createExporterKeyring()`, `updateCephExporterCephxStatus()`, and `createOrUpdateExporterSecret()`.

## Control Flow And State
Secret creation obtains a `keyring.SecretStore`, generates or gets a Ceph key with daemon-specific caps, checks the owning `CephCluster` for key rotation requirements, optionally rotates the CephX key, updates `cluster.Status.Cephx.CrashCollector` or `CephExporter` via retry-on-conflict and `reporting.UpdateStatus`, formats a keyring file, sets owner refs on a Kubernetes Secret, and creates/updates it through the secret store. Crash collector caps allow monitor crash profile and manager read/write. Exporter caps allow monitor exporter profile plus read access to mgr/osd/mds.

## Dependencies And Integration Points
The file depends on Ceph command execution behind `keyring.SecretStore`, CephCluster status, Rook key rotation policy helpers, owner refs, Kubernetes Secrets, status reporting, and retry-on-conflict. It feeds the volumes mounted by `crash.go`, `exporter.go`, and `pruner.go`.

## Risks And Test Signals
Risks include overbroad caps, stale Kubernetes Secret data after rotation, status update conflicts, and version/policy mismatches. The TODO notes rotation during Ceph version updates should distinguish running and desired versions. `keyring_test.go` covers caps and key rotation/status update for both crash collector and exporter using mocked Ceph command output.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring_test.go

## Purpose
This file tests node-daemon CephX caps, key generation, rotation, and CephCluster status updates for crash collector and ceph-exporter.

## Important APIs, Types, And Functions
`TestCephCrashCollectorKeyringCaps` and `TestExporterKeyringCaps` validate exact cap slices. `TestCreateCrashCollectorKeyring` exercises `createCrashCollectorKeyring()`. `TestCreateCephExporterKeyring` exercises `createExporterKeyring()`.

## Control Flow And State
Both keyring tests construct a fake CephCluster with key-generation policy, uninitialized cephx status, fake controller-runtime client, and mock executor. The mock returns a static key for `auth get-or-create-key` and a rotated key for `auth rotate`. The tests first verify initial key generation, then update cluster spec key generation, raise Ceph version to a rotation-supporting version, call the keyring function again, and verify the rotated key plus status generation update.

## Dependencies And Integration Points
The tests depend on Rook keyring helpers, fake controller-runtime clients, Ceph version constants, mock executors, CephCluster API types, and cluster info owner refs. They validate the integration between Ceph auth commands and Kubernetes CR status.

## Risks And Test Signals
The tests prove both daemon identities rotate independently and update the correct `Status.Cephx` field. They do not validate final Kubernetes Secret creation, owner refs, or retry conflict behavior in the status update path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner.go

## Purpose
This file reconciles a CronJob that periodically prunes old Ceph crash reports using the crash collector keyring.

## Important APIs, Types, And Functions
`reconcileCrashPruner(namespace, cephCluster, tolerations)` decides whether to create/update or delete the pruner. `createOrUpdateCephCron(cephCluster, tolerations)` builds the CronJob. `getCrashPruneContainer(cephCluster)` builds the `ceph crash prune` container. The schedule is `0 0 * * *`.

## Control Flow And State
If crash collection is disabled, reconciliation skips pruning. If `DaysToRetain` is zero, it deletes the CronJob if present and ignores not-found. Otherwise it creates or updates an owned CronJob with label `app: rook-ceph-crashcollector-pruner`, cluster label, pod template using crash keyring volumes, inherited tolerations, optional host networking, default service account, and a single container running `ceph -n client.crash crash prune <days>`. The CronJob has `StartingDeadlineSeconds` of 60 to avoid accumulated missed runs counting indefinitely.

## Dependencies And Integration Points
The file depends on Kubernetes batch/v1 CronJobs, Rook controller volume/env helpers, crash collector keyring volumes, CephCluster crash collector spec, owner refs, and controller-runtime `CreateOrUpdate`. It integrates with node reconciliation after node daemon create/delete handling.

## Risks And Test Signals
Risks include stale CronJobs when retention is disabled, missing keyring secret, and prune jobs with incorrect tolerations or host networking. `pruner_test.go` covers CronJob creation and toleration propagation. Deletion and disabled paths are not covered in the shown tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner_test.go

## Purpose
This file tests crash pruner CronJob creation.

## Important APIs, Types, And Functions
`TestCreateOrUpdateCephCron` calls `r.createOrUpdateCephCron(cephCluster, tolerations)` and then fetches the `rook-ceph-crashcollector-pruner` CronJob from a fake controller-runtime client.

## Control Flow And State
The test creates a CephCluster with placement tolerations, a fake scheme/client with batch/v1 registered, and a `ReconcileNode`. It verifies the operation result is `created` and that the CronJob pod template carries the expected tolerations.

## Dependencies And Integration Points
The test depends on Kubernetes batch/v1 CronJob types, Rook fake clients, controller-runtime fake client, and node-daemon pruner code. It validates the object creation path, not the higher-level `reconcileCrashPruner()` decision logic.

## Risks And Test Signals
The test covers a narrow but important scheduling property: prune jobs inherit tolerations. It does not assert schedule, command args, owner refs, keyring volumes, delete-on-zero-retention behavior, or crash collector disabled behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/reconcile.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/reconcile.go

## Purpose
This file implements the node daemon reconciler. It ensures crash collector and ceph-exporter daemons exist only on nodes that currently host Ceph pods, removes them from nodes without Ceph pods, manages disabled states, performs one-time orphan exporter cleanup, and reconciles the crash pruner.

## Important APIs, Types, And Functions
`ReconcileNode` stores scheme, controller-runtime client, Rook cluster context, operator manager context, and operator config. `Reconcile()` wraps `reconcile()` with panic recovery/logging. `reconcile(request)` is the main control loop. Supporting methods include `createOrUpdateNodeDaemons()`, `removeDisabledCrashCollectorDaemons()`, `removeDisabledCephExporterDaemons()`, `listDeploymentAndDelete()`, `deleteNodeDaemon()`, `cephPodList()`, `listNodeDaemonsAndDelete()`, and `deleteDeployment()`. Global state includes `waitForRequeueIfSecretNotCreated` and `exporterOrphanCheckDone`.

## Control Flow And State
Reconciliation fetches the requested node and ignores not-found nodes. It lists all Ceph pods by app labels for mon, mgr, osd, object, mds, rbd, and mirror, groups them by namespace, and for each namespace fetches the first CephCluster. If crash collector/exporter are disabled, it deletes their deployments and may skip the namespace if both are disabled. It requires the crash collector keyring secret before creating any node daemons, requeueing for 30 seconds if missing. It determines Ceph version from the cluster image, collects unique tolerations from Ceph pods on the target node, runs one-time exporter orphan cleanup per namespace, and either creates/updates node daemons when the node hosts Ceph pods or deletes node daemons from that node when it does not. Finally it reconciles the crash pruner.

## Dependencies And Integration Points
The reconciler depends on controller-runtime client/list/delete operations, Kubernetes Node/Pod/Deployment/Secret APIs, CephCluster CRs, app label conventions across Ceph daemon packages, Ceph version detection, disruption toleration set utilities, crash/exporter/pruner builders, and service/service monitor helpers. It is the integration point tying node and pod watch events to daemon resources.

## Risks And Test Signals
Risks include selecting the first CephCluster when multiple exist in a namespace, global `exporterOrphanCheckDone` lifecycle across tests/operator lifetime, requeue blocking all node daemons on missing crash secret, partial API list failures, and best-effort deletion only logging errors in cleanup paths. This file has no direct test file in the listed set; behavior is covered indirectly by tests for add filters, crash/exporter/pruner object builders, and orphan exporter cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/reconcile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config.go

## Purpose
This file provides OSD configuration helpers for networking and encryption device naming/key generation.

## Important APIs, Types, And Functions
`osdOnSDNFlag(network)` returns Ceph daemon args needed when OSDs run on pod networking. `encryptionKeyPath()` returns the path to the LUKS key under `/etc/ceph`. `EncryptionDMName(pvcName, blockType)` and `EncryptionDMPath(pvcName, blockType)` derive dm-crypt mapper names and paths. `encryptionBlockDestinationCopy(mountPath, blockType)` builds temporary copy paths for block files. `GenerateDmCryptKey()` returns a base64-encoded 128-byte random key.

## Control Flow And State
The file is mostly pure helpers. `osdOnSDNFlag` appends `--ms-learn-addr-from-peer=false` when the network is not host networking, avoiding incorrect peer-learned bind addresses on SDN. `GenerateDmCryptKey` calls `mgr.GenerateRandomBytes` and base64 encodes the result. No Kubernetes or Ceph persistent state is modified here.

## Dependencies And Integration Points
The code depends on CephCluster network specs, OSD config constants such as encryption key filename and block names from nearby package files, operator config paths, and manager random byte generation. It integrates with OSD prepare/activate paths that need consistent encrypted device and key file naming.

## Risks And Test Signals
Risks are mostly compatibility: changing mapper name/path formats would break existing encrypted OSD activation, and network flag behavior affects OSD connectivity on SDN. `config_test.go` covers SDN flag selection, encryption key path, temporary block copy paths, and dm-crypt name/path formatting. Random key length/encoding is not covered in the listed tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/config.go

## Purpose
This package file defines structured OSD store configuration parsed from string maps, plus JSON-facing types for configured devices.

## Important APIs, Types, And Functions
Constants define keys such as `walSizeMB`, `databaseSizeMB`, `osdsPerDevice`, `encryptedDevice`, `metadataDevice`, `deviceClass`, `initialWeight`, and `primaryAffinity`. `StoreConfig` holds WAL/database sizes, OSDs per device, encryption flag, metadata device, device class, initial weight, primary affinity, and store type. `IsValidStoreType()` accepts BlueStore and BlueStoreRDR. `GetStoreFlag()` returns `--<storeType>`. `NewStoreConfig()` defaults `OSDsPerDevice` to 1. `ToStoreConfig(config)` parses a string map into a `StoreConfig`. `MetadataDevice(config)` extracts just the metadata device. `ConfiguredDevice` pairs a device ID with a store config.

## Control Flow And State
`ToStoreConfig` iterates over arbitrary map order and switches on known keys. Integer parsing ignores invalid values by returning zero; `OSDsPerDevice` only updates when the parsed value is positive, preserving the default of 1 for absent, invalid, or nonpositive values. Encryption is true only for exact string `"true"`. Unknown keys are ignored. No persistent state is changed; the struct is passed onward to OSD provisioning logic.

## Dependencies And Integration Points
The file depends on Ceph API store type constants and Go JSON tags. It integrates with OSD discovery/provisioning code that accepts device configuration from CRD fields or device maps.

## Risks And Test Signals
The lenient parsing model avoids hard failures but can silently turn invalid numeric values into zero or ignore typos. Store type validation is narrow and must stay aligned with supported Ceph/Rook store types. No direct test file for this subpackage is listed in the work item; coverage may exist elsewhere. The adjacent `osd/config_test.go` does not exercise this package.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/scheme.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/scheme.go

## Purpose
This file defines a single OSD config default constant.

## Important APIs, Types, And Functions
`WalDefaultSizeMB` is set to `576` and documented as the default WAL size in megabytes for RocksDB in BlueStore.

## Control Flow And State
There is no control flow and no state mutation. The constant is imported by OSD provisioning/configuration code that needs a default WAL size.

## Dependencies And Integration Points
The file has no imports. Its integration point is compile-time use by the OSD config package and consumers that need the BlueStore WAL default.

## Risks And Test Signals
The only risk is semantic drift if Ceph/Rook default WAL sizing changes but this constant is not updated. No direct tests in the listed set assert this constant.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config/scheme.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config_test.go

## Purpose
This test file validates selected OSD helper functions for network flags and encryption path/name generation.

## Important APIs, Types, And Functions
`TestOsdOnSDNFlag` exercises `osdOnSDNFlag()`. `TestEncryptionKeyPath`, `TestEncryptionBlockDestinationCopy`, `TestEncryptionDMPath`, and `TestEncryptionDMName` exercise encryption helper functions from `config.go`.

## Control Flow And State
The tests create small in-memory values: a `NetworkSpec`, a mount path string, PVC name, and block type constants. They assert exact returned strings and whether SDN args are present.

## Dependencies And Integration Points
The tests depend on Ceph API network spec and OSD package constants. They are pure unit tests with no Kubernetes or Ceph command execution.

## Risks And Test Signals
The tests pin compatibility-sensitive strings such as `/etc/ceph/luks_key`, `/dev/mapper/<pvc>-block-dmcrypt`, and `block.db-tmp`. They also confirm host networking suppresses the SDN peer-learning flag. `GenerateDmCryptKey()` is not covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/osd/config_test.go -->
