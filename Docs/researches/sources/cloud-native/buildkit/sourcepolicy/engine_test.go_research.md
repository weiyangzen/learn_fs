# sources/cloud-native/buildkit/sourcepolicy/engine_test.go

## Purpose
Tests source policy evaluation semantics across allow, deny, conversion, loop protection, multiple policies, and match types.

## Important APIs, Types, And Functions
- `TestEngineEvaluate` orchestrates subtests.
- Helper subtests include `testDenyAll`, `testAllowDeny`, `testConvert`, `testConvertExact`, `testConvertDeny`, `testAllowConvertDeny`, `testConvertLoop`, `testConvertHTTP`, `testConvertRegex`, `testConvertWildcard`, `testConvertMultiple`, `testMultiplePolicies`, and `testLastRuleWins`.

## Control Flow
Each subtest builds protobuf policy rules and source ops, evaluates with `NewEngine`, and asserts mutation booleans, errors, and final identifiers/attrs. Conversion tests rely on repeated evaluation after mutation; loop tests expect `ErrTooManyOps`.

## State And Persistence
No persistence. Source ops are intentionally mutated in memory during assertions.

## Dependencies And Integration Points
Uses solver protobuf source ops, sourcepolicy protobufs, BuildKit logger, logrus, and `testify/require`.

## Risks And Edge Cases
Tests document important policy semantics: last allow/deny rule wins within a policy, multiple policies are evaluated sequentially, and conversion can be followed by denial.

## Test Signals
Strong coverage for engine orchestration but does not directly test selector-cache concurrency.
