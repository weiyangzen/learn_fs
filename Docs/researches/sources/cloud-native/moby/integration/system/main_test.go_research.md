# sources/cloud-native/moby/integration/system/main_test.go

## Purpose
Package-level test harness for system integration tests.

## Important APIs, Types, And Functions
- `TestMain` configures tracing, creates `environment.Execution`, ensures frozen Linux images, prints environment data, runs tests, and exits.
- `setupTest` creates a per-test span, protects baseline resources, and schedules cleanup.

## Control Flow
The flow is identical to service/session/volume package harnesses: initialize once, run all tests, then shut down tracing.

## State And Persistence
Holds global environment and base context. Per-test cleanup removes resources created by system tests while preserving protected initial state.

## Dependencies And Integration Points
Depends on `internal/testutil`, `environment`, OpenTelemetry, and frozen image provisioning.

## Risks And Edge Cases
Any failure before `m.Run` panics and prevents tests from executing. Cleanup is broad and can interact with tests that start their own daemons or rely on the shared daemon state.

## Test Signals
Successful startup yields a usable `testEnv` and traced base context for all system tests.
