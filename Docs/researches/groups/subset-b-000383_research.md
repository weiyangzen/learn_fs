# subset-b-000383 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/groupsnapshot_update_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/groupsnapshot_update_test.go

## Purpose
This test file exercises update-time reconciliation for `VolumeGroupSnapshot` objects in the common snapshot controller. It focuses on already-created pre-provisioned and dynamically-provisioned group snapshots, especially the transition from not-ready to ready based on `VolumeGroupSnapshotContent` status.

## Important APIs, Types, And Functions
The only exported test entry is `TestUpdateGroupSnapshotSync`. It builds `controllerTest` fixtures with helper constructors such as `newGroupSnapshotArray`, `newGroupSnapshotContentArray`, `withGroupSnapshotFinalizers`, `withClaimLabels`, and `newVolumeCoupleArray`, then runs them through `runSyncTests` with `testSyncGroupSnapshot`. It relies on shared test constants like `classGold`, `deletionPolicy`, `False`, and `True`.

## Control Flow
Each table entry seeds initial group snapshots, group contents, PVCs, and PVs, invokes one group snapshot sync, then compares expected API state. Case `4-1` verifies a pre-provisioned group snapshot that is bound but not ready stays unchanged. Case `4-2` does the same for a dynamic group snapshot with a selector and bound content. Case `4-3` changes only the content readiness and expects the group snapshot `ReadyToUse` status to become true.

## State And Persistence Behavior
The tests model persisted Kubernetes CR state through fake client/reactor state. They validate status propagation from `VolumeGroupSnapshotContent.Status.ReadyToUse` into `VolumeGroupSnapshot.Status.ReadyToUse` while preserving finalizers and content specs. They also model label-selected PVC/PV sets that back dynamic group snapshot membership.

## Dependencies And Integration Points
This file depends on the common controller test framework and on group snapshot CRD types indirectly through helper constructors. It integrates group snapshot reconciliation with ordinary Kubernetes PVC/PV fixtures, because dynamic group snapshot contents are derived from selected claims and volumes.

## Risks
Coverage is focused and narrow: it validates no-op and readiness propagation, but does not cover group snapshot deletion, missing group content, ownership propagation to individual snapshots, class defaulting, or sidecar CSI calls. Since helper functions hide much of the setup, regressions in helper semantics could make these tests less transparent.

## Test Signals
The strongest signal is that readiness is driven by content status and does not mutate unrelated fields. The file also asserts that bound finalizers are preserved during update paths.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/groupsnapshot_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller.go

## Purpose
This is the core `VolumeSnapshot` reconciliation implementation for the common controller. It maintains the bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent`, creates dynamic content from PVC/PV input, reconciles pre-provisioned content, propagates content status to snapshot status, coordinates deletion and finalizers, protects source PVCs, and records operation metrics.

## Important APIs, Types, And Functions
Key reconciliation entry points are `syncSnapshot(ctx, snapshot)` and `syncContent(content)`. Snapshot deletion is handled by `processSnapshotWithDeletionTimestamp` and `checkandRemoveSnapshotFinalizersAndCheckandDeleteContent`. Creation/update helpers include `syncUnreadySnapshot`, `syncReadySnapshot`, `createSnapshotContent`, `getCreateSnapshotInput`, `checkandBindSnapshotContent`, `bindandUpdateVolumeSnapshot`, `needsUpdateSnapshotStatus`, and `updateSnapshotStatus`. Class and source lookup helpers include `SetDefaultSnapshotClass`, `getSnapshotClass`, `getSnapshotDriverName`, `getClaimFromVolumeSnapshot`, `getVolumeFromVolumeSnapshot`, `pvDriverFromSnapshot`, and `getManagedByNode`. Persistence helpers update informer-backed stores via `storeSnapshotUpdate` and `storeContentUpdate`. `controllerUpdateError` wraps API update failures in a consistent message.

## Control Flow
`syncSnapshot` first removes stale PVC finalizers when possible, handles deletion timestamps, validates exactly one snapshot source, ensures snapshot finalizers, and then dispatches to `syncUnreadySnapshot` or `syncReadySnapshot`. `syncUnreadySnapshot` starts create metrics, reconciles pre-provisioned content, handles group snapshot members with existing content, or creates dynamic content from a bound PVC and CSI PV. `syncReadySnapshot` verifies the bound content still exists and points back to the snapshot, then adds group owner references when needed. `syncContent` validates content source shape, adds a content finalizer, queues snapshot status updates when content status changes, and marks content with the deletion annotation when the bound snapshot is being deleted.

## State And Persistence Behavior
The controller persists Kubernetes API mutations through typed snapshot clients and then mirrors successful objects into local stores. Dynamic content names are deterministic from snapshot UID, so retries can reuse already-created content. Status updates copy creation time, restore size, ready state, errors, bound content name, and group snapshot name from content to snapshot. Finalizer state spans three resources: source PVCs get `PVCFinalizer`, snapshots get source/bound/group finalizers, and contents get a content finalizer. Deletion sets `AnnVolumeSnapshotBeingDeleted` on content, optionally deletes content when its policy is `Delete`, and only removes the snapshot bound finalizer when content deletion no longer needs to block the snapshot.

## Dependencies And Integration Points
The file depends on Kubernetes core API types, client-go retries/listers, snapshot CRD clients, snapshot utilities, feature-adjacent group snapshot listers, and `pkg/metrics`. It integrates with sidecar behavior through `VolumeSnapshotContent` status and deletion annotations rather than direct CSI calls. It also integrates with distributed snapshotting by labeling content with a matching node from PV node affinity, and with prevent-volume-mode-conversion by persisting source volume mode into content.

## Risks
The code intentionally manages transactionless bidirectional binding and has many race-sensitive branches. Important risks are stale informer state, API conflict retries outside some update paths, nil status/source fields, data loss if orphan content is deleted incorrectly, and missed cleanup if PVC finalizers or bound finalizers are removed in the wrong order. `updateSnapshotStatus` compares error time pointers in a way that may not express timestamp equality clearly. Group snapshot membership adds another deletion guard: individual snapshots cannot be deleted while their parent group exists.

## Test Signals
The companion tests cover dynamic creation, static binding, status rebuilds, deletion policies, pending restore PVC blocking, finalizers, class defaulting, API error injection, and content deletion annotations. They provide strong regression coverage for the main state machine, though concurrent HA interleavings remain primarily protected by the design and deterministic naming rather than direct race tests.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_base.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_base.go

## Purpose
This file wires the common snapshot controller together: clients, informers, listers, local stores, rate-limited workqueues, worker loops, cache initialization, and feature-gated group snapshot queues. It is the operational shell around the reconciliation methods implemented in snapshot and group snapshot controller files.

## Important APIs, Types, And Functions
The central type is `csiSnapshotCommonController`, which holds snapshot CRD clients, Kubernetes clients, event recorder, workqueues, listers, synced functions, local stores, metrics manager, feature flags, and indexers. `NewCSISnapshotCommonController` constructs the controller and installs informer handlers/indexers. `Run` waits for caches, initializes local stores, and starts workers. Queue and worker functions include `enqueueSnapshotWork`, `enqueueContentWork`, `snapshotWorker`, `contentWorker`, `syncSnapshotByKey`, `syncContentByKey`, plus group counterparts. Update/delete dispatchers include `updateSnapshot`, `updateContent`, `deleteSnapshot`, `deleteContent`, `updateGroupSnapshotContent`, and `deleteGroupSnapshotContent`.

## Control Flow
Informers enqueue add/update/delete events with meta keys. Workers pop keys, call `sync*ByKey`, requeue with rate limiting on errors, and forget keys on success. `syncSnapshotByKey` fetches the snapshot from the lister, applies class defaulting or lookup through `checkAndUpdateSnapshotClass`, then calls `updateSnapshot`; if the lister reports not found, it uses the local store to process deletion. Content and group content flows mirror this pattern. `Run` conditionally tracks goroutines in a wait group when `ReleaseLeaderElectionOnExit` is enabled.

## State And Persistence Behavior
The controller maintains separate informer/lister state and local `cache.Store` state. Local stores are used to suppress stale resource versions and to retain deleted objects long enough for delete-event processing. Delete handlers remove objects from local stores and enqueue the opposite side of the binding so snapshots and contents do not wait for periodic resync. Group queues/stores are created only when `enableVolumeGroupSnapshots` is true.

## Dependencies And Integration Points
This file integrates client-go informers/workqueues, Kubernetes event recording, snapshot/group snapshot generated clients and listers, `pkg/features`, `pkg/metrics`, and utility index keys. It also installs PV indexing by CSI driver/handle and snapshot indexing by parent group for later lookup paths.

## Risks
The most notable risk is cache initialization in the group-snapshot block: it calls `ctrl.snapshotLister.List` and `ctrl.contentLister.List` while storing into group snapshot stores, which appears type-inconsistent and should be reviewed against actual build/test coverage. Worker shutdown behavior depends on the feature gate for wait group tracking; without it, goroutines are started without `wg`. All workers rely on correct resource-version comparisons in utility store updates to avoid stale event processing.

## Test Signals
`snapshot_controller_test.go` directly tests store version behavior and node-affinity lookup. Most queue wiring is indirectly exercised by the broader controller test framework, but informer event registration and shutdown behavior are not deeply unit-tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_base.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_test.go

## Purpose
This file contains focused unit tests for controller cache update semantics and distributed snapshotting node selection. It verifies low-level helpers that the broader controller state machine depends on.

## Important APIs, Types, And Functions
`FakeNodeLister` implements enough of `corelisters.NodeLister` for node-affinity tests. `storeVersion` is a test helper that creates a `VolumeSnapshotContent`, sets a resource version, calls `utils.StoreObjectUpdate`, and checks whether the cache accepted or rejected the update. Test entry points are `TestControllerCache`, `TestControllerCacheParsingError`, and `TestGetManagedByNode`.

## Control Flow
`TestControllerCache` inserts resource versions in increasing, duplicate, stale, and string-order-tricky sequences to prove the store compares versions numerically. `TestControllerCacheParsingError` seeds a valid object and then attempts to store a non-numeric resource version, expecting an error. `TestGetManagedByNode` creates nodes and a PV node affinity selector, then checks that `getManagedByNode` returns the matching node name or an empty string when no node matches.

## State And Persistence Behavior
The cache tests validate in-memory `cache.Store` behavior rather than API persistence. The state being protected is the controller's local view of objects: stale events should not roll back newer cached objects, and invalid resource versions should surface errors. The node test models no persistence and only checks deterministic lookup.

## Dependencies And Integration Points
The file depends on snapshot test constructors, `utils.StoreObjectUpdate`, Kubernetes `cache.Store`, node labels/selectors, and the controller method `getManagedByNode`. It supports the distributed snapshotting integration path where dynamic `VolumeSnapshotContent` may be labeled with `VolumeSnapshotContentManagedByLabel`.

## Risks
The cache tests operate on `VolumeSnapshotContent` only, but the same utility is used for snapshots and group objects. `FakeNodeLister.Get` is a stub, so only list-based matching is covered. The no-match path expects no error and empty node, which matches current controller behavior but may hide cluster configuration problems.

## Test Signals
The file gives strong signal for numeric resource-version ordering and parsing failures. It also confirms node affinity matching uses Kubernetes selector semantics via the controller method.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_create_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_create_test.go

## Purpose
This test file validates dynamic `VolumeSnapshotContent` creation from `VolumeSnapshot` objects. It covers successful content creation, secret annotation propagation, and many failure paths before or during content/status updates.

## Important APIs, Types, And Functions
The main entry is `TestCreateSnapshotSync`. It uses `controllerTest` tables run through `runSyncTests` and usually invokes `testSyncSnapshot`. Shared fixtures include `newSnapshotArray`, `newContentArrayNoStatus`, `newClaimArray`, `newVolumeArray`, `withContentAnnotations`, and reactor error injection through `reactorError`.

## Control Flow
Each test seeds initial snapshots, claims, volumes, classes, optional secrets, and expected objects. Success cases create a deterministic `snapcontent-<snapshotUID>` object and update snapshot status with the bound content name. Failure cases cover nonexistent classes, missing class names, missing PVCs, missing PVs, unbound PVCs, PVC finalizer update failures, snapshot status update failures, invalid secret parameters, and content create API failures.

## State And Persistence Behavior
The expected state demonstrates that creation is multi-step: add or verify PVC finalizer, resolve class/PV/secret, create `VolumeSnapshotContent`, update snapshot status, and record events/errors when steps fail. Secret references are persisted as deletion secret annotations on content. When content creation succeeds but status update fails, the test expects content to exist while snapshot status may remain unbound, matching retry-oriented controller behavior.

## Dependencies And Integration Points
The file integrates the controller with snapshot classes, Kubernetes PVC/PV binding, CSI volume handles, snapshotter secret parameter parsing, fake client reactors, and event recording. It indirectly tests `createSnapshotContent`, `getCreateSnapshotInput`, `ensurePVCFinalizer`, and `updateSnapshotStatus`.

## Risks
Creation has several partial-success states. The tests show content can be created even when later snapshot status updates fail, so idempotent retry and deterministic naming are critical. Secret parameter validation is covered, but credential lookup details live in utility code. Distributed snapshotting and source volume mode conversion are not explicitly exercised here.

## Test Signals
The table covers both happy path and high-value error paths, with expected events such as `SnapshotContentCreationFailed` and `CreateSnapshotContentFailed`. It is a strong regression suite for dynamic snapshot creation preconditions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_delete_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_delete_test.go

## Purpose
This file validates deletion reconciliation for `VolumeSnapshot` and `VolumeSnapshotContent`, including dynamic and static snapshots, delete versus retain policies, API failures, misbinding, and restore-in-progress blocking.

## Important APIs, Types, And Functions
The main test is `TestDeleteSync`. It defines reusable snapshot class parameter maps and `snapshotClasses`, then runs table entries through `runSyncTests`. Test calls include `testSyncContent`, `testSyncSnapshot`, and `testSyncSnapshotError`, sometimes wrapped by `wrapTestWithInjectedOperation` to mutate reactor state during reconciliation.

## Control Flow
The table first verifies content-side no-ops and already-deleted content. It then exercises snapshot deletion with pending restore PVCs, dynamic content deletion, content delete API failure, retain policy, missing content, mismatched content UID/name, and parallel static cases. For delete policy, expected content is removed and snapshot retains the bound finalizer until content deletion completes. For retain policy or no/misbound content, snapshot finalizers can be removed while content is retained or ignored.

## State And Persistence Behavior
Deletion persists `AnnVolumeSnapshotBeingDeleted` on content before deletion decisions. A `Delete` policy leads to `VolumeSnapshotContent` API deletion and retention of the snapshot bound finalizer. A `Retain` policy keeps content but annotates it and removes snapshot finalizers. Pending restore PVCs keep the snapshot from deletion and produce a retryable error. Tests verify finalizer state, object existence, and warning events.

## Dependencies And Integration Points
The file depends on snapshot class fixtures, PVC restore data source helpers, fake client reactors, and event validation. It directly exercises integration between snapshot deletion, content deletion policy, PVC restore safety, and sidecar-triggering annotations.

## Risks
Deletion is data-loss-sensitive. The tests highlight why content is not deleted when binding is ambiguous and why restore PVCs block deletion. There is still limited direct coverage for group snapshot membership deletion guards in this file; those are implemented in the main controller and covered elsewhere.

## Test Signals
Important expected events include `SnapshotDeletePending` and `SnapshotContentObjectDeleteError`. The tests strongly validate idempotent deletion and safe behavior under missing/misbound content.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_finalizer_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_finalizer_test.go

## Purpose
This file isolates finalizer helper behavior for PVCs and snapshots. It verifies that protection finalizers are added and removed only when controller state says they are needed.

## Important APIs, Types, And Functions
`TestSnapshotFinalizer` is the sole test function. It uses `controllerTest` fixtures and calls helper test adapters: `testAddPVCFinalizer`, `testRemovePVCFinalizer`, `testAddSnapshotFinalizer`, `testAddSingleSnapshotFinalizer`, and `testRemoveSnapshotFinalizer`.

## Control Flow
The table covers adding a PVC finalizer, skipping add when already present, removing a PVC finalizer, skipping remove when absent, refusing to remove while PVC remains in use, adding snapshot finalizers from an empty finalizer list, patching a single snapshot finalizer when another already exists, and removing snapshot finalizers.

## State And Persistence Behavior
The tests model finalizers as persisted metadata on PVC and `VolumeSnapshot` API objects. They validate both update-style behavior when no finalizers exist and patch-style behavior when appending to an existing finalizer list. PVC finalizer removal depends on usage checks across snapshots in the namespace.

## Dependencies And Integration Points
The file integrates with utility finalizer constants such as `VolumeSnapshotBoundFinalizer` and the shared test framework. It indirectly covers `ensurePVCFinalizer`, `checkandRemovePVCFinalizer`, `addSnapshotFinalizer`, and `removeSnapshotFinalizer`.

## Risks
Finalizer operations are ordering-sensitive: removing snapshot finalizers before PVC finalizers can strand PVCs, while removing PVC finalizers too early can allow source mutation during snapshot creation. The file does not exhaustively test API failure injection for every finalizer branch; those appear in create/update/delete tests.

## Test Signals
The file gives concise, high-signal coverage for idempotency and expected success/no-op outcomes in finalizer helpers.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_finalizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_update_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_update_test.go

## Purpose
This is the broadest snapshot reconciliation test file. It validates sync behavior for bound/unbound, ready/unready, dynamic/static, content-driven status updates, content finalizer additions, deletion annotation propagation, error status propagation, and recreation of missing content.

## Important APIs, Types, And Functions
`TestSync` defines one large `controllerTest` table. It uses helper constructors for snapshots, contents, claims, volumes, secrets, errors, annotations, and restore sizes. Test adapters include `testSyncSnapshot`, `testSyncSnapshotError`, `testSyncContent`, `testSyncContentError`, `testUpdateSnapshotErrorStatus`, and `testNewSnapshotContentCreation`.

## Control Flow
The test table covers missing content, misbound static and dynamic content, successful binding, no-op ready states, status rebuilds from content fields, API update failures, dynamic-vs-static content mismatch, adding content finalizers, marking content when snapshots are being deleted, propagating content errors into snapshot status, clearing snapshot errors, and creating new content when snapshot status is nil or stale.

## State And Persistence Behavior
Expected objects show how `VolumeSnapshot.Status` is rebuilt from `VolumeSnapshotContent.Status`: bound content name, ready state, creation time, restore size, and error. They also show how content metadata is changed by finalizer addition and deletion annotations. The file validates partial failure behavior where in-memory annotations may appear in expected reactor objects even when API update fails.

## Dependencies And Integration Points
The file integrates most of the common controller stack: snapshot/content listers, fake client reactors, snapshot classes, Kubernetes PVC/PV state, events, secrets, content statuses, and utility constants. It provides indirect coverage for `syncSnapshot`, `syncContent`, `syncReadySnapshot`, `syncUnreadySnapshot`, `updateSnapshotStatus`, and `addContentFinalizer`.

## Risks
Because this file is large and table-driven, understanding a failed case often requires tracing helper defaults in `framework_test.go`. Some cases intentionally set content status changes through reactor behavior, so the initial and expected content can differ in ways not obvious from one row. Still, the breadth is valuable for preventing regressions in the multi-step state machine.

## Test Signals
Expected warning events include `SnapshotContentMissing`, `SnapshotContentMisbound`, `SnapshotFinalizerError`, `SnapshotContentMismatch`, and `SnapshotContentCreationFailed`. The file is a strong signal for idempotence, status propagation, and safe handling of bad bindings.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshot_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshotclass_test.go -->
# sources/control-plane/external-snapshotter/pkg/common-controller/snapshotclass_test.go

## Purpose
This file tests `VolumeSnapshotClass` lookup and defaulting behavior before snapshot reconciliation proceeds. It verifies both explicit class names and automatic default class assignment.

## Important APIs, Types, And Functions
`TestUpdateSnapshotClass` defines table-driven `controllerTest` rows and runs them with `runUpdateSnapshotClassTests`. The test path targets `checkAndUpdateSnapshotClass` and `SetDefaultSnapshotClass`. Fixtures use PVC/PV pairs whose storage class and CSI driver influence default class selection.

## Control Flow
Case `1-1` starts with no class name and expects the controller to patch the default class matching the source PV driver. Case `1-2` verifies a pre-set class remains unchanged. Case `1-3` verifies a missing explicit class records an error and event. Case `1-5` verifies defaulting fails when the source PVC cannot be found.

## State And Persistence Behavior
Defaulting persists by patching `snapshot.Spec.VolumeSnapshotClassName` and updating the controller's local store. Failure paths persist error status on the snapshot with warnings such as `GetSnapshotClassFailed` or `SetDefaultSnapshotClassFailed`.

## Dependencies And Integration Points
The file depends on global `snapshotClasses`, Kubernetes PVC/PV fixtures, and the shared test framework. It integrates class defaulting with `pvDriverFromSnapshot`, which means default class selection depends on a valid PVC/PV binding and CSI driver match.

## Risks
The file covers missing class and missing PVC, but not multiple default classes, non-CSI PVs, or pre-provisioned snapshots where class lookup can be skipped. Multiple defaults are an important production risk because the controller refuses ambiguous defaulting.

## Test Signals
The expected state and events confirm that class errors are visible to users and that defaulting mutates spec only when prerequisites are satisfied.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/common-controller/snapshotclass_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/features/features.go -->
# sources/control-plane/external-snapshotter/pkg/features/features.go

## Purpose
This file declares external-snapshotter feature gates and registers their default specs with Kubernetes' global mutable feature gate.

## Important APIs, Types, And Functions
It defines two `featuregate.Feature` constants: `VolumeGroupSnapshot` (`CSIVolumeGroupSnapshot`) and `ReleaseLeaderElectionOnExit`. The `init` function calls `feature.DefaultMutableFeatureGate.Add(defaultKubernetesFeatureGates)`. The `defaultKubernetesFeatureGates` map sets `VolumeGroupSnapshot` to Beta/default false and `ReleaseLeaderElectionOnExit` to Alpha/default false.

## Control Flow
There is no runtime branching beyond package initialization. Importing the package registers the feature specs with the shared feature gate. Other packages query `utilfeature.DefaultFeatureGate.Enabled(...)` to decide behavior, such as group snapshot support or worker wait group shutdown handling.

## State And Persistence Behavior
The only state change is process-local registration in the default feature gate. No Kubernetes API objects or files are persisted by this package.

## Dependencies And Integration Points
The file depends on `k8s.io/apiserver/pkg/util/feature` and `k8s.io/component-base/featuregate`. `snapshot_controller_base.go` uses `ReleaseLeaderElectionOnExit`, and the controller construction path accepts explicit group snapshot enablement that is conceptually tied to `VolumeGroupSnapshot`.

## Risks
Feature gate registration occurs in `init`, so missing imports can silently prevent feature availability. Both features default to false, so deployments must opt in where needed. Changing default or prerelease state is a compatibility-sensitive API decision.

## Test Signals
No tests are in this file. Behavior is indirectly tested by controller paths that query feature gates or pass group snapshot enablement.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/features/features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter.go -->
# sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter.go

## Purpose
This package is the CSI RPC adapter for volume group snapshot operations. It exposes a small `GroupSnapshotter` interface that the sidecar/controller code can use without handling raw CSI generated clients directly.

## Important APIs, Types, And Functions
`GroupSnapshotter` defines `CreateGroupSnapshot`, `DeleteGroupSnapshot`, and `GetGroupSnapshotStatus`. `NewGroupSnapshotter(conn)` returns a `groupSnapshot` backed by a gRPC connection. `CreateGroupSnapshot` calls CSI Identity through `csirpc.GetDriverName`, then sends `CreateVolumeGroupSnapshotRequest`. `DeleteGroupSnapshot` sends `DeleteVolumeGroupSnapshotRequest`. `GetGroupSnapshotStatus` sends `GetVolumeGroupSnapshotRequest`.

## Control Flow
Each method constructs a `csi.GroupControllerClient` from the stored connection. Create first resolves the driver name and returns early on identity error, then sends source volume IDs, parameters, and secrets to CSI. It returns driver name, group snapshot ID, per-volume snapshots, creation time converted from protobuf timestamp, ready flag, and error. Delete and status calls pass group snapshot ID, individual snapshot IDs, and credentials directly to the CSI driver.

## State And Persistence Behavior
The adapter is stateless except for the gRPC connection. It does not cache driver names or snapshots and does not persist Kubernetes objects. All authoritative state comes from CSI responses and is returned to callers.

## Dependencies And Integration Points
The file depends on CSI generated Go types, `csi-lib-utils/rpc` for driver identity, gRPC, and klog. It integrates external-snapshotter group logic with CSI `GroupController` service methods.

## Risks
The implementation assumes CSI responses include non-nil `GroupSnapshot` and `CreationTime`; a nil response field could panic. It also fetches driver name on every create, which is simple but adds a dependency on Identity service availability for create operations. Context timeouts/cancellation are delegated to callers.

## Test Signals
`group_snapshotter_test.go` uses an in-process fake CSI server to cover success and RPC error paths for all methods, including custom timestamps and status codes.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter_test.go -->
# sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter_test.go

## Purpose
This file tests the CSI group snapshot RPC adapter against an in-process fake CSI server. It verifies request/response plumbing, driver name lookup, timestamp conversion, ready flags, and error propagation.

## Important APIs, Types, And Functions
`fakeCSIServer` implements CSI Identity and GroupController server methods. `startFakeCSI` opens a local TCP listener, registers the fake services, dials with insecure credentials, and returns a cleanup function. Tests include `TestNewGroupSnapshotter`, create success/error/custom response cases, delete success/error cases, and get-status success/custom/error cases.

## Control Flow
Each test starts a fake CSI server configured with default behavior or injected errors/responses, creates a `GroupSnapshotter`, calls one method, and asserts returned fields or gRPC status codes. Create tests cover identity failure before create RPC, create RPC internal error, default success, and custom response. Delete tests verify nil error and NotFound propagation. Status tests verify default ready response, custom not-ready response, and error returning false plus zero time.

## State And Persistence Behavior
State is entirely in-memory within `fakeCSIServer`. The fake stores configured responses/errors and returns deterministic timestamps. No Kubernetes state is involved.

## Dependencies And Integration Points
The file uses CSI generated services, gRPC server/client APIs, `status`/`codes`, protobuf timestamps, and Go's net listener. It is a direct integration-style unit test for `group_snapshotter.go`.

## Risks
The fake server does not assert request contents, so incorrect parameter, secret, or ID forwarding might go unnoticed unless return behavior depends on request fields. It also does not test nil `GroupSnapshot` responses or context deadline behavior.

## Test Signals
The file gives strong signal that normal RPC paths work and errors are not swallowed. It also confirms creation/status timestamps are converted to `time.Time`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/metrics/metrics.go -->
# sources/control-plane/external-snapshotter/pkg/metrics/metrics.go

## Purpose
This file implements Prometheus/Kubernetes metrics for snapshot controller operations. It tracks operation start times, emits latency histograms, tracks operations in flight, and supports cancellation metrics when deletes terminate unfinished creates.

## Important APIs, Types, And Functions
Public constants name operations (`CreateSnapshot`, `CreateSnapshotAndReady`, `DeleteSnapshot`), snapshot provision types (`dynamic`, `pre-provisioned`), and status types (`unknown`, `success`, `cancel`). `MetricsManager` exposes `PrepareMetricsPath`, `OperationStart`, `DropOperation`, `RecordMetrics`, `RecordVolumeGroupSnapshotMetrics`, and `GetRegistry`. `OperationKey` identifies an operation by name and resource UID; `OperationValue` stores driver, snapshot type, and start time. `NewMetricsManager` creates an `operationMetricsManager`; `NewOperationKey`, `NewOperationValue`, and `NewSnapshotOperationStatus` are constructors.

## Control Flow
`OperationStart` records a start time only if the key is not already cached, making starts idempotent. `RecordMetrics` returns if no start exists, computes duration, resolves unknown driver names from the cached value, observes the histogram, handles delete-triggered cancel metrics for pending create operations, removes cached entries, and updates the in-flight gauge. `DropOperation` removes cached state without histogram emission. `PrepareMetricsPath` attaches the registry to an HTTP mux.

## State And Persistence Behavior
The manager's only state is an in-memory map protected by a mutex plus Prometheus registry objects. It periodically resets `operations_in_flight` from cache length. There is no persisted state; process restart loses pending operation starts.

## Dependencies And Integration Points
The file depends on Kubernetes component-base metrics, Prometheus `promhttp`, Kubernetes UIDs, HTTP muxes, and `time`. The snapshot controller records create/delete metrics through this interface during status and deletion transitions.

## Risks
`init` starts a goroutine with a context canceled by deferred `cancel`, so the scheduled in-flight refresh likely exits immediately after initialization; the gauge is still updated on start/finish operations, but leak correction may not run. Metrics are process-local and depend on every operation path correctly calling start and record/drop. Missing driver names fall back to `"unknown"` or cached driver names.

## Test Signals
Separate metrics tests in the package cover manager creation, non-existing operation handling, recording, unknown status, concurrency, in-flight gauge, process start time, and group snapshot metrics. This file itself has no tests but is well-covered by adjacent tests.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/metrics/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/metrics/metrics_group.go -->
# sources/control-plane/external-snapshotter/pkg/metrics/metrics_group.go

## Purpose
This file extends the snapshot metrics manager with group snapshot operation names and recording behavior. It mirrors single-snapshot metric semantics for `VolumeGroupSnapshot` workflows.

## Important APIs, Types, And Functions
It defines `CreateGroupSnapshotOperationName`, `CreateGroupSnapshotAndReadyOperationName`, `DeleteGroupSnapshotOperationName`, `DynamicGroupSnapshotType`, and `PreProvisionedGroupSnapshotType`. The main function is `RecordVolumeGroupSnapshotMetrics`, a method on `operationMetricsManager` exposed through `MetricsManager`.

## Control Flow
`RecordVolumeGroupSnapshotMetrics` locks the metrics cache, returns if the operation was not started, resolves status and driver name, observes operation duration in the shared latency histogram, handles delete-triggered cancellation for pending group create and create-and-ready operations, deletes the completed operation key, and updates the in-flight gauge.

## State And Persistence Behavior
It uses the same in-memory `operationMetricsManager.cache` as snapshot metrics. Group snapshot operations are distinguished only by operation name and resource UID. No state is persisted beyond Prometheus metric samples.

## Dependencies And Integration Points
The file depends on `time` and the types/constants from `metrics.go`. It integrates group snapshot controller code with the same metric labels used for ordinary snapshot operations: driver name, operation name, snapshot type, and operation status.

## Risks
The implementation intentionally duplicates `RecordMetrics` logic; future changes to single-snapshot metric behavior must be mirrored here to avoid semantic drift. It shares the same reliance on correct `OperationStart` calls and the same in-flight gauge behavior.

## Test Signals
Metrics package tests include group snapshot recording and pre-provisioned group snapshot cases. These tests confirm the group operation names emit through the common histogram path.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/metrics/metrics_group.go -->
