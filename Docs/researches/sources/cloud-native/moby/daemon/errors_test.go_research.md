# sources/cloud-native/moby/daemon/errors_test.go

## Purpose
Tests daemon not-running error classification.

## Important APIs, Types, And Functions
- `TestContainerNotRunningError` creates an error with `errNotRunning` and asserts `isNotRunning` recognizes it.

## Control Flow
The test directly exercises the constructor and classifier.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Covers `errors.go` and the internal type-based `errors.As` classification used by delete/kill cleanup paths.

## Risks And Edge Cases
The test is narrow and does not cover errdefs marker behavior or start exit-code mapping.

## Test Signals
Failure would mean force-removal and cleanup paths may stop ignoring already-not-running conditions correctly.
