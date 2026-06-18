# sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask.go

## Purpose

This small helper package converts a `CephObjectStoreUser` operation-mask slice into the exact RGW admin API string format used for object-user op masks. It normalizes operation order to match radosgw-admin/admin API output.

## Important APIs, Types, and Functions

- `type OpMask struct` stores private booleans for `read`, `write`, and `delete`.
- `FromSlice(ops []cephv1.ObjectUserOpMask) (*OpMask, error)` parses a CRD enum slice into an `OpMask`.
- `(*OpMask).String() string` formats the mask as `"read, write, delete"`, any subset in read/write/delete order, or `"<none>"` when no operations are enabled.

## Control Flow

`FromSlice` rejects a nil slice, returns an empty mask for a zero-length slice, and sets booleans based on `slices.Contains` checks for `"read"`, `"write"`, and `"delete"`. It does not reject unknown entries; unknown values are ignored. `String` checks the empty mask first because RGW represents no permissions as `"<none>"`, then builds a string in fixed RGW order.

## State and Persistence Behavior

The package has no external state. Its output feeds `admin.User.OpMask` in the object user controller, which becomes persistent RGW user configuration through admin ops create/modify calls.

## Dependencies and Integration Points

It depends on the Ceph API type `cephv1.ObjectUserOpMask`, Go's `slices` and `strings` packages, and `pkg/errors`. The object user controller calls it when `spec.opMask` is explicitly set.

## Risks and Edge Cases

- Nil slices are treated as an error, but empty non-nil slices intentionally map to `"<none>"`. The controller distinguishes nil/unset from explicit empty, so this contract matters.
- Unknown operation values are ignored rather than rejected. This is probably acceptable because CRD enum validation should block invalid values, but direct Go callers would not get an error for unknown non-nil values.
- The private fields make construction outside the package impossible, which keeps callers on `FromSlice` but requires tests in-package for exact struct equality.

## Test Signals

`opmask_test.go` verifies all valid subsets, arbitrary input order, empty list behavior, and normalized string output. It does not test nil slices or unknown values.
