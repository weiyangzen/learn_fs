# sources/cloud-native/containerd/internal/cri/util/deep_copy_test.go

## Purpose
Tests the JSON-backed `DeepCopy` helper with nested composite values.

## Important APIs, Types, And Functions
Defines test struct `A` with strings, ints, slices, maps, and nested `*A` values. `TestCopy` builds distinct source, destination, and expected values.

## Control Flow
The test asserts the destination initially differs, calls `DeepCopy(dst, src)`, requires no error, then checks full equality with the expected copy.

## State And Persistence
Only in-memory test fixtures. The destination object is intentionally mutated.

## Dependencies And Integration Points
Uses Go testing and `testify/assert`. It directly covers `internal/cri/util.DeepCopy`.

## Risks
The test does not cover nil arguments, marshal errors, unmarshal errors, custom JSON methods, or partial mutation on unmarshal failure.

## Test Signals
Strong signal for ordinary JSON-compatible nested maps/slices and replacement semantics.
