# sources/cloud-native/buildkit/sourcepolicy/mutate_test.go

## Purpose
Tests convert-rule mutation of BuildKit source ops.

## Important APIs, Types, And Functions
- `TestMutate` table drives `mutate` against `pb.Op_Source` wrappers and expected protobuf results.

## Control Flow
Each case extracts the source op, calls `mutate` with a selector cache and current identifier, asserts the mutation boolean and either an expected error or protobuf equality with the expected op.

## State And Persistence
No persistence. The input op is modified in place.

## Dependencies And Integration Points
Uses solver protobuf ops, sourcepolicy protobuf rules, `proto.Equal`, and `testify/require`.

## Risks And Edge Cases
The tests cover overwriting an already resolved image digest and adding HTTP checksum attrs, but do not cover nil updates despite the production error path.

## Test Signals
Focused signal that mutation correctly rewrites identifiers and initializes/updates attrs maps.
