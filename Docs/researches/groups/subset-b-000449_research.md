# subset-b-000449 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr_test.go

## Purpose

This file is the main unit test suite for Rook's Ceph manager cluster controller. It exercises manager startup, deployment/service reconciliation, active/standby role labeling, module configuration, Prometheus module behavior, monitoring labels, daemon ID generation, and manager cephx key rotation status.

## Important APIs and Test Flow

`createNewCluster()` builds a fake `mgr.Cluster` with a mock Ceph executor, fake Kubernetes clientsets, a controller-runtime fake client containing a `CephCluster`, and a temporary config directory. The executor returns canned responses for `mgr stat`, `auth get-or-create-key`, `auth rotate`, and `versions`, while `waitForDeploymentToStart` is stubbed so tests focus on object reconciliation.

`TestStartMgr` calls `Start()` through several spec variants and validates expected deployments and services. `validateStart()` checks deployment annotations, labels, priority class, sidecar presence when `Mgr.Count > 1`, and absence of extra manager deployments. `validateServices()` verifies the metrics service and conditional dashboard service, including custom dashboard port handling.

`TestActiveMgrLabels` creates fake manager pods and verifies `SetMgrRoleLabel()` toggles `mgr_role` between `active` and `standby`. `TestUpdateServiceSelectors` verifies legacy selectors lose `ceph_daemon_id` and gain active-manager selection. `TestConfigureModules` covers generic mgr module enable/disable. `TestCluster_configurePrometheusModule` covers metrics-disabled behavior, metrics port changes, scrape interval comparison, and the disable-enable sequence needed for config changes. `TestMgrKeyRotation` validates key-generation status updates when the CephCluster daemon key-rotation policy advances.

## State, Dependencies, and Integration

The tests model state across Kubernetes Deployments, Services, Pods, fake `CephCluster.Status.Cephx.Mgr`, and command-output counters. They depend on Rook's fake operator clients, the Prometheus Operator API type for `ServiceMonitor`, Kubernetes policy/app/core APIs, and Ceph client command wrappers.

## Risks and Test Signals

The strongest signals are around upgrade-sensitive selectors and key generation. Risks include global test hooks (`updateDeploymentAndWait`, `waitForDeploymentToStart`) leaking if not reset, map-order-insensitive endpoint/service assertions, and mocked Ceph commands that may not catch argument changes outside the tested branches.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator.go

## Purpose

This file configures Ceph's manager orchestrator integration so Rook can be selected as the Ceph orchestrator backend. It is a small bridge between Rook manager reconciliation and Ceph's `mgr/orchestrator` command surface.

## Important APIs and Control Flow

`configureOrchestratorModules()` first enables the Ceph manager module named `rook` with `client.MgrEnableModule(..., force=true)`. It then calls `setRookOrchestratorBackend()`.

`setRookOrchestratorBackend()` executes `ceph orch set backend rook` through `client.NewCephCommand(...).RunWithTimeout(exec.CephCommandsTimeout)` inside `client.ExecuteCephCommandWithRetry`. The retry count is five and the wait interval is `orchestratorInitWaitTime`, defaulting to five seconds. This exists because enabling a mgr module does not mean the module is immediately ready to accept orchestrator commands.

## State and Persistence

No Kubernetes object is persisted by this file. The durable state is inside Ceph's mgr module configuration: the rook module is enabled and the orchestrator backend is set to `rook`. Failures are wrapped with context so upper reconciliation can report whether module enablement or backend selection failed.

## Dependencies and Integration Points

The code depends on `pkg/daemon/ceph/client` for mgr module and Ceph command execution, `pkg/util/exec` for command timeout, and the `Cluster`'s `context`/`clusterInfo`. It integrates with manager startup after the manager daemon is available.

## Risks and Test Signals

The main risk is timing: a newly enabled mgr module may reject orchestrator commands until initialized. The retry wrapper mitigates that. Another risk is that Ceph command semantics or module names change. `orchestrator_test.go` explicitly exercises retry behavior and error wrapping around simulated command failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator_test.go

## Purpose

This file tests Rook's Ceph manager orchestrator-module setup, especially the retry path for selecting the `rook` orchestrator backend after enabling the manager module.

## Important APIs and Test Flow

`TestOrchestratorModules` installs a mock executor with two command paths. `MockExecuteCommandWithOutput` recognizes `ceph mgr module enable rook` and records that the rook module was enabled. `MockExecuteCommandWithTimeout` recognizes `ceph orch set backend rook`, fails the first five calls, then succeeds.

The test creates a minimal `Cluster` with `ClusterInfo`, `clusterd.Context`, a Squid Ceph version, and an overridden `exitCode` hook. It sets `orchestratorInitWaitTime = 0` to avoid real sleeps. The first call to `configureOrchestratorModules()` is expected to fail because the retry budget is exhausted. A direct call to `setRookOrchestratorBackend()` then succeeds once the mock's error counter has reached the success threshold. Later calls verify the success path remains clean once the backend command no longer fails.

## State, Dependencies, and Integration

State is entirely in local booleans and the `backendErrorCount` counter. The test depends on Rook's `exectest.MockExecutor`, Ceph client command wrappers, and the global `exec.CephCommandsTimeout`.

## Risks and Test Signals

The test is a good signal for backend command retry semantics and exact Ceph CLI arguments. It also has global-state risk: it modifies `orchestratorInitWaitTime` and `exec.CephCommandsTimeout` without restoring them. Changes to retry count, command construction, or module setup order will be caught by the command assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/orchestrator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec.go

## Purpose

This file builds Kubernetes Deployments, containers, labels, annotations, and Services for Ceph manager daemons. It encodes how the mgr daemon, active-manager sidecar, Multus command-proxy sidecar, metrics service, and dashboard service should look from a `CephCluster` spec.

## Important APIs and Control Flow

`makeDeployment()` constructs the mgr Deployment and pod template. It starts with daemon volumes and a chown init container, adds the main `ceph-mgr` container, applies placement, tolerations, priority class, annotations, labels, owner references, and Ceph/Rook version labels. When `Mgr.Count > 1`, it adds the `watch-active` sidecar, config/secret volumes, and anti-affinity across hostnames or required zones. When log collection is enabled it adds the log collector and shares the process namespace. Host networking sets DNS policy; Multus applies network annotations, mounts the admin keyring, and adds a command-proxy sidecar.

`makeMgrDaemonContainer()` configures the `ceph-mgr` command, daemon flags, `client-mount-uid/gid`, foreground mode, ports for daemon traffic, metrics, and dashboard, standard daemon env vars, orchestrator-module env vars, resources, security context, and probes. Non-host-network pods advertise `ROOK_POD_IP` as public address.

`makeMgrSidecarContainer()` builds the Rook `ceph mgr watch-active` sidecar that can update active/standby labels and carries cluster, namespace, dashboard, monitoring, endpoint, and Ceph version env vars. `makeCmdProxySidecarContainer()` supports Multus command execution through admin keyring and `CEPH_ARGS`.

`MakeMetricsService()` and `makeDashboardService()` build ClusterIP services. Metrics selectors target `mgr_role=active`, except the external manager service intentionally has no selector. Dashboard service names and ports reflect SSL and dashboard spec settings.

## State, Persistence, and Dependencies

This file does not write objects directly; callers create or update the generated Deployment/Service objects. Persistent state is encoded as Kubernetes metadata and pod template spec. Dependencies include Rook controller helpers for daemon volumes, probes, resources, labels, Multus, keyrings, and owner references, plus Kubernetes apps/core API types.

## Risks and Test Signals

Selector changes can route metrics/dashboard traffic incorrectly, so `buildSelectorLabels()` and active labels are high-risk. Network transitions are also sensitive: host networking changes public address behavior, while Multus requires extra keyring volume and command proxy. `spec_test.go` covers pod shape, Multus, probes, services, host networking, annotations, and manager-specific host-network override behavior; `mgr_test.go` covers service selector migration and active labels.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec_test.go

## Purpose

This file tests Kubernetes object generation for Ceph manager deployments and services. It focuses on pod spec correctness, resource propagation, Multus sidecars, probe overrides, service selectors, host-network behavior, Prometheus annotations, and manager-specific host-network overrides.

## Important APIs and Test Flow

`TestPodSpec` builds a manager cluster with a Ceph image, dashboard port, priority class, data dir, and resource requests/limits. The traditional deployment subtest validates Ceph labels, expected env vars, the shared pod-template tester's full suite, annotation count, container count, and volume mounts. The Multus subtest sets `Network.Provider = "multus"` and expects an extra annotation, an extra command-proxy container, admin-keyring mount, and `CEPH_ARGS` pointing at the admin keyring. The probe subtest configures mgr startup and liveness probes and confirms generated container probes use the custom initial delays.

`TestServiceSpec` validates `MakeMetricsService()` output: name, single metrics port, labels, and selectors for `app=rook-ceph-mgr`, `mgr_role=active`, and `rook_cluster`. `TestHostNetwork` confirms cluster-level host networking sets `DNSClusterFirstWithHostNet`. `TestApplyPrometheusAnnotations` verifies default scrape annotations are applied only when no mgr-specific annotations are configured. `TestMgrNetwork` covers the precedence of `spec.Mgr.HostNetwork` over cluster network settings when explicitly set.

## State, Dependencies, and Integration

The tests use fake Kubernetes clients, minimum owner references, Rook's pod-template test helpers, and resource quantity assertions. The state under test is generated in-memory Kubernetes object specs, not persisted API server state.

## Risks and Test Signals

These tests are strong signals for object drift that could affect scheduling, monitoring, or networking. They intentionally assert exact counts for annotations, containers, mounts, selectors, and probes. A risk is that exact counts can be brittle when legitimate shared volumes or annotations are added, but that brittleness is useful for catching unintended pod-shape changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/config.go

## Purpose

This file contains monitor configuration helpers shared by mon orchestration and other daemons. It builds the shared mon keyring, derives monitor host data paths, writes client connection config, and exposes the secret volume/mount used by sidecars that need the Ceph admin secret.

## Important APIs and Behavior

`genMonSharedKeyring()` renders `keyringTemplate` with the cluster monitor secret and the admin credential keyring. The template grants the mon identity full mon caps and appends admin keyring material.

`dataDirRelativeHostPath(monName)` returns the mon data directory below `dataDirHostPath`. Legacy names containing `mon` are used directly; letter IDs such as `a` become `mon-a/data`. This preserves Rook's historic storage layout.

`WriteConnectionConfig()` delegates to `cephclient.GenerateConnectionConfig()` and wraps failures. `CephSecretVolume()` creates a Secret volume named `ceph-admin-secret` from the `rook-ceph-mon` secret and maps `controller.CephUserSecretKey` to `secret.keyring`. `CephSecretVolumeMount()` mounts that secret read-only at `/var/lib/rook-ceph-mon`.

## State, Persistence, and Dependencies

Generated keyring content is stored by callers in Kubernetes Secrets. Connection config is written to the operator config directory. The volume helpers are consumed by mgr sidecars and other pods that need mon/admin credentials. Dependencies include Ceph client config generation, Rook key naming conventions, path utilities, and Kubernetes core volume types.

## Risks and Test Signals

The keyring template and secret key names are security-sensitive. Path compatibility is also important because changing `dataDirRelativeHostPath()` could orphan existing mon data. Coverage is mostly indirect through mon and mgr spec/startup tests that use these helpers to build deployments and sidecar volume mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain.go

## Purpose

This file reconciles the monitor PodDisruptionBudget used to keep voluntary node drains from breaking Ceph monitor quorum. It adjusts `maxUnavailable` based on desired mon count and current quorum health.

## Important APIs and Control Flow

`reconcileMonPDB()` exits early when `ManagePodBudgets` is disabled or `spec.Mon.Count <= 2`. For larger mon sets, it queries `cephclient.GetMonQuorumStatus()`, computes how many mons are down as `len(mon map) - len(quorum)`, and subtracts that from the allowed unavailable count. The result is clamped at zero, which blocks additional drains while monitors are already down. If the existing PDB already has the same `maxUnavailable`, reconciliation returns without updating.

`createOrUpdateMonPDB(maxUnavailable)` uses controller-runtime `CreateOrUpdate` to maintain `rook-ceph-mon-pdb` in the cluster namespace. The selector targets pods labeled `app=rook-ceph-mon`, and `MaxUnavailable` is an integer value. `getExistingMaxUnavailable()` reads the current PDB, returning `-1` for not found. `getMaxUnavailableMonPodCount()` returns `2` for five or more mons and `1` otherwise.

## State, Persistence, and Dependencies

The persistent object is a Kubernetes `policy/v1.PodDisruptionBudget`. Runtime state comes from Ceph quorum status. The code depends on controller-runtime client APIs, Ceph quorum command helpers, Rook logging, and Kubernetes label conventions.

## Risks and Test Signals

The safety-critical risk is allowing too many monitor pods to be drained during partial quorum loss. Conservative clamping to zero mitigates that. Another risk is stale PDB values if the Ceph quorum query fails; in that case reconciliation fails instead of guessing. `drain_test.go` covers disabled management, low mon counts, 3/5 mon quorum states, down-mon clamping, idempotent second reconciliation, and the max-unavailable threshold helper.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain_test.go

## Purpose

This file tests monitor PDB reconciliation under different mon counts and quorum states. It verifies that Rook creates, updates, or skips the mon PodDisruptionBudget in a way that protects quorum during node drains.

## Important APIs and Test Flow

`createMonQuorumResponse()` builds serialized `cephclient.MonStatusResponse` fixtures from mon names and quorum ranks. `createFakeClusterWithExecutor()` builds a fake mon `Cluster` with controller-runtime and client-go fake clients, a test `ClusterInfo`, and an optional executor returning the quorum fixture.

`TestReconcileMonPDB` is table-driven. Cases include disabled `ManagePodBudgets`, mon counts one and two, three healthy mons, three mons with one down, five healthy mons, and five mons with one, two, or three down. The test calls `reconcileMonPDB()`, checks whether a PDB should exist, asserts `maxUnavailable`, runs reconciliation a second time to cover idempotent no-change behavior, and deletes the PDB before the next case.

`TestGetMaxUnavailableMonPodCount` asserts the threshold helper: counts below five allow one unavailable mon pod, while five and seven allow two.

## State, Dependencies, and Integration

The tests persist PDBs in the fake controller-runtime client and use mock Ceph command output for quorum status. They depend on Rook test helpers, the Ceph client test package, Kubernetes policy API registration, and fake Kubernetes version setup.

## Risks and Test Signals

The tests strongly signal the drain-safety formula `allowedDown = baseAllowed - downMonCount`, including clamping negative results to zero. They do not cover PDB delete behavior when management becomes disabled because the implementation currently has a TODO instead of deletion. They also assume rank arrays accurately represent quorum membership, matching Ceph's quorum status contract.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint.go

## Purpose

This file provides the string serialization helper for monitor endpoints stored in Rook's mon endpoint ConfigMap and consumed by other Rook/Ceph components.

## Important APIs and Behavior

`flattenMonEndpoints(mons map[string]*cephclient.MonInfo)` iterates over monitor info values and returns a comma-delimited string of `name=endpoint` pairs. Each endpoint uses the `MonInfo.Name` and `MonInfo.Endpoint` fields. The format is the inverse of `controller.ParseMonEndpoints()` used elsewhere in the operator.

## State, Persistence, and Dependencies

The helper itself is stateless, but its output becomes persistent data in `rook-ceph-mon-endpoints` under the `data` key. That ConfigMap is then used for daemon connection config, env vars, CSI config, and reconciliation. Dependencies are minimal: standard string formatting/joining and the Ceph client's `MonInfo` type.

## Risks and Test Signals

Because Go map iteration order is intentionally nondeterministic, callers and tests must treat the endpoint list as an unordered set. The format is also delimiter-sensitive: monitor names and endpoints must not contain comma or equals characters in unexpected positions. `endpoint_test.go` validates round-tripping through `controller.ParseMonEndpoints()` for one and two monitors without assuming ordering for the multi-monitor case.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint_test.go

## Purpose

This file tests serialization of monitor endpoint maps into the ConfigMap string format and verifies that the result can be parsed back into monitor endpoint objects.

## Important APIs and Test Flow

`TestMonFlattening` starts with one monitor named `foo` at `1.2.3.4:5000`, calls `flattenMonEndpoints()`, expects the exact single-entry string, then parses it with `controller.ParseMonEndpoints()` and validates the parsed name and endpoint. It then adds `bar` at `2.3.4.5:6000`, flattens again, parses again, and validates that both monitors are present.

## State, Dependencies, and Integration

The test uses in-memory `map[string]*cephclient.MonInfo` values and the production parser from the controller package. This is an integration-style unit test for the writer and reader of the mon endpoints ConfigMap data format.

## Risks and Test Signals

The single-monitor assertion is exact because ordering is deterministic with one item. The multi-monitor part validates parsed map contents instead of raw string order, which is necessary because map iteration order is nondeterministic. The test would catch incompatible changes to the `name=endpoint` pair format or parser assumptions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/env.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/env.go

## Purpose

This file centralizes Kubernetes environment variable definitions that expose monitor namespace, monitor endpoint data, and Ceph username credentials to Rook sidecars and daemons.

## Important APIs and Behavior

`PodNamespaceEnvVar(namespace)` returns `ROOK_POD_NAMESPACE` with a literal namespace value. `EndpointEnvVar()` returns `ROOK_MON_ENDPOINTS` sourced from the `rook-ceph-mon-endpoints` ConfigMap `data` key. `CephUsernameEnvVar()` returns `ROOK_CEPH_USERNAME` sourced from the `rook-ceph-mon` Secret key identified by `controller.CephUsernameKey`.

## State, Persistence, and Dependencies

The file does not persist state. Its env var definitions depend on persisted ConfigMap and Secret objects created by monitor reconciliation and cluster access-secret management. Consumers include the mgr active watcher sidecar and other components that need live mon endpoint and username values without embedding them into pod specs.

## Risks and Test Signals

Incorrect object names or keys would cause pods to start with missing env vars or fail admission depending on Kubernetes behavior. The helpers reduce duplication, but coverage is indirect through pod spec tests that assert these env vars are present in sidecar containers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health.go

## Purpose

This file implements the monitor health loop and failover/removal logic. It is responsible for periodically checking Ceph monitor quorum, reconciling external monitors, adding or removing monitors to match the CRD, failing over unhealthy monitors, persisting out-of-quorum state, and cleaning up Kubernetes resources after mon changes.

## Important APIs and Control Flow

`NewHealthChecker()` creates a checker with the default `HealthCheckInterval`. `HealthChecker.Check()` loops until the cluster health context or cluster-info context is canceled. On each interval it refreshes `MonOutTimeout` and check interval from legacy env vars or CRD health settings, then calls `Cluster.checkHealth()`.

`checkHealth()` is serialized by the mon orchestration mutex. It validates cluster info, skips empty non-external clusters, honors skip-reconcile labels, handles external clusters through `handleExternalMonStatus()`, reconciles the mon PDB, reads quorum status, reconciles configured external mon IDs, and then compares Ceph quorum state with `ClusterInfo.InternalMonitors`. It marks mons in/out of quorum via `trackMonInOrOutOfQuorum()`, waits for `MonOutTimeout` before failover unless disabled or the assigned node was deleted, retries once for unscheduled pods after node drains, and handles one unhealthy mon per pass. It also starts new mons when below desired count, removes one extra mon when above desired count, cleans canaries on healthy convergence, evicts duplicate-node mons once per operator restart, checks multi-cluster service export state, and processes deferred `monsToFailover`.

`reconcileExternalMons()` tracks `spec.Mon.ExternalMonIDs` for local clusters by adding in-quorum external mons to `ClusterInfo.ExternalMons`, removing absent ones, saving config on change, and stripping external mons from quorum status before normal internal-mon logic. `removeMonsFromQuorumStatusResponse()` performs that rank-aware filtering.

`failMon()` chooses between removing an extra mon and `failoverMon()`. `failoverMon()` picks a replacement zone, optionally scales down the failed mon, schedules and starts a replacement, configures stretch arbiter if needed, increments max mon ID only after success, and removes the old mon. A defer path reverts replicas, removes the replacement, and rolls back maxMonID if replacement startup fails. `removeMonWithOptionalQuorum()` updates Ceph quorum, `ClusterInfo`, mapping, mon config, bootstrap peer secret, and Kubernetes resources.

## State, Persistence, and Dependencies

State spans `ClusterInfo.InternalMonitors`, `ExternalMons`, `OutOfQuorum`, `monTimeoutList`, `mapping.Schedule`, `monsToFailover`, mon endpoint ConfigMap, connection config on disk, PDBs, Deployments, Services, PVCs, and bootstrap peer Secret. Dependencies include Ceph quorum/mon commands, Rook controller config helpers, Kubernetes pod/node/deployment/PVC APIs, CSI config generation, and operator logging.

## Risks and Test Signals

This is high-risk quorum-preservation code. Risks include failing over too aggressively, losing quorum during drains, stale endpoint persistence, host-network replacement conflicts, external mons skewing desired-count logic, and global timeout variables shared across tests/process state. `health_test.go` provides broad signals for missing mons, extra mons, immediate node-deletion failover, duplicate-node eviction, host-network stop decisions, replica scaling, out-of-quorum persistence, timeout/interval overrides, and external mon behavior. `drain_test.go` complements it for PDB safety.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health_test.go

## Purpose

This file is the main test suite for monitor health, failover, scaling, out-of-quorum tracking, and external monitor reconciliation. It provides behavioral coverage for the most failure-prone logic in `health.go`.

## Important APIs and Test Flow

`TestCheckHealth` validates error returns before cluster info and mon count are initialized, then exercises health reconciliation, failover, replacement mon creation, deployment counts, and orphan PVC cleanup. `TestRemoveExtraMon` verifies extra-mon selection for duplicate nodes, arbitrary removal, and stretch-cluster zone rules. `TestScheduleFailoverImmediately` confirms deleted assigned nodes trigger immediate failover while unscheduled or existing-node mons do not. `TestTrackMonsOutOfQuorum` persists out-of-quorum state into the mon endpoints ConfigMap and clears it when the mon returns.

`TestEvictMonOnSameNode` creates fake running pods and verifies duplicate-node detection triggers a failover to a new mon. `TestHostNetworkFailover` covers whether the old mon should be scaled down during failover under default networking, host networking, and host-network migration cases. `TestScaleMonDeployment` checks direct replica toggling.

`TestCheckHealthNotFound` covers a mon in `ClusterInfo` missing from Ceph's mon map, expecting replacement and ConfigMap update. `TestAddRemoveMons` covers scaling from one to five, down to three, and the guard preventing reduction from two mons to one. `TestAddOrRemoveExternalMonitor` covers external-cluster monitor map refresh. `TestUpdateMonTimeout`, `TestUpdateMonInterval`, and `TestNewHealthChecker` cover health-loop configuration.

The three `TestExternalMons_*` cases cover external mon IDs not in spec, in spec but not quorum, and in spec and quorum, including interactions with downscale/upscale and endpoint ConfigMap persistence.

## State, Dependencies, and Integration

The tests use fake client-go and controller-runtime clients, temporary config dirs, mock Ceph executors, fake `CephCluster` objects, stubbed `waitForMonitorScheduling`, and the `UpdateDeploymentAndWaitStub`. They inspect Deployments, Pods, PVCs, ConfigMaps, and `ClusterInfo` maps.

## Risks and Test Signals

These tests are strong integration-style unit signals for monitor safety. They catch errors in one-mon-at-a-time removal, endpoint persistence, duplicate-node placement, external mon filtering, and timeout configuration. Risks are global hook mutation (`updateDeploymentAndWait`, `waitForMonitorScheduling`, `MonOutTimeout`) and reliance on canned quorum responses that may miss malformed Ceph output behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon.go -->
# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon.go

## Purpose

This file is the core monitor orchestrator for Rook-managed Ceph clusters. It creates and updates monitor Deployments, Services, PVCs, EndpointSlices, and endpoint ConfigMaps; initializes cluster info and keyrings; schedules monitors safely; waits for quorum; configures stretch clusters; persists mon identity state; and rotates monitor cephx keys.

## Important Types and APIs

`Cluster` holds cluster info, Kubernetes/Ceph context, spec, namespace, image, orchestration lock, port, `maxMonID`, startup wait flag, timeout map, node mapping, owner info, upgrade flag, arbiter mon, deferred failover map, and mon key Secret resource version. `monConfig` is the per-monitor runtime plan: resource name, daemon ID, public IP, port, zone, node, data path map, and whether the mon uses host networking. `SchedulingResult` returns the canary-scheduled node and optional canary artifacts.

`New()` initializes an empty mon cluster with a context-backed `ClusterInfo`, empty scheduling map, `maxMonID = -1`, and empty timeout/failover maps. `Start()` serializes orchestration, validates host-network/allow-multiple constraints and mon memory, initializes cluster info, and calls `startMons()`.

## Control Flow and Persistence

`initClusterInfo()` loads or creates cluster info and max mon ID, applies metadata to the mon secret, saves mon config, stores the shared mon keyring, and stores the admin keyring. `initMonConfig()` converts existing cluster info to `monConfig`s and appends new IDs/zones up to the desired count. `startMons()` schedules mons, sets default Ceph configs before or after starting depending on whether a cluster already exists, creates mons one at a time when growing, force-updates existing mons when needed, applies network settings, configures stretch behavior, reconciles PDBs, and removes orphan PVCs.

`scheduleMonitor()` creates a canary deployment to let Kubernetes choose a node while avoiding mutation of real mon storage. `assignMons()` runs canary scheduling concurrently, records explicit node info for host-network or hostPath mons, records zone assignments when required, and cleans canaries when appropriate. `initMonIPs()` creates services or uses host-network node addresses, exports services for multi-cluster service when enabled, and updates `ClusterInfo.InternalMonitors`.

`startDeployments()` creates or updates each mon deployment, waits for quorum according to startup/upgrade safety rules, and removes extra deployment resources. `startMon()` builds default or floating mon deployment specs, annotates them with the cephx key resource version and last-applied hash, configures storage/scheduling, updates existing deployments, creates new deployments, commits maxMonID after deployment creation, and persists expected mon daemons. `configureDefaultMonStorage()` preserves existing hostPath/PVC choices, expands PVCs on update, flags host-network/path transitions for failover, and applies placement and anti-affinity.

`saveMonConfig()` persists expected mons to the endpoint ConfigMap and EndpointSlices, updates the global config store, writes local connection config, and creates CSI `CephConnection`/default client profile when monitors exist. EndpointSlice persistence splits IPv4 and IPv6 addresses and exposes msgr2 plus optional msgr1 ports. ConfigMap persistence stores flattened endpoints, external mon IDs, maxMonID, scheduling mapping JSON, out-of-quorum mons, and CSI cluster config.

Stretch helpers enable stretch election strategy, create default stretch CRUSH rule, wait for CRUSH failure domains and `.mgr` pool, then configure or update the arbiter/tiebreaker. `RotateMonCephxKeys()` and `UpdateMonCephxStatus()` rotate monitor daemon keys when policy and Ceph version allow it, update the cluster access secret/shared keyring, and persist status with conflict retries.

## Dependencies and Integration Points

The file integrates with Ceph command APIs, Rook controller config and keyring stores, CSI custom resources, Kubernetes apps/core/discovery clients, service export helpers, object matcher annotations, Rook owner references, and health/failover logic in `health.go`. It is the persistence source for monitor endpoint data consumed by daemons, CSI, and sidecars.

## Risks and Test Signals

High-risk areas include maxMonID persistence during interrupted failovers, preserving mon identity across host-network and storage-mode changes, canary cleanup, EndpointSlice address parsing, stretch-cluster readiness gates, and quorum waits during upgrades. Tests in adjacent mon files cover deployment specs, scheduling, health, node assignment, endpoint persistence, and key rotation behavior; this file's functions are also indirectly exercised by `health_test.go`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon.go -->
