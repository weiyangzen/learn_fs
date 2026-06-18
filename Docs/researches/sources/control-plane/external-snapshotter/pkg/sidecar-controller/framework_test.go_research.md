# sources/control-plane/external-snapshotter/pkg/sidecar-controller/framework_test.go

## Purpose
This file is the shared unit-test framework for sidecar controller snapshot content tests. It simulates a Kubernetes API server, informer state, fake CSI snapshotter, event recorder, object builders, injected API errors, and evaluation helpers so individual tests can describe controller scenarios as `controllerTest` tables.

## Important APIs, Types, And Functions
- `controllerTest` describes initial contents, expected contents, secrets, events, injected API errors, expected CSI create/delete/list calls, a test callback, and expected success/requeue flags.
- `snapshotReactor` is a fake API server/etcd reactor that stores secrets, snapshot classes, contents, changed objects, fake watchers, and one-shot injected errors.
- `reactorError` configures fake client failures by verb/resource.
- `snapshotReactor.React` handles create, update, patch, get, and delete for `volumesnapshotcontents`, plus secret gets. It enforces simple resource-version conflict behavior and applies JSON patches.
- `checkContents`, `checkEvents`, `waitTest`, `syncAll`, and event simulation helpers validate final state and emitted events.
- `newTestController` constructs a `csiSnapshotSideCarController` with fake clients, fake snapshotter, no group snapshotter, short operation timeout, metadata injection enabled, and rate-limiting queues.
- `newContent` and related builders construct `VolumeSnapshotContent` objects with status, source handles, deletion timestamps, finalizers, group snapshot handles, annotations, and binding references.
- `runSyncContentTests` is the main harness loop that assembles fake state, injects classes and secrets, invokes the test callback, checks requeue/error expectations, waits for state, and compares results.
- `fakeSnapshotter` validates exact CSI create/delete/list requests and returns configured responses.

## Control Flow
Tests supply declarative `controllerTest` cases. For each case, `runSyncContentTests` creates fake Kubernetes and external-snapshotter clients, constructs the controller, registers `snapshotReactor` hooks, seeds content store and reactor state for driver-matching content, inserts secrets, builds a class lister from supplied classes, and calls the requested `testCall`. The fake snapshotter checks each CSI call against the next expected call. The reactor records every object mutation and can inject one-shot failures. The harness then waits with exponential backoff until reactor content matches expected content and verifies event prefixes.

## State And Persistence Behavior
All persistence is in-memory simulated API state. `snapshotReactor.contents` is the authoritative fake etcd view of `VolumeSnapshotContent`; updates increment string resource versions; patches are applied with `evanphx/json-patch`; secret and class stores back credential/class lookups. The controller's own `contentStore` models informer cache state. Event state is held in `record.FakeRecorder`. No filesystem or real network state is used.

## Dependencies And Integration Points
This framework integrates with external-snapshotter fake clientsets, informers and listers, Kubernetes fake clients, workqueues, watch fakes, Prometheus-independent controller APIs, `go-cmp` for diffs, and production utility functions for annotations and finalizers. It is the shared dependency for `content_create_test.go` and related sidecar controller tests.

## Risks And Edge Cases
- The reactor only implements the API actions needed by current tests; new controller calls may bypass the fake or fail with unhandled actions.
- Resource-version behavior is simplified but intentionally catches stale update attempts.
- Event verification checks prefixes, not full messages, so message regressions can pass if reason/type prefixes are stable.
- `newTestController` passes a nil group snapshotter, so tests using this harness cannot exercise group snapshot CSI behavior without extending it.
- Some helper comments and error messages refer to snapshots/volumes imprecisely, but behavior is clear from the code.
- `runSyncContentTests` has a duplicated nil-error expectation block; harmless but redundant.

## Test Signals
The framework gives strong signals on controller mutation behavior, CSI request shape, event emission, requeue return values, injected API failures, resource-version conflicts, secret resolution, and object status/finalizer/annotation changes. Its fake snapshotter makes CSI interaction regressions visible through exact argument checks.
