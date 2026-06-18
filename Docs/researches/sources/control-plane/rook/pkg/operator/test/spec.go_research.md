# sources/control-plane/rook/pkg/operator/test/spec.go

## Purpose
`spec.go` provides generic assertion helpers for operator-generated CLI arguments and Kubernetes labels.

## Important APIs, Types, and Functions
`ArgumentsMatchExpected(actualArgs, expectedArgs)` verifies that expected argument groups appear exactly once and that no extra actual arguments remain. `AssertLabelsContainRookRequirements()` asserts an `app=<appName>` label is present. A package logger supports debug output.

## Control Flow, State, and Persistence
`ArgumentsMatchExpected()` joins args into one string, searches for each expected group with `strings.Count`, removes matched text once, and errors on missing, duplicate, empty expected, or leftover actual args. There is no persistence.

## Dependencies and Integration Points
It depends on capnslog, testify, and testing. It is used by operator unit tests that validate generated command args and resource labels.

## Risks
String-search matching can create false positives when one argument group is a substring of another or when argument values contain spaces. It cannot support duplicate identical flag/value groups by design.

## Test Signals
`spec_test.go` covers short flags, long flags with `=`, long flags with values, out-of-order values, missing/extra args, empty expected args, and duplicates.
