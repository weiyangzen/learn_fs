# sources/cloud-native/moby/daemon/internal/versions/compare.go

## Purpose
Implements simple dot-separated numeric version comparison helpers.

## Important APIs, Types, And Functions
Private `compare(v1, v2)` returns -1, 0, or 1. Public helpers `LessThan`, `LessThanOrEqualTo`, `GreaterThan`, `GreaterThanOrEqualTo`, and `Equal` wrap it as booleans.

## Control Flow
Versions are split on `"."`; missing components are treated as zero. Each component is converted with `strconv.Atoi`; conversion errors are ignored, making invalid components compare as zero. The first differing numeric component decides the result.

## State And Persistence
Stateless.

## Dependencies And Integration Points
Used wherever daemon internals need lightweight numeric version checks without semantic-version prerelease/build handling.

## Risks And Test Signals
Ignoring parse errors means `"1.x"` equals `"1.0"` and negative or nonnumeric inputs are not rejected. This is not full semver. Tests cover equality with trailing zeros and basic numeric ordering.
