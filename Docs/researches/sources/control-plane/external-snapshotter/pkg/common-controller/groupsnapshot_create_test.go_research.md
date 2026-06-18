# sources/control-plane/external-snapshotter/pkg/common-controller/groupsnapshot_create_test.go

## Purpose

This file tests create-time `VolumeGroupSnapshot` sync behavior for dynamic and pre-provisioned group snapshots. It defines the reusable `groupSnapshotClasses` fixture and a table-driven `TestCreateGroupSnapshotSync` suite covering happy paths and validation failures.

## Important APIs, Types, And Functions

- `groupSnapshotClasses` defines `classGold`, `defaultClass`, and `classSilver` `VolumeGroupSnapshotClass` objects with drivers, parameters, default annotations, and Delete/Retain policies.
- `TestCreateGroupSnapshotSync` builds `controllerTest` cases and runs them through `runSyncTests`.
- The tests use builders from `framework_test.go`: `newGroupSnapshotArray`, `newGroupSnapshotContentArray`, `newClaimCoupleArray`, `newVolumeCoupleArray`, `withClaimLabels`, `withVolumesLocalPath`, `withVolumesCSIDriverName`, and `newVolumeError`.

## Control Flow

Each test case seeds an initial group snapshot, optional group contents, PVCs, and PVs, then calls `testSyncGroupSnapshot`, which invokes `ctrl.syncGroupSnapshot`. Expected results assert group snapshot status, generated group content, error status, and whether the sync should be considered successful.

Dynamic creation cases verify that a selector over PVC labels resolves bound PVCs, those PVCs resolve PVs, all PVs use the group class driver, and a deterministic `VolumeGroupSnapshotContent` is created with selected volume handles. Error cases stop at the expected validation point and write a group snapshot error status with `ReadyToUse=false`.

Pre-provisioned cases start from `Spec.Source.VolumeGroupSnapshotContentName`. The success path binds status to the named content and reports ready. Failure paths cover missing content, content bound to the wrong group snapshot, and a content object shaped as dynamic when static content was expected.

## State And Persistence Behavior

The expected dynamic success case persists a new `VolumeGroupSnapshotContent` named from the group snapshot UID and volume handles from the two selected PVs. The group snapshot status records `BoundVolumeGroupSnapshotContentName` and `ReadyToUse=false` until the CSI sidecar reports content status. Error cases preserve no content and set `Status.Error.Message` to the production error text. Pre-provisioned success does not create content; it binds the existing content name and mirrors readiness from content status.

## Dependencies And Integration Points

These tests integrate the group snapshot helper with the fake API reactor, class lister, PVC list/get, PV get, utility constants for default classes, and class parameters from the broader test package. They validate the controller contract between `VolumeGroupSnapshot`, `VolumeGroupSnapshotClass`, PVC label selectors, PV CSI sources, and `VolumeGroupSnapshotContent`.

## Risks And Edge Cases

- The scenarios focus on two-PVC groups and do not stress large groups or ordering beyond sorted expected volume handles.
- Secret parameter behavior is mostly inherited from class fixtures and is not the main assertion target in this file.
- The expected errors are string-exact, which catches behavior changes but can make harmless message edits noisy.
- Dynamic creation is tested before CSI sidecar status updates; individual member snapshot fan-out is covered in sync/helper tests instead.

## Test Signals

The file gives strong coverage for initial create validation: missing/nonexistent class, selector matching no PVCs, unbound PVCs, non-CSI PVs, driver mismatch, dynamic content creation, pre-provisioned missing content, wrong back-reference, and static/dynamic content shape mismatch.
