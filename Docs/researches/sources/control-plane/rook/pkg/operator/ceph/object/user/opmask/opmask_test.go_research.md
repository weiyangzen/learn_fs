# sources/control-plane/rook/pkg/operator/ceph/object/user/opmask/opmask_test.go

## Purpose

This file tests the `opmask` helper's conversion and formatting behavior for RGW object-user operation masks.

## Important Test Cases

- `TestFromSlice` checks all read/write/delete subsets, confirms input order does not matter, and confirms an empty slice returns an empty mask.
- `TestString` checks all matching string outputs and the `"<none>"` representation for an empty mask.

## Control Flow and Test Setup

Both tests use table-driven subtests with `fmt.Sprintf` names and `testify/assert`. The tests are in the `opmask` package, so they can compare private `OpMask` fields directly.

## State and Persistence Signals

No external state is created. The tests validate the exact strings that will later be persisted into RGW user op-mask settings by the object user controller.

## Dependencies and Integration Points

The tests depend on `cephv1.ObjectUserOpMask`, `testify/assert`, and the local `FromSlice`/`String` APIs.

## Risks and Gaps

Nil input behavior is not tested even though `FromSlice` returns an error for nil. Unknown values are also untested. Those gaps are acceptable if CRD validation guarantees only valid enum values and the controller never passes nil when an explicit op-mask is set.
