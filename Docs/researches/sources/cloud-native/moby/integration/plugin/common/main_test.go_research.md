# sources/cloud-native/moby/integration/plugin/common/main_test.go

## Purpose
Shared test harness for common plugin integration tests. It configures tracing, initializes the test environment, exposes `testEnv` and `baseContext`, and provides `setupTest` for environment protection and cleanup.

## Important APIs, Types, And Functions
`TestMain` calls `testutil.ConfigureTracing`, `environment.New`, `testEnv.Print`, `m.Run`, and records OpenTelemetry span status/exit attribute. `setupTest` starts a per-test span, calls `environment.ProtectAll`, and schedules `testEnv.Clean`.

## Control Flow
Suite setup runs once, then common plugin tests call `setupTest` or use `baseContext` directly. The process exits with the test runner's code.

## State And Persistence Behavior
Package globals hold environment and base context. Per-test cleanup is delegated to the environment helper.

## Dependencies And Integration Points
All common plugin tests depend on this file for environment discovery and cleanup. It integrates with OpenTelemetry and Moby's integration environment utilities.

## Risks
If environment initialization fails, the package panics before any tests run. Tests that bypass `setupTest` must handle cleanup themselves.

## Test Signals
No direct assertions except setup failure handling and non-zero exit marking in tracing.
