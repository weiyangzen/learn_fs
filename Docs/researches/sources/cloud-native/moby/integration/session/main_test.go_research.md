# sources/cloud-native/moby/integration/session/main_test.go

## Purpose
Provides package-level tracing, environment initialization, frozen image setup, and per-test cleanup for session integration tests.

## Important APIs, Types, And Functions
- `TestMain` configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment metadata, runs tests, and exits with the test code.
- `setupTest` wraps tests in spans, protects baseline resources, and registers `testEnv.Clean`.

## Control Flow
Startup mirrors other integration packages: create base context/span, create environment, ensure images, run tests, then shut tracing down.

## State And Persistence
Stores `testEnv` and `baseContext` package globals. The environment protection snapshot controls what cleanup preserves.

## Dependencies And Integration Points
Depends on `internal/testutil`, `environment`, and OpenTelemetry. Session tests use this to reach the configured daemon.

## Risks And Edge Cases
Environment setup failures panic before tests. Cleanup is broad, so session tests must protect resources they expect to survive.

## Test Signals
Package readiness is signaled by successful environment creation and frozen-image preparation before `m.Run`.
