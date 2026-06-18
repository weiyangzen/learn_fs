# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils_test.go

## Purpose
This test file covers selected package-level dashboard utility behavior: reverse sorting, PVC selector emptiness, and directory string normalization.

## Important APIs, Types, And Functions
It defines `TestReverse`, `TestIsPVCSelectorEmpty`, and `TestStripDir`.

## Control Flow
`TestReverse` builds a `ListSCResult` with three storage classes and sorts it through `Reverse`, then asserts descending creation timestamps. `TestIsPVCSelectorEmpty` checks that an empty `config.PVCSelector` is treated as empty. `TestStripDir` verifies backslash, slash, and `..` replacement with dashes.

## State And Persistence
Tests use local in-memory fixtures only.

## Dependencies And Integration Points
The tests exercise helpers used by `pv.go`, `batch.go`, and debug bundle path construction. They depend on StorageClass metadata and config selector structs.

## Risks
Coverage is narrow: nil selector behavior, populated selector fields, safe `/tmp` path enforcement, zip creation, and owner-reference helpers are not tested.

## Test Signals
Passing tests indicate basic sort inversion and path component normalization still behave as expected.
