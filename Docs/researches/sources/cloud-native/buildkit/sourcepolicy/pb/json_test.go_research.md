# sources/cloud-native/buildkit/sourcepolicy/pb/json_test.go

## Purpose
Tests JSON string and numeric round-tripping for sourcepolicy enum types.

## Important APIs, Types, And Functions
- `TestActionJSON`, `TestAttrMatchJSON`, and `TestMatchTypeJSON`.

## Control Flow
Each test iterates the generated enum name map, marshals enum values to JSON strings, unmarshals strings back, marshals numeric values, and unmarshals numbers back to equivalent enum values.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses Go `encoding/json`, generated protobuf enum maps, and `testify/require`.

## Risks And Edge Cases
The tests do not exercise invalid enum values. Because current enum numeric ranges align, they do not detect `MatchType.UnmarshalJSON` validating against the wrong enum map.

## Test Signals
Confirms human-readable JSON compatibility for all currently generated enum values.
