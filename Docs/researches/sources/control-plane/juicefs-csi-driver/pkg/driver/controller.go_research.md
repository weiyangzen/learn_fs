# sources/control-plane/juicefs-csi-driver/pkg/driver/controller.go

## Purpose
This file implements the CSI Controller service for JuiceFS: volume creation/deletion, capability validation, snapshots, and controller-side quota expansion.

## Important APIs, Types, And Functions
It defines supported `volumeCaps` and `controllerCaps`, `controllerService`, `newControllerService`, `setQuotaInController`, `CreateVolume`, `DeleteVolume`, `ControllerGetCapabilities`, `GetCapacity`, `ListVolumes`, `ValidateVolumeCapabilities`, `isValidVolumeCapabilities`, `CreateSnapshot`, `DeleteSnapshot`, `ListSnapshots`, `ControllerExpandVolume`, and unimplemented publish/get/modify methods.

## Control Flow
`CreateVolume` validates name/capabilities, rejects unsupported block/readonly dynamic modes, parses snapshot restore source when present, records requested capacity in an in-memory map, copies parameters into volume context, optionally starts asynchronous controller quota setting through a dispatch pool, and returns CSI volume context with `subPath` and `capacity`. Snapshot restore is invoked before quota setup when requested. `DeleteVolume` validates volume ID, ignores non-dynamic PVs or empty secrets, serializes deletes with `VolumeLocks`, calls `JfsDeleteVol`, and removes the in-memory volume record. `ValidateVolumeCapabilities` checks the in-memory volume map and confirms supported capabilities. Snapshot methods call JuiceFS create/delete snapshot operations and encode/decode snapshot handles. `ControllerExpandVolume` validates quota config and capacity range, resolves subpath, and calls `setQuotaInController`.

## State And Persistence
Process-local state includes `vols` capacity map, `volLocks`, and a quota worker pool. Persistent effects occur in the JuiceFS backend: creating/restoring/deleting subdirectories, setting quotas, and creating/deleting snapshots. CSI response volume context persists in Kubernetes PV metadata through the external provisioner.

## Dependencies And Integration Points
It depends on CSI protobuf APIs, gRPC status codes, JuiceFS provider interface, `k8sclient`, global config, utility functions for dynamic PV/snapshot/subdir parsing, resource volume locks, and dispatch pools. It is exposed through the driver server as the CSI Controller service.

## Risks
The `vols` map is process-local, so `ValidateVolumeCapabilities` can return NotFound after controller restart even for existing volumes. Controller quota setting in `CreateVolume` runs asynchronously and logs errors without failing volume creation. `CreateVolume` records capacity before later errors and does not always roll back the map on failure. Snapshot and restore operations rely on secrets and backend behavior without PV context loading. Several CSI capabilities are advertised while list/get/publish methods remain unimplemented, though advertised caps exclude those unimplemented paths.

## Test Signals
This subset does not include `controller_test.go`, but that file exists nearby. Key tests should cover capability validation, readonly rejection, async quota flagging, dynamic PV delete checks, process-local map behavior, snapshot handle parsing, and expansion quota calls.
