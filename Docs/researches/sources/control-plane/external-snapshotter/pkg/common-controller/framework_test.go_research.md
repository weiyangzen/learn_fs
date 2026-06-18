# sources/control-plane/external-snapshotter/pkg/common-controller/framework_test.go

## Purpose

This file is the shared unit-test harness for the CSI snapshot common controller. It builds a fake controller environment, models API-server persistence with a custom `snapshotReactor`, constructs Kubernetes snapshot, group snapshot, PVC, PV, class, and secret objects, and provides reusable runner functions used by both legacy VolumeSnapshot tests and newer VolumeGroupSnapshot tests.

## Important APIs, Types, And Functions

- `controllerTest` is the central test-case struct. It carries initial and expected normal snapshot objects, group snapshot objects, PVs, PVCs, secrets, expected event prefixes, injected fake API errors, and a `testCall`.
- `testCall` is the function signature for invoking a controller path under test, such as `testSyncSnapshot`, `testSyncGroupSnapshot`, or `testSyncGroupSnapshotContent`.
- `snapshotReactor` is a fake API-server and etcd model. It owns maps for secrets, volumes, claims, snapshot contents, snapshots, snapshot classes, group snapshot contents, group snapshots, and group snapshot classes. It also tracks changed objects and optional injected `reactorError` values.
- `snapshotReactor.React` implements fake-client reactions for creates, updates, patches, gets, lists, and deletes across snapshot, group snapshot, PV, PVC, and secret resources.
- `checkContents`, `checkGroupContents`, `checkSnapshots`, and `checkGroupSnapshots` compare reactor state against expected state after normalizing resource versions and selected timestamps.
- `newTestController` wires `NewCSISnapshotCommonController` with fake informer factories, fake metrics, fake event recorder, always-ready lister sync hooks, and rate limiters.
- Object builders such as `newContent`, `newGroupSnapshotContent`, `newSnapshot`, `newGroupSnapshot`, `newClaim`, `newVolume`, and array helpers keep test setup compact and consistent.
- `runSyncTests`, `runFinalizerTests`, and `runUpdateSnapshotClassTests` populate stores/listers/reactor maps, invoke the requested `testCall`, wait for expected convergence, and evaluate objects and events.

## Control Flow

The main test flow in `runSyncTests` creates fake Kubernetes and snapshot clientsets, constructs the controller, installs the reactor, seeds controller stores and reactor maps with initial objects, installs custom listers for PVCs and snapshot classes, calls the test function, and then waits until the reactor state matches expected objects. The runner then calls `evaluateTestResults`, which performs object comparisons and event checks.

`snapshotReactor.React` is the behavioral center. For create actions it validates non-existence, stores objects, and records changed objects. For `volumesnapshots` creates, it assigns a deterministic UID when the caller does not provide one, which is important for group snapshot fan-out tests that bind `VolumeSnapshotContent.Spec.VolumeSnapshotRef.UID`. For update actions it simulates optimistic concurrency by comparing `ResourceVersion` and returning `errVersionConflict` when stale. For patch actions it applies JSON patches with `evanphx/json-patch`, increments resource versions, and stores the patched object. For get/list/delete it returns or mutates the backing maps.

The object builder helpers encode the controller's expected object shapes: dynamic group contents use `Spec.Source.VolumeHandles`, pre-provisioned group contents use `Spec.Source.GroupSnapshotHandles`, group snapshots can carry a selector or target content name, and finalizer helpers add the same constants used by production utilities.

## State And Persistence Behavior

The fake persisted state lives in `snapshotReactor` maps, while controller cache state is represented by the controller's stores and listers. Tests often seed both so that code using either API clients or local caches sees consistent objects. Resource versions are bumped on update/patch to emulate Kubernetes concurrency. `changedObjects` and `changedSinceLastSync` support pseudo-watch behavior and idle/convergence waits.

The comparison functions intentionally normalize volatile fields: resource versions are cleared, group content `Spec.Source.VolumeHandles` are sorted, and some creation/error timestamps are zeroed. This makes tests assert semantic controller state rather than fake-server implementation detail.

## Dependencies And Integration Points

The framework integrates Kubernetes fake client-go, external-snapshotter fake clientsets, informers/listers, workqueues, JSON patch application, fake event recording, and the repository's `utils` and `metrics` packages. It is the shared test substrate for group snapshot create/delete/finalizer/sync tests and for lower-level helper tests that reuse `newTestController` and `newSnapshotReactor`.

## Risks And Edge Cases

- The reactor has some subtle type-map coupling. For example, update logic for `volumegroupsnapshotcontents` checks `r.contents` in one branch while storing in `r.groupContents`; if exercised with real updates rather than patches/creates this could diverge from intended group-content behavior.
- List support is implemented for normal snapshot resources and PVCs, but not every group snapshot list path, so new tests may need additional reactor cases.
- The framework's fake watch helpers cover normal contents/snapshots but not group snapshot watches, limiting event-loop style tests for group objects.
- The group snapshot builders use specific defaults and may mask missing fields unless a test explicitly varies them.

## Test Signals

This file is itself test infrastructure. Its strongest signal is that many scenario tests can describe only initial and expected objects while relying on the reactor to catch API create/update/patch/delete behavior, event ordering, status writes, and finalizer mutations. It also provides direct error injection with `reactorError` and convergence checking through `waitTest`.
