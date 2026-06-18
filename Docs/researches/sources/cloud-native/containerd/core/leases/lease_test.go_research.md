# sources/cloud-native/containerd/core/leases/lease_test.go

## Purpose

This test file verifies lease label option behavior. It protects label merging semantics used by lease creation and metadata GC labeling.

## Important APIs, Types, and Functions

`TestWithLabels` runs table cases for `WithLabels` and repeated `WithLabel`. `newLease` creates a lease with a defensive copy of initial labels.

## Control Flow

The test first applies `WithLabels` to leases with nil or existing labels and compares the resulting map to expected values. It then repeats the same cases by applying `WithLabel` for each input label and checking the same expected output.

## State and Persistence Behavior

All state is in-memory. The tests do not exercise a lease manager or metadata DB.

## Dependencies and Integration Points

It uses `maps.Copy`, `testify/assert`, and `testify/require`. It validates option helpers consumed by both local metadata and remote proxy lease managers.

## Risks and Edge Cases

The file does not test overwriting an existing key, empty values, nil input maps, expiration labels, random IDs, or delete options. It also does not validate labels through the metadata manager.

## Test Signals

Passing tests indicate label map initialization, merging, and preservation of existing labels work for both bulk and single-label option APIs.
