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
