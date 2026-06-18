# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/deviceset_test.go

## Purpose
This file tests `deviceSet.go`, especially idempotent PVC creation for `StorageClassDeviceSet`, naming compatibility, generated PVC labels, storage annotation propagation, and PVC resize checking.

## Important APIs, Types, and Helpers
`TestPrepareDeviceSets` and `testPrepareDeviceSets` validate both blank and explicit volume claim template names. `TestPrepareDeviceSetWithHolesInPVCs` uses a fake PVC reactor to assign generated names, then exercises multi-template data/metadata/wal PVC groups through scale-up, repeat reconcile, missing companion PVC recreation, scale-down, and scale-up with new indexes. `assertPVCExists()` verifies expected generated resources. `testVolumeClaim()` provides minimal templates. `TestPrepareDeviceSetsWithCrushParams` validates `crushDeviceClass`, `crushInitialWeight`, and `crushPrimaryAffinity` annotation extraction. `TestPVCName` covers `deviceSetPVCID()` normalization. `TestCreateValidImageVersionLabel` covers image-label sanitization. `TestCheckAllPvcResize` uses a controller-runtime fake client and status subresource support to validate resize bookkeeping.

## Control Flow Covered
The tests prove that a single unnamed template is treated as data, that generated names include the default or explicit template name, that device set count drives group creation, and that existing labeled PVC indexes are reused before new indexes are allocated. The holes test shows an important behavior: deleting one companion PVC in an existing index causes the missing PVC to be recreated, but reducing the count prevents deleted lower-index PVC groups from being recreated if enough other indexes already satisfy the count. Scaling back up then allocates a higher new index instead of reusing a deleted one.

## State and Persistence Behavior
All state is fake Kubernetes PVC state. Labels are the primary source of identity for `GetExistingPVCs()`. Generated names are simulated by a reactor because the fake client does not automatically behave exactly like the apiserver for this test's purposes. Resize state is represented by an in-memory `pvcResizeMap` and fake PVC spec/status resource quantities.

## Dependencies and Integration Points
The tests depend on Rook's fake clientsets, client-go reactors, controller-runtime fake client, Kubernetes resource quantities, and the CephCluster storage API. They indirectly validate `labels.go` because PVC label keys and image labels are asserted.

## Risks and Gaps
The tests exercise PVC object creation well, but do not run real CSI resize behavior or validate asynchronous wait timeout timing. They do not cover memory validation failure in this file directly, although create tests cover provisioning error paths. The holes test encodes nuanced index behavior that future refactors must preserve to avoid unintended OSD identity reuse.

## Test Signals
This is strong regression coverage for source-tree state alignment between CephCluster storage specs and persistent PVCs. It is especially useful for changes to PVC naming, label keys, generated names, and scale behavior.
