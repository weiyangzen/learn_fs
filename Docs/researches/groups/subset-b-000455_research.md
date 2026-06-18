# Research: subset-b-000455

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/controller_test.go

## Purpose
This test file validates the top-level Ceph operator configuration reconciler behavior around operator settings. It exercises `ReconcileConfig.Reconcile` through fake Kubernetes clients and confirms that environment/config-map-driven settings are applied without requeueing.

## Important APIs, Types, and Functions
The only test entry point is `TestOperatorController`. It builds `clusterd.Context` values with fake core and Rook clientsets, uses controller-runtime fake clients with either the Rook scheme or the client-go scheme, and constructs `ReconcileConfig` with `controller.OperatorConfig`. It asserts effects on `exec.CephCommandsTimeout`, `controller.LoopDevicesAllowed()`, and discovery daemonset creation.

## Control Flow, State, and Persistence
Each subtest creates an isolated fake clientset and reconciler, then calls `Reconcile` with a request targeting `rook-ceph-operator-config` in `rook-ceph`. State is process-local except for environment variables like `ROOK_CEPH_COMMANDS_TIMEOUT_SECONDS`, `ROOK_ENABLE_DISCOVERY_DAEMON`, and `ROOK_CEPH_ALLOW_LOOP_DEVICES`, plus fake API objects created during reconciliation.

## Dependencies and Integration Points
The test integrates top-level operator config reconciliation with `pkg/operator/ceph/controller`, `pkg/util/exec`, discovery daemon handling, and Kubernetes version probing through `test.SetFakeKubernetesVersion`.

## Risks
Several subtests mutate package globals and environment variables, so test isolation depends on `t.Setenv` or explicit cleanup. The fake schemes differ by case, which is useful coverage but can mask scheme-registration dependencies in real managers.

## Test Signals
Coverage confirms normal reconciliation, command timeout from env/config, discovery daemon enablement, and loop-device allowance. It does not validate failure paths or real config-map content because fake clients often start empty.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cr_manager.go -->
# sources/control-plane/rook/pkg/operator/ceph/cr_manager.go

## Purpose
`cr_manager.go` wires Rook Ceph custom-resource controllers into a controller-runtime manager. It is the registration point for the main Ceph cluster controller, child resource controllers, CSI, object/file/pool controllers, and the maintenance/disruption controller.

## Important APIs, Types, and Functions
`resourcesSchemeFuncs` registers client-go and Ceph API schemes. `AddToManagerFuncs` lists child controller `Add` functions for node daemons, pools, object users, realms/zones, object stores, filesystems, NFS, RBD, clients, NVMe-oF, mirroring, the operator config controller, CSI, bucket/topic/notification, subvolume groups, rados namespaces, COSI, and object accounts. `AddToManagerFuncsMaintenance` currently contains `clusterdisruption.Add`. `Operator.addToManager` registers cluster, child, and maintenance controllers. `Operator.startCRDManager` builds and starts the controller-runtime manager.

## Control Flow, State, and Persistence
Startup creates a new runtime scheme, configures metrics binding from `ROOK_OPERATOR_METRICS_BIND_ADDRESS`, optionally restricts cache namespaces using `NamespaceToWatch`, creates a manager from in-cluster/rest config, builds a `controllerconfig.Context`, registers controllers, and blocks in `mgr.Start(context)`. Errors are sent to `mgrErrorCh`; no persistent state is written by this file directly.

## Dependencies and Integration Points
The file integrates all Ceph operator packages with controller-runtime manager/cache/config APIs, `clusterd.Context`, operator config, and maintenance context. `controllerconfig.LockingBool` is prepared for disruption reconciliation coordination.

## Risks
Controller order is implicit in list order and can affect watches or shared resources. A failure in any child registration aborts the whole manager. Namespace cache restriction must match all watched resources. The package global `EnableMachineDisruptionBudget` is declared here but not used in this file.

## Test Signals
Signals come mainly from individual controller tests and operator startup integration tests. Registration failures, scheme omissions, and namespace cache behavior are the critical cases to test around this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/cr_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection.go

## Purpose
This file creates or updates ceph-csi-operator `CephConnection` custom resources that describe how CSI drivers connect to a Rook-managed Ceph cluster.

## Important APIs, Types, and Functions
`CreateUpdateCephConnection` upserts a `csiopv1.CephConnection` named after the Ceph cluster namespace and placed in the operator pod namespace. `generateCephConnSpec` builds `CephConnectionSpec` with monitors, read-affinity settings, and the first `CephRBDMirror` daemon count. `ReadAffinityEnabled` gates read affinity and disables it specifically for Ceph `20.2.0`.

## Control Flow, State, and Persistence
The reconciler reads `POD_NAMESPACE`, lists `CephRBDMirror` resources in the cluster namespace, computes monitor endpoints using `MonEndpoints`, and persists the result as a controller-runtime custom resource create or update. Read affinity defaults to CRUSH topology labels when enabled without explicit labels.

## Dependencies and Integration Points
It depends on Rook Ceph cluster info, Ceph version parsing, `cephv1.ClusterSpec`, OSD topology defaults, and the ceph-csi-operator API. It reuses `cluster_config.go` for monitor endpoint formatting.

## Risks
Only the first `CephRBDMirror` item is used, so multiple mirror CRs are not represented. Upserts use the cluster context and operator namespace env var, making missing env setup a deployment/test risk. Read affinity has a hard-coded version exclusion that must track Ceph bugs.

## Test Signals
Tests cover create/update with and without RBD mirror resources, default topology labels, and read-affinity behavior for versions below, at, and above `20.2.0`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection_test.go

## Purpose
This test file validates `CephConnection` CR generation for the ceph-csi-operator integration.

## Important APIs, Types, and Functions
`TestCreateUpdateCephConnection` exercises `CreateUpdateCephConnection` with fake cluster info, a fake controller-runtime client, and optional `CephRBDMirror` objects. `TestCephConnectionDefaultTopology` checks default CRUSH label expansion. `TestReadAffinityEnabled` table-tests the Ceph version gate.

## Control Flow, State, and Persistence
Tests set `POD_NAMESPACE`, register Ceph and ceph-csi API types in the shared scheme, call the upsert API, and read the resulting `CephConnection` object from the fake API server. State persists only in the fake client.

## Dependencies and Integration Points
The tests depend on `clienttest.CreateTestClusterInfo`, Rook client scheme registration, ceph-csi-operator API structs, and topology default labels.

## Risks
The test mutates a package/global scheme with `AddKnownTypes`, which can leak across tests in the same package. It verifies the count and contents of default labels but not monitor endpoint ordering, ownership, namespace env failure, or update-over-existing behavior with changed specs.

## Test Signals
Strong signals are mirror daemon count propagation, default read-affinity topology, and the Ceph `20.2.0` disablement. Additional useful coverage would include existing object update and list failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config.go

## Purpose
`cluster_config.go` manages legacy ceph-csi cluster JSON config and the `rook-ceph-csi-config` ConfigMap. It also formats monitor endpoints and normalizes network namespace fields during the ceph-csi-operator transition.

## Important APIs, Types, and Functions
`CSIClusterConfigEntry` embeds `cephcsi.ClusterInfo` and adds `Namespace`. `FormatCsiClusterConfig`, `parseCsiClusterConfig`, and `formatCsiClusterConfig` marshal/unmarshal JSON. `MonEndpoints` optionally converts msgr1 monitor ports to msgr2. `updateCsiClusterConfig` adds, updates, or removes cluster entries while preserving subvolume groups, RBD namespaces, mount options, NFS/RBD/CephFS network fields, and read-affinity values. `CreateCsiConfigMap` and `updateCsiConfigMapOwnerRefs` create or fix the CSI ConfigMap owner reference.

## Control Flow, State, and Persistence
The key state is JSON stored under `csi-cluster-config-json` in `rook-ceph-csi-config`. Updates parse existing JSON, patch entries by cluster ID and namespace, clear `NetNamespaceFilePath` for entries owned by the namespace, and marshal back to JSON. ConfigMap owner references are corrected to the operator deployment owner.

## Dependencies and Integration Points
The file integrates with ceph-csi JSON schema, Rook cluster info, Kubernetes ConfigMaps, `k8sutil.OwnerInfo`, and CSI read-affinity logic.

## Risks
JSON entry update behavior is intricate and order-sensitive. `MonEndpoints` iterates maps, so output order is nondeterministic. `updateCsiClusterConfig` only updates some nested fields when non-empty, which preserves state but can make clearing fields difficult. Owner-ref correction overwrites multiple owners to a single expected owner.

## Test Signals
Tests cover JSON add/update/remove scenarios, mon port conversion including IPv6, namespace correction, net namespace clearing, and owner-ref repair. A test helper bug compares expected JSON to itself, weakening some string-equality assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config_test.go

## Purpose
This test file exercises the legacy ceph-csi JSON config update algorithm, monitor endpoint conversion, network namespace cleanup, and CSI ConfigMap owner-reference repair.

## Important APIs, Types, and Functions
`TestUpdateCsiClusterConfig` covers many incremental updates through `updateCsiClusterConfig`: monitors, multi-cluster entries, subvolume groups, mount options, RBD rados namespaces, Multus net namespace data, read affinity, invalid input, and namespace correction. `TestMonEndpoints`, `TestUpdateNetNamespaceFilePath`, and `Test_updateCsiConfigMapOwnerRefs` cover focused helpers. `contains`, `verifyEndpointPort`, `unmarshal`, and `compareJSON` are test helpers.

## Control Flow, State, and Persistence
Tests build JSON strings, update them repeatedly, parse results, and use fake Kubernetes clients for ConfigMap owner-reference updates. The owner-ref tests create or fetch `rook-ceph-csi-config` in fake clientsets and assert resulting owner metadata.

## Dependencies and Integration Points
The tests use ceph-csi deploy API structs, Rook topology defaults, fake Kubernetes clientsets, and `k8sutil.NewOwnerInfoWithOwnerRef`.

## Risks
`compareJSON` unmarshals `exceptedJSON` into both expected and actual variables, so calls to it do not validate `actualJSON`. Many important assertions are still direct `parseCsiClusterConfig` checks, but string-shape tests using `compareJSON` are weak. Map iteration can also make monitor order nondeterministic.

## Test Signals
Useful signals include preservation of subvolume group during monitor updates, propagation of mon changes to all entries in the same namespace, IPv6 msgr2 conversion safety, clearing old holder-pod net namespace paths, and replacing stale CephCluster owner refs with the operator owner.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/config.go

## Purpose
`config.go` creates and updates ceph-csi-operator `ClientProfile` custom resources for default CSI access, RBD rados namespaces, and CephFS subvolume groups.

## Important APIs, Types, and Functions
Package globals hold derived CSI driver names and config keys. `CreateUpdateClientProfileRadosNamespace`, `CreateUpdateClientProfileSubVolumeGroup`, and `CreateDefaultClientProfile` construct `csiopv1.ClientProfile` specs. `generateProfileSubVolumeGroupSpec` builds the CephFS profile and applies mount options. `createUpdateClientProfile` handles get/create/update. `applyCephFSMountOptions` and `parseMountOptions` translate comma-separated `key=value` CephFS mount options into maps expected by ceph-csi-operator.

## Control Flow, State, and Persistence
Profile CRs are named by the cluster namespace, rados namespace, or subvolume group cluster ID and are created in `POD_NAMESPACE`. Specs reference the `CephConnection`, CSI secret names in the Ceph namespace, and optional CephFS/RBD settings. Updates replace the existing profile spec.

## Dependencies and Integration Points
The file integrates Rook cluster info, `cephv1.CSIDriverSpec`, ceph-csi-operator APIs, Kubernetes secret references, and env-driven operator namespace selection.

## Risks
`applyCephFSMountOptions` uses `else if`, so kernel options take precedence and fuse options are skipped if both are provided. `parseMountOptions` silently ignores options without `=`, which may hide invalid user input. Missing `POD_NAMESPACE` can place profiles in an empty namespace.

## Test Signals
Tests cover rados namespace and subvolume group profile creation, CephFS rados namespace pointers, kernel mount option parsing, multiple options, whitespace handling, and empty input.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/config_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/config_test.go

## Purpose
This test file verifies `ClientProfile` creation for RBD rados namespaces and CephFS subvolume groups, plus CephFS mount option parsing.

## Important APIs, Types, and Functions
`TestCreateUpdateClientProfile` constructs test cluster info with `CSIDriverSpec.CephFS.KernelMountOptions`, creates both profile types, and fetches them from a fake controller-runtime client. `TestParseMountOptions` table-tests `parseMountOptions`.

## Control Flow, State, and Persistence
The test sets `POD_NAMESPACE`, registers ceph-csi profile types, creates profiles with fake clients, and asserts persisted CR fields. Mount parsing tests are pure in-memory.

## Dependencies and Integration Points
Dependencies include ceph-csi-operator API types, Rook fake cluster info, Rook scheme registration, and Kubernetes `types.NamespacedName`.

## Risks
The test covers create paths but not update-over-existing behavior or error paths. It only validates kernel options, leaving the `FuseMountOptions` branch untested. The test double-registers namespace/name setup, which is harmless but noisy.

## Test Signals
Signals include correct RBD `RadosNamespace`, CephFS `SubVolumeGroup`, CephFS metadata rados namespace pointer, and parsing of one or more comma-separated `key=value` mount options.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/controller.go

## Purpose
`controller.go` defines the CSI controller reconciler that reacts to operator config and CephCluster events, initializes CSI shared config, applies operator settings, derives driver names, and prepares ceph-csi-operator mapping state.

## Important APIs, Types, and Functions
`ReconcileCSI` stores scheme, controller-runtime client, `clusterd.Context`, operator context/config, and the first cluster spec. `Add`, `newReconciler`, and `add` register the controller, CSIAddons scheme, ConfigMap watch, CephCluster watch, and ceph-csi-operator scheme. `Reconcile` wraps `reconcile` with panic recovery. `reconcile` creates the CSI ConfigMap, applies operator settings, derives `CephFSDriverName`, `RBDDriverName`, and `NFSDriverName`, lists CephClusters, creates an empty peer-map config, and loads cluster info for ready clusters.

## Control Flow, State, and Persistence
On each reconcile, the controller obtains an operator deployment owner reference, ensures `rook-ceph-csi-config`, applies operator settings from ConfigMap/env, then lists all CephClusters. If none exist, it exits. For existing clusters it skips deleting/cleanup-policy clusters, stores the first spec, loads cluster info, and sets owner info. State persists in Kubernetes ConfigMaps and package-level driver name globals.

## Dependencies and Integration Points
It integrates with controller-runtime watches/predicates, CSIAddons API, ceph-csi-operator API, Rook operator settings, cluster info loading, and peer-map config creation.

## Risks
Package-level driver name mutation affects all clusters and tests. The reconciler returns early if any cluster is deleting or has cleanup policy, which can skip later clusters. Cluster info load failures can either requeue or abort depending on type. The file currently prepares cluster info but does not itself call the CephConnection/Profile creation helpers.

## Test Signals
Tests validate no-cluster and basic cluster-present reconciliation. Broader signals would verify watch setup, peer-map creation, multi-cluster iteration behavior, and driver-name globals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/controller_test.go

## Purpose
This test file checks basic reconciliation behavior for the CSI controller in no-cluster and cluster-present scenarios.

## Important APIs, Types, and Functions
`TestCephCSIController` creates fake operator pod/replicaset objects, fake core/Rook clientsets, a fake controller-runtime client, and a `ReconcileCSI`. It calls `Reconcile` with a request for the operator namespace.

## Control Flow, State, and Persistence
The no-cluster case verifies reconciliation exits without error. The success case creates a `CephCluster` object and a `rook-ceph-mon` secret with `fsid`, `mon-secret`, and `admin-secret` so `LoadClusterInfo` can proceed. The fake API server holds created ConfigMaps and any other reconciled resources.

## Dependencies and Integration Points
The test depends on `test.FakeOperatorPod`, `test.FakeReplicaSet`, Rook fake clientsets, Ceph/Rook scheme registration, and env vars `POD_NAME` and `POD_NAMESPACE`.

## Risks
The test does not assert the resulting ConfigMap, peer-map config, driver names, or loaded cluster owner info. It mainly checks that the reconciliation path does not fail with prepared fake inputs.

## Test Signals
Signals are smoke-level: no CephCluster is a no-op, and a minimally ready cluster with mon secret reconciles without requeueing. More targeted assertions would improve behavioral confidence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config.go

## Purpose
This file maintains peer cluster and RBD pool ID mappings used by ceph-csi for RBD mirroring disaster recovery. It writes mappings to `rook-ceph-csi-mapping-config`.

## Important APIs, Types, and Functions
`PeerIDMapping` stores one peer-to-local cluster ID map and a list of peer-to-local RBD pool ID maps. `PeerIDMappings` has methods for adding cluster maps, adding pool maps, updating pool maps, JSON serialization, and lookup. `ReconcilePoolIDMap` skips pools without peer secrets, gets mappings, and calls `CreateOrUpdateConfig`. `getClusterPoolIDMap` reads local pool details, peer bootstrap secrets, decodes tokens, queries peer pool details through `ceph`, and builds mappings. `CreateOrUpdateConfig`, `UpdateExistingData`, `createConfig`, `decodePeerToken`, `getPeerPoolDetails`, and `getMapKV` support persistence and CLI interaction.

## Control Flow, State, and Persistence
State is persisted in a ConfigMap key `csi-mapping-config-json` in the operator namespace. New mappings are merged with existing config data unless it is exactly `[]`. Peer pool queries use temporary keyring, config, and output files and execute `ceph osd pool get ... --format json`.

## Dependencies and Integration Points
Dependencies include CephBlockPool mirroring peer secrets, Kubernetes Secrets/ConfigMaps, Rook Ceph client pool-detail parsing, operator deployment owner references, and the configured executor.

## Risks
Single-entry maps are assumed by `getMapKV`; empty maps silently produce empty keys. Config merging never removes stale peer/pool mappings. Peer secret token content and temp-file cleanup are critical. The command argument layout is tested indirectly and can be brittle.

## Test Signals
Tests cover cluster and pool map insertion/update, single and multi-peer mapping generation, token decoding, and create/update ConfigMap behavior with fake command output.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config_test.go

## Purpose
This test file validates peer-map data structure behavior, peer token decoding, peer pool ID discovery, and mapping ConfigMap creation/update.

## Important APIs, Types, and Functions
Tests include `TestAddClusterIDMapping`, `TestUpdateClusterPoolIDMap`, `TestAddPoolIDMapping`, `TestSinglePeerMappings`, `TestMultiPeerMappings`, `TestDecodePeerToken`, and `TestCreateOrUpdateConfig`. Helpers define fake peer tokens/secrets, fake mirrored pools, `saveMockDataInTempFile`, a `mockExecutor`, and `validateConfig`.

## Control Flow, State, and Persistence
The mock executor returns local pool details and writes peer pool details into temp output files that `getPeerPoolDetails` later reads. Tests use fake Kubernetes clientsets for peer Secrets and controller-runtime fake clients for the mapping ConfigMap. Env vars identify operator pod and namespace for owner reference creation.

## Dependencies and Integration Points
The tests use Rook Ceph API schemes, fake operator pods/replicasets, `exectest.MockExecutor`, Kubernetes fake clients, and base64-encoded peer tokens matching `cephclient.PeerToken`.

## Risks
The temp-file helper appends to any matching temp file by prefix, which is acceptable in a controlled unit test but could be flaky if stale temp files remain. `TestCreateOrUpdateConfig` comments out one validation after adding data, reducing coverage of the second create/update step.

## Test Signals
Signals cover idempotent cluster map adds, updating an existing peer pool ID, adding new pools and clusters, multi-peer mapping shape, invalid token rejection, and persisted ConfigMap JSON equivalence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/predicate.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/predicate.go

## Purpose
This file defines controller-runtime predicates controlling when the CSI controller reconciles for operator ConfigMap and CephCluster events.

## Important APIs, Types, and Functions
`cmPredicate` returns typed predicates for `ConfigMap` events. It accepts creates/deletes for the operator settings ConfigMap and updates when `.Data` changes according to `cmp.Diff`. `cephClusterPredicate` accepts CephCluster creates only when not a duplicate and either the operator config map is absent or the cluster generation is `1`; it ignores updates and accepts deletes.

## Control Flow, State, and Persistence
Predicates are pure event filters except `cephClusterPredicate`, which reads the operator config map and checks duplicate clusters through the controller-runtime client. They do not persist state.

## Dependencies and Integration Points
They integrate with `controller.OperatorSettingConfigMapName`, `opcontroller.DuplicateCephClusters`, Kubernetes API errors, go-cmp, and controller-runtime typed event/predicate APIs.

## Risks
The ConfigMap update comparison uses only `.Data`, so metadata or owner changes do not trigger reconciliation. CephCluster updates never trigger CSI reconcile, so CSI settings changed in cluster spec rely on other controllers/flows. The create predicate has nuanced behavior when the operator ConfigMap is absent to support env-var-only deployments.

## Test Signals
Tests cover create/delete/update behavior for operator ConfigMaps and CephCluster create filtering by generation, config-map presence, and duplicate cluster detection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/predicate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/predicate_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/predicate_test.go

## Purpose
This test file verifies CSI controller predicates for operator ConfigMap and CephCluster events.

## Important APIs, Types, and Functions
`Test_cmPredicate` exercises ConfigMap create, delete, and update event filters. `Test_cephClusterPredicate` exercises CephCluster create decisions with fake clients containing or omitting the operator config map and duplicate clusters.

## Control Flow, State, and Persistence
Tests build typed controller-runtime events and call predicate methods directly. CephCluster predicate tests use fake controller-runtime clients and registered schemes to simulate config-map lookup and duplicate cluster listing.

## Dependencies and Integration Points
The tests integrate `corev1.ConfigMap`, `cephv1.CephCluster`, the Rook scheme, controller-runtime fake client, and capnslog debug logging.

## Risks
Update/delete/generic behavior for CephCluster is mostly untested except as code inspection. ConfigMap tests only change `.Data`; they do not cover resource quantity comparison or metadata-only changes.

## Test Signals
Signals confirm non-operator ConfigMaps are ignored, operator config creates/deletes reconcile, data changes reconcile, repeated CephCluster generations are suppressed when a ConfigMap exists, env-only deployments reconcile without the ConfigMap, and duplicate clusters are suppressed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/predicate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/secrets.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/secrets.go

## Purpose
`secrets.go` creates, rotates, prunes, and persists CephX credentials for CSI RBD and CephFS node/provisioner users.

## Important APIs, Types, and Functions
Constants define Ceph client base names and Kubernetes Secret names. `createCSIKeyring` determines rotation state, generates the desired Ceph client key, prunes older generations, and returns key metadata. Capability helpers define RBD/CephFS node/provisioner caps. `createOrUpdateCSISecret` writes four Kubernetes secrets. `CreateCSISecrets` orchestrates all four users and updates CephCluster CSI CephX status. Helpers include `updateCephStatusWithCephxStatus`, `getPriorKeyCount`, `getCsiKeyRotationInfo`, `getMatchingClient`, `parseCsiClient`, `deleteOldKeyGen`, `deleteCount`, `deleteOwnedCSISecretsByCephCluster`, `sortCSIClientName`, and `deduplicate`.

## Control Flow, State, and Persistence
If `SkipUserCreation` is true, owned CSI secrets are deleted and Ceph user creation is skipped. Otherwise, the file reads the CephCluster, lists existing Ceph auth entities, computes desired key generation/status, creates Ceph auth keys, deletes excess old generations, writes Kubernetes Secrets with `userID`/`userKey`, and updates `status.cephx.csi`.

## Dependencies and Integration Points
It integrates with Ceph CLI auth commands, Rook keyring secret store, CephCluster security status, Kubernetes Secrets, owner references, and Rook status reporting.

## Risks
Rotation correctness depends on parsing `client.<name>[.<generation>]`; malformed names are logged but may still enter sorting with generation zero. Deletion errors are logged but do not stop rotation after key creation. Secret creation delegates to `SecretStore.CreateSecret`, so update semantics depend on that store. Status key counts use the max across four clients.

## Test Signals
Tests cover caps, owned secret deletion, generation sorting/parsing, auth-list handling, deletion count math, old-key pruning, matching clients, and prior-key count.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/secrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/secrets_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/csi/secrets_test.go

## Purpose
This test file validates CSI CephX capability definitions, key-generation parsing/sorting/pruning, auth-list inspection, and deletion of Rook-owned CSI secrets.

## Important APIs, Types, and Functions
Tests include caps checks, `Test_deleteOwnedCSISecretsByCephCluster`, `TestSortCsiClientName`, `TestDeleteOldKeyGen`, `TestGetCsiKeyRotationInfo`, `TestGetCSIKeyInfoAndDeleteOldKey`, `Test_getMatchingClient`, `TestParseCsiClient`, `TestGetPriorKeyCount`, and `Test_deleteCount`. `loadTestClusterDetails` builds fake cluster context/info/spec.

## Control Flow, State, and Persistence
Mock executors return fake `ceph auth ls` JSON and record `auth del` calls. Fake Kubernetes clientsets hold Secrets and verify owner-based deletion. Pure helpers are tested with table-driven inputs.

## Dependencies and Integration Points
The tests use Rook fake exec, fake Kubernetes clientsets, keyring helpers, Ceph auth JSON output, and Kubernetes API error handling.

## Risks
`sortCSIClientName` appends entries even when parsing fails, with suffix zero; tests do not cover this malformed-entry ordering directly. `CreateCSISecrets` full orchestration and status update conflicts are not directly exercised. Some expected auth lists preserve input order before sorting, which is acceptable for `getMatchingClient` but not a sorted contract.

## Test Signals
Signals cover least-privilege capability strings, secret owner protection, numeric generation ordering, no-delete boundaries, timeout/invalid JSON auth-list errors, exact old-key deletion order, many malformed client-name cases, and deletion math.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/csi/secrets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/add.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/add.go

## Purpose
`add.go` registers the cluster disruption controller and its watches. The controller manages safe PodDisruptionBudget behavior for Ceph OSDs, RGWs, and MDS daemons.

## Important APIs, Types, and Functions
`objectsToWatch` lists `CephBlockPool`, `CephFilesystem`, and `CephObjectStore`. `cephClusterPredicate` reconciles on CephCluster creates and spec updates. `pdbPredicate` watches the main OSD PDB and reconciles when `DisruptionsAllowed` falls to zero with `maxUnavailable=1`. `watchNamespacedObject` maps namespaced child resource events to a reconcile request for that namespace. `Add` constructs `ReconcileClusterDisruption`, creates the controller, and registers all watches.

## Control Flow, State, and Persistence
Registration creates a shared `ClusterMap` and passes it to the reconciler. Watches enqueue either direct CephCluster requests or namespace-only requests that the reconciler later resolves to the cluster name.

## Dependencies and Integration Points
It integrates controller-runtime controller/watch/source/handler/predicate APIs, Rook Ceph CRDs, Kubernetes PDBs, and `controllerconfig.Context`.

## Risks
Spec comparison uses `reflect.DeepEqual`, so semantically equivalent defaulting changes can trigger reconciliation. Namespace-only requests depend on `ClusterMap` being populated during reconciliation. PDB predicate only watches a narrow transition on the default OSD PDB.

## Test Signals
This file has no direct test in the subset. Behavior is indirectly tested by disruption reconciler tests and would benefit from predicate/watch unit coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/doc.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/doc.go

## Purpose
`doc.go` provides the package-level documentation for `clusterdisruption`, describing it as the controller responsible for safe drain handling.

## Important APIs, Types, and Functions
There are no runtime APIs in this file. Its package comment points readers to the Rook design document for Ceph managed disruption budgets.

## Control Flow, State, and Persistence
There is no control flow or persisted state. The file exists for Go package documentation.

## Dependencies and Integration Points
The documentation links the implementation package to the design rationale for managed disruption budgets.

## Risks
The GitHub design URL points at the `master` branch, so the referenced design can drift from the checked-out source version.

## Test Signals
No tests apply directly. Documentation accuracy should be reviewed when disruption-budget behavior changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd.go

## Purpose
`osd.go` implements dynamic OSD PodDisruptionBudget management during node drains and OSD outages. It protects non-draining failure domains, allows one active drain domain, and manages Ceph `noout` on drained failure domains.

## Important APIs, Types, and Functions
PDB helpers include `createPDB`, `deletePDB`, `createDefaultPDBforOSD`, `deleteDefaultPDBforOSD`, `createBlockingPDBForOSD`, and `deleteBlockingPDBForOSD`. State helpers include `initializePDBState`, `resetPDBConfig`, `setPDBConfig`, and `getLastNodeDrainTimeStamp`. Main orchestration is `reconcilePDBsForOSDs`. Discovery helpers include `getOSDFailureDomains`, `hasOSDNodeDrained`, `getNode`, `getPDBName`, `requeuePDBController`, and `pdbExcludesOSDs`. `updateNoout` applies/unsets Ceph `noout` per CRUSH unit.

## Control Flow, State, and Persistence
The reconciler reads Ceph health, OSD deployments, OSD metadata, Kubernetes Nodes, and a state ConfigMap `rook-ceph-pdbstatemap`. Clean clusters reset state and restore a default PDB. Unhealthy OSD-down states set a draining failure domain, delete the default PDB, and create blocking PDBs for other domains. Clean clusters with down OSDs can exclude those OSD IDs from the default PDB. State is persisted in the ConfigMap and PDB objects; Ceph flags are persisted in OSD map state.

## Dependencies and Integration Points
It integrates with Ceph status/OSD dump/metadata commands, Rook OSD labels, Kubernetes Deployments/Nodes/PDBs/ConfigMaps, topology failure domains, and operator requeue constants.

## Risks
Correctness depends on deployment labels and Ceph metadata hostnames. The state machine is time-sensitive, especially the 60-second wait after node drain detection and maintenance timeout. `sets.List` ordering can influence which failure domain is chosen first. `updateNoout` errors are logged but reconciliation continues to update ConfigMap state.

## Test Signals
Tests cover failure-domain detection, node-drain detection, healthy/unhealthy PDB transitions, OSD exclusion, `setPDBConfig`, and custom PG healthy regex behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd_test.go

## Purpose
This test file validates OSD disruption state-machine behavior, including failure-domain discovery, node-drain detection, PDB creation/deletion, and ConfigMap state updates.

## Important APIs, Types, and Functions
Helpers define fake Ceph status JSON, fake OSD deployments, fake nodes, fake PDB ConfigMaps, fake reconcilers, and fake cluster info. `TestGetOSDFailureDomains`, `TestGetOSDFailureDomainsError`, `TestReconcilePDBForOSD`, `TestHasNodeDrained`, and `TestSetPDBConfig` cover the main behavior.

## Control Flow, State, and Persistence
Tests use controller-runtime fake clients containing Deployments, Nodes, ConfigMaps, and CephCluster objects. Mock executors return Ceph `status`, `osd dump`, and `osd metadata` output. Reconcile tests inspect created PDBs and updated ConfigMaps.

## Dependencies and Integration Points
The file depends on Rook schemes, fake exec, Kubernetes fake client objects, OSD topology labels, and PDB v1 APIs.

## Risks
Many assertions rely on deterministic ordering of failure-domain slices returned from sets; this can be fragile if set ordering changes. `updateNoout` is only lightly exercised through mock OSD dump output, not detailed CRUSH flag behavior. Timing behavior around the 60-second node-drain delay is not directly tested.

## Test Signals
Strong signals include schedulable vs unschedulable node detection, missing node treated as drained, missing topology label errors, active drain blocking PDBs, default PDB restoration, excluded down OSDs, and `set-no-out` state selection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/osd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools.go

## Purpose
`pools.go` summarizes Ceph pool failure domains and reconciles static PDBs for object store RGW and filesystem MDS workloads.

## Important APIs, Types, and Functions
`processPools` lists CephBlockPools, CephFilesystems, and CephObjectStores in a namespace, collects their pool specs, counts top-level pool-bearing resources, and returns the minimum failure domain. `getMinimumFailureDomain` chooses the lowest-ranked CRUSH failure domain based on `topology.CRUSHMapLevelsOrdered`. `reconcileCephObjectStore` creates or deletes RGW PDBs. `reconcileCephFilesystem` creates or deletes MDS PDBs.

## Control Flow, State, and Persistence
Pool processing reads CRs from the API server but persists nothing. RGW PDBs use `minAvailable = gateway instances - 1` and are deleted if that falls below 1. MDS PDBs use `activeCount - 1`, adding one when active-standby is enabled, and delete stale PDBs if below 1. Static PDBs are persisted through `reconcileStaticPDB`.

## Dependencies and Integration Points
The file integrates with Rook Ceph CRDs, topology ordering, Kubernetes PDB APIs, and owner references to the owning object store or filesystem.

## Risks
`processPools` increments `poolCount` by CR count, not actual pool spec count, which is sufficient for deciding whether any pool-bearing CR exists but not for precise pool totals. `reconcileStaticPDB` does not update existing PDB specs, so scale changes above the deletion threshold may leave stale `minAvailable` values.

## Test Signals
Tests cover minimum failure-domain selection and stale/create behavior for RGW and MDS PDBs, including scale-down deletion and active-standby MDS creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools_test.go

## Purpose
This test file verifies failure-domain selection and static PDB behavior for RGW object stores and CephFS MDS workloads.

## Important APIs, Types, and Functions
`TestGetMinimumFailureDomain` validates `getMinimumFailureDomain`. `TestReconcileCephObjectStorePDB` covers stale PDB deletion and PDB creation for gateway instances. `TestReconcileCephFilesystemPDB` covers stale MDS PDB deletion and active-standby creation.

## Control Flow, State, and Persistence
Tests build fake controller-runtime clients with optional pre-existing PDBs, call the reconcile helper, then fetch PDBs to assert creation or deletion. State exists only in the fake API client.

## Dependencies and Integration Points
The tests use the Rook scheme, Kubernetes PDB v1 scheme, controllerconfig context with `context.TODO()`, and fake controller-runtime clients.

## Risks
Existing PDB update behavior is not tested; this is important because `reconcileStaticPDB` leaves existing specs unchanged. `processPools` itself is not tested for list aggregation across block pools, filesystems, and object stores.

## Test Signals
Signals include host/zone/region ordering, defaulting to host for unknown domains, stale PDB deletion when instance counts cannot tolerate disruption, RGW PDB creation for two instances, and MDS PDB creation with one active plus standby.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile.go

## Purpose
`reconcile.go` is the top-level reconciliation loop for managed Ceph disruption budgets. It coordinates cluster discovery, pool/RGW/MDS PDB reconciliation, OSD PDB state-machine execution, and cleanup of legacy drain canary resources.

## Important APIs, Types, and Functions
`ReconcileClusterDisruption` holds scheme, controller-runtime client, `controllerconfig.Context`, `ClusterMap`, and maintenance timeout. `Reconcile` wraps `reconcile` with panic recovery. `reconcile` lists CephClusters in the request namespace, updates `ClusterMap`, checks `ManagePodBudgets`, deletes legacy drain canaries once, computes maintenance timeout, calls pool/static PDB processing, computes OSD failure domains, initializes PDB state, and calls `reconcilePDBsForOSDs`. `ClusterMap` provides synchronized namespace-to-cluster storage and lookup. `deleteDrainCanaryPods` removes old drain canary Deployments.

## Control Flow, State, and Persistence
The reconciler requires a namespace. If no CephCluster exists, it does not requeue. If cluster info is not yet populated, it requeues after five seconds. Feature-disabled clusters return without work. Persistent state is primarily Kubernetes PDBs and the PDB state ConfigMap created in OSD logic; `ClusterMap` is in-memory controller state.

## Dependencies and Integration Points
It integrates CephCluster CRs, child pool/object/filesystem CRs, OSD Ceph CLI state, controller-runtime reconcile API, and operator requeue constants.

## Risks
It chooses the first CephCluster in a namespace, relying on the one-cluster-per-namespace model. `deleteLegacyResources` is a package global, so cleanup runs once per process rather than per namespace. In-memory `ClusterMap` is lost on restart but repopulated by reconciliation.

## Test Signals
The subset tests `ClusterMap` behavior. End-to-end reconcile paths are mostly covered indirectly by OSD and pool helper tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile_test.go

## Purpose
This test file validates the thread-safe `ClusterMap` helper used by the disruption controller to associate namespaces with CephCluster names.

## Important APIs, Types, and Functions
`TestClusterMap` calls `GetClusterInfo`, `UpdateClusterMap`, and `GetClusterNamespaces` on a shared `ClusterMap`.

## Control Flow, State, and Persistence
The test starts with an empty map, asserts missing lookup returns nil, populates three namespaces, validates a retrieved `ClusterInfo` name/namespace, verifies missing namespace lookup, and checks namespace count. State is in-memory only.

## Dependencies and Integration Points
The test uses `cephv1.CephCluster`, Kubernetes `ObjectMeta`, and testify assertions.

## Risks
The test does not exercise concurrent access despite the mutex-backed implementation. `GetClusterNamespaces` order is not asserted, only length, which is appropriate for map-backed data.

## Test Signals
Signals confirm lazy map initialization, namespace-to-cluster mapping, construction of admin cluster info, missing lookup behavior, and namespace enumeration count.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/reconcile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/static_pdb.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/static_pdb.go

## Purpose
`static_pdb.go` provides small helpers to create static PDBs for non-OSD Ceph workloads such as RGW and MDS.

## Important APIs, Types, and Functions
`createStaticPDB` wraps controller-runtime `Create` and annotates errors with the PDB name. `reconcileStaticPDB` gets an existing PDB by `types.NamespacedName`, creates it if missing, and otherwise leaves it unchanged.

## Control Flow, State, and Persistence
The function persists a new Kubernetes `PodDisruptionBudget` only when one does not already exist. Existing PDB state is treated as accepted and is not updated or reconciled to the desired spec.

## Dependencies and Integration Points
It is called by `reconcileCephObjectStore` and `reconcileCephFilesystem` in `pools.go`, using controller-runtime clients and Kubernetes PDB v1 APIs.

## Risks
Because existing PDBs are not updated, changes to object store instance counts, filesystem active counts, selectors, or owner references can leave stale PDB specs until deletion/recreation logic handles only the low-count stale case.

## Test Signals
There is no direct test file for this helper. Pool tests indirectly verify create-if-missing and stale deletion paths in callers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/static_pdb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/context.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/context.go

## Purpose
This file defines the shared context object passed to disruption controllers and a mutex-protected boolean helper.

## Important APIs, Types, and Functions
`Context` carries `ClusterdContext`, `ReconcileCanaries`, and `OpManagerContext`. `LockingBool` stores a boolean plus `sync.Mutex`. `Get` returns the current value under lock, and `Update` sets it under lock.

## Control Flow, State, and Persistence
The state is in-memory only. `LockingBool` serializes concurrent access inside a single operator process and does not persist across restarts.

## Dependencies and Integration Points
`Context` is constructed in the Ceph CR manager and passed to `clusterdisruption.Add` and its reconciler. `ClusterdContext` provides Kubernetes and Ceph execution dependencies; `OpManagerContext` carries cancellation from the manager.

## Risks
`LockingBool` is simple and safe for process-local coordination, but it is not a distributed lock. Any behavior depending on it must tolerate operator restarts and multiple manager instances being prevented by higher-level leader election or deployment assumptions.

## Test Signals
No direct tests are in this subset. Useful tests would exercise concurrent `Get`/`Update` under race detection if this boolean controls future reconciliation gates.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration.go -->
# sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration.go

## Purpose
`toleration.go` implements a deterministic set abstraction for Kubernetes tolerations.

## Important APIs, Types, and Functions
`TolerationSet` stores tolerations in a map keyed by `getKey`, which concatenates key, operator, effect, and value. `Add` initializes the map if needed and stores/replaces by key. `ToList` returns all tolerations sorted by the same key for stable output.

## Control Flow, State, and Persistence
State is in-memory. Adding the same logical toleration overwrites the existing entry, and `ToList` creates a sorted slice without mutating Kubernetes objects directly.

## Dependencies and Integration Points
It depends on `corev1.Toleration` and is intended for disruption/controller configuration paths that need stable toleration lists for pod specs or controller options.

## Risks
The key excludes `TolerationSeconds`, so two tolerations that differ only by duration collide and the later one wins. `ToList` on a zero-value set returns an empty slice, which is safe. There is no locking, so callers should not mutate one set concurrently.

## Test Signals
No direct tests are in this subset. Good signals would cover duplicate elimination, deterministic ordering, and the `TolerationSeconds` collision behavior if duration-sensitive tolerations are expected.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration.go -->
