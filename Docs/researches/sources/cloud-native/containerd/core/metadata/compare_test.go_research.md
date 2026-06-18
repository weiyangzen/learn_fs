# sources/cloud-native/containerd/core/metadata/compare_test.go

## Purpose

This test helper file defines custom `go-cmp` comparers used by metadata tests. It normalizes typed nils, timestamps, and protobuf Any values so object round-trip assertions focus on meaningful fields.

## Important APIs, Types, and Functions

`isNil` detects nil and typed nil pointers. `compareNil` treats two nil or typed nil values as equal. `ignoreTime` treats all `time.Time` values as equal. `compareAny` compares `typeurl.Any` values by type URL and raw value bytes.

## Control Flow

The comparers use `cmp.FilterValues` predicates to activate only for relevant value pairs, then supply equality functions. `compareAny` type-asserts both values and compares type URL plus bytes.

## State and Persistence Behavior

No state is persisted. These are test-only comparison utilities.

## Dependencies and Integration Points

Container metadata tests use these options when comparing containers that include timestamps, optional Any fields, and typed nil protobuf values. Dependencies include `reflect`, `bytes`, `time`, `typeurl`, and `go-cmp`.

## Risks and Edge Cases

`ignoreTime` hides timestamp regressions unless tests explicitly check timestamps elsewhere. `isNil` only treats pointers as typed nil, not nil slices/maps/interfaces of other kinds. `compareAny` compares serialized values, not semantic decoded messages.

## Test Signals

These helpers support container create/update tests. Separate timestamp checks in `containers_test.go` compensate for the broad `ignoreTime` comparer.
