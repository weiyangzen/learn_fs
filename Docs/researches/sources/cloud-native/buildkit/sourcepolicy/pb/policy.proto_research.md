# sources/cloud-native/buildkit/sourcepolicy/pb/policy.proto

## Purpose
Defines the source policy protobuf schema used to allow, deny, or convert BuildKit source operations.

## Important APIs, Types, And Functions
- `Rule` has `action`, `selector`, and `updates`.
- `Update` has destination `identifier` and attr map.
- `Selector` has source `identifier`, `match_type`, and repeated attr constraints.
- `AttrConstraint` has key, value, and condition.
- `Policy` has version and repeated rules.
- Enums: `PolicyAction` (`ALLOW`, `DENY`, `CONVERT`), `AttrMatch` (`EQUAL`, `NOTEQUAL`, `MATCHES`), and `MatchType` (`WILDCARD`, `EXACT`, `REGEX`).

## Control Flow
The proto itself has no runtime flow, but generated code and engine logic interpret rules in order. Defaults matter: zero values mean allow action, wildcard matching, and equality constraints.

## State And Persistence
Policies serialized from this schema are the durable policy representation. `version` is documented as currently 1.

## Dependencies And Integration Points
The `go_package` maps generated bindings to `github.com/moby/buildkit/sourcepolicy/pb;moby_buildkit_v1_sourcepolicy`. Engine, matcher, mutator, and JSON helpers consume the generated Go types.

## Risks And Edge Cases
Typos in comments (`due`, `litteral`) are harmless but visible in generated docs. Adding enum values requires updating JSON validation tests and fixing enum-specific validation logic.

## Test Signals
All sourcepolicy tests exercise generated types from this schema; JSON tests validate enum serialization for current values.
