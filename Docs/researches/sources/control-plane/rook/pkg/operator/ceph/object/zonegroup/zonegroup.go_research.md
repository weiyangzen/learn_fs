# sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/zonegroup.go

## Purpose

This helper file provides zonegroup-specific parsing and validation used by the `CephObjectZoneGroup` controller.

## Important APIs, Types, and Functions

- `masterZoneGroupType` models the `master_zonegroup` field from `radosgw-admin period get` JSON.
- `decodeMasterZoneGroup(data string) (string, error)` unmarshals period JSON and returns the master zonegroup ID/name field.
- `validateZoneGroup(u *cephv1.CephObjectZoneGroup) error` validates required CR fields: name, namespace, and `spec.realm`.

## Control Flow

`decodeMasterZoneGroup` unmarshals into a minimal struct and wraps JSON errors. Missing `master_zonegroup` naturally returns an empty string. `validateZoneGroup` performs sequential required-field checks and returns the first missing-field error.

## State and Persistence Behavior

The file has no state. `decodeMasterZoneGroup` influences whether a newly created Ceph zonegroup receives `--master`, which persists in Ceph multisite period/zonegroup configuration.

## Dependencies and Integration Points

It depends on Go `encoding/json`, `pkg/errors`, and `cephv1.CephObjectZoneGroup`. The controller calls both functions during active reconciliation.

## Risks and Edge Cases

- `decodeMasterZoneGroup` only extracts one field and cannot validate overall period structure.
- A period JSON with no `master_zonegroup` is indistinguishable from a valid period with an intentionally empty master; this is used by the controller to mark the first zonegroup master.
- `validateZoneGroup` does not validate that the referenced realm exists; that is handled by controller logic.

## Test Signals

There is no direct unit test for this helper file. `controller_test.go` indirectly exercises successful period decoding and validation in the happy path.
