# sources/cloud-native/buildkit/sourcepolicy/matcher_test.go

## Purpose
Tests source policy selector matching and attribute constraint behavior.

## Important APIs, Types, And Functions
- `TestMatch` defines table-driven cases for `match`.

## Control Flow
Each case constructs a selector, ref, optional attrs, expected boolean, and expected error flag. The test wraps the selector with `newSelectorCache`, calls `match`, and asserts the result.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses sourcepolicy protobuf selector/constraint enums and `testify/require`.

## Risks And Edge Cases
The table documents that wildcard `*` can match full source identifiers, scheme mismatch prevents more specific wildcard matches, default constraint condition is equality, and unknown attr conditions are errors.

## Test Signals
Provides focused coverage for matching before engine-level allow/deny/convert behavior.
