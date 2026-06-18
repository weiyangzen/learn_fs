# sources/cloud-native/moby/integration/service/main_test.go

## Purpose
Provides package-level setup and per-test cleanup for `integration/service` tests.

## Important APIs, Types, And Functions
- Global `testEnv *environment.Execution` and `baseContext context.Context` are shared by tests.
- `TestMain` configures tracing, creates the environment, ensures frozen Linux images, prints environment details, runs tests, and shuts tracing down.
- `setupTest` starts a span, protects baseline resources, and registers environment cleanup.

## Control Flow
`TestMain` runs before tests, builds a root OpenTelemetry span, initializes daemon environment metadata, loads required frozen images, then delegates to `m.Run`. Each test calls `setupTest`, which wraps the test context and schedules cleanup.

## State And Persistence
Holds package-wide environment state and protected resource snapshots. Cleanup removes test-created daemon resources after each test while preserving protected baseline objects.

## Dependencies And Integration Points
Depends on `internal/testutil`, `internal/testutil/environment`, OpenTelemetry, and the integration environment's frozen image setup. Every service integration test relies on this harness.

## Risks And Edge Cases
Failures during environment creation or frozen image setup panic before tests run. Cleanup behavior is shared and can mask or expose resource leaks across tests.

## Test Signals
Successful package startup prints environment details and allows tests to run under traced contexts with cleanup attached.
