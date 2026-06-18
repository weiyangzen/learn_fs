# sources/cloud-native/buildkit/sourcepolicy/pb/json.go

## Purpose
Adds custom JSON marshal/unmarshal behavior for sourcepolicy enum types so policies can use readable enum names.

## Important APIs, Types, And Functions
- `PolicyAction.MarshalJSON` / `UnmarshalJSON`.
- `AttrMatch.MarshalJSON` / `UnmarshalJSON`.
- `MatchType.MarshalJSON` / `UnmarshalJSON`.

## Control Flow
Marshal calls BuildKit's gogo proto JSON enum helper with enum name maps. Unmarshal accepts string or numeric JSON, validates that the decoded numeric value exists in the enum name map, and assigns it.

## State And Persistence
No persistent state. It uses generated enum name/value maps.

## Dependencies And Integration Points
Used whenever policies are JSON encoded/decoded. Depends on `util/gogo/proto` helpers and pkg/errors.

## Risks And Edge Cases
`MatchType.UnmarshalJSON` validates against `AttrMatch_name` instead of `MatchType_name`, which works only because both enums currently have values 0..2; adding divergent enum values would incorrectly reject/accept values.

## Test Signals
`json_test.go` round-trips all current enum values by string and number, but would not catch the wrong validation map while enum numeric ranges remain identical.
