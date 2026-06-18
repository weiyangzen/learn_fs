# sources/cloud-native/moby/daemon/volume/mounts/validate_unix_test.go

## Purpose
Unix test constants for shared mount validation tests.

## Important APIs, Types, And Functions
Defines `testDestinationPath = "/foo"` and `testSourcePath = "/foo"` for non-Windows builds.

## Control Flow
No runtime logic; constants are compiled into `validate_test.go` and `parser_test.go`.

## State And Persistence
No state.

## Dependencies And Integration Points
Selected by `//go:build !windows` and used by shared tests to express Unix absolute paths.

## Risks
Constants must stay valid for Linux parser absolute-path rules.

## Test Signals
Successful non-Windows test compilation validates build-tag wiring.
