# sources/cloud-native/buildkit/sourcepolicy/pb/policy.pb.go

## Purpose
Generated Go bindings for the source policy protobuf schema.

## Important APIs, Types, And Functions
- Enums `PolicyAction`, `AttrMatch`, and `MatchType` with name/value maps and descriptor methods.
- Messages `Rule`, `Update`, `Selector`, `AttrConstraint`, and `Policy` with protobuf reflection methods and getters.
- File descriptor globals, raw descriptor compression, dependency indexes, and `TypeBuilder` initialization.

## Control Flow
Runtime control flow is generated boilerplate: enum string/descriptor methods delegate to `protoimpl`, message methods manage protobuf reflection state, getters return zero defaults on nil receivers, and init builds the file descriptor once.

## State And Persistence
Generated descriptor globals are initialized once in memory. Message structs carry protobuf state, unknown fields, and size cache.

## Dependencies And Integration Points
Consumed by sourcepolicy engine, matcher, mutator, JSON helpers, and policy readers. Depends on `google.golang.org/protobuf` reflection/runtime packages.

## Risks And Edge Cases
Manual edits would be overwritten by regeneration. Schema/default changes affect policy semantics because nil or omitted enum fields default to `ALLOW`, `EQUAL`, and `WILDCARD`.

## Test Signals
Covered indirectly by engine/matcher/mutate/json tests. Regeneration consistency is tied to `policy.proto`.
