# sources/cloud-native/moby/daemon/volume/mounts/validate_test.go

## Purpose
Shared validation tests for mount configs on the current platform plus LCOW-specific validation on Windows.

## Important APIs, Types, And Functions
`TestValidateMount` calls `NewParser().ValidateMountConfig`; `TestValidateLCOWMount` calls `NewLCOWParser` on Windows.

## Control Flow
Tests cover missing target/source, valid volume and bind configs, volume subpaths, extra option structs for wrong mount types, unknown mount types, missing bind source, and non-Windows image mount validation. LCOW tests verify similar rules with Linux-style targets and Windows host sources.

## State And Persistence
Uses temporary directories only.

## Dependencies And Integration Points
Depends on parser selection and platform constants from `validate_unix_test.go` or `validate_windows_test.go`.

## Risks
Because platform-specific parser behavior differs, the same table can assert slightly different full errors only through substring matching.

## Test Signals
Good regression signal for common API validation rules and cross-type option rejection.
