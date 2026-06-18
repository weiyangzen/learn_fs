# sources/cloud-native/moby/integration/networking/main_test.go

## Purpose
Defines shared test-suite setup for the `integration/networking` package. It initializes tracing, creates the execution environment, preloads/freeze-checks Linux images, exposes global `testEnv` and `baseContext`, and provides per-test cleanup helpers.

## Important APIs, Types, And Functions
`TestMain` calls `testutil.ConfigureTracing`, creates an OpenTelemetry span, runs `environment.New`, `environment.EnsureFrozenImagesLinux`, prints environment details, runs the package tests, sets span status on failure, and exits. `setupTest` starts a child span, calls `environment.ProtectAll`, and schedules `testEnv.Clean`. `sanitizeCtrName` replaces `/` and `=` with `-` for Docker-safe names.

## Control Flow
Suite initialization happens once before tests. Individual tests call `setupTest` to attach to the shared context and ensure environment cleanup after each test. Fatal environment errors panic after closing tracing.

## State And Persistence Behavior
Maintains package-level `testEnv` and `baseContext`. Per-test cleanup protects and clears daemon/container/network artifacts through the environment helper.

## Dependencies And Integration Points
Integrates all networking tests with Moby's environment abstraction, frozen image setup, OpenTelemetry, and name sanitation used by tests that derive names from `t.Name()`.

## Risks
If image preparation or environment discovery fails, no package tests run. The global context and environment are shared, so cleanup discipline in tests is important to avoid cross-test leakage.

## Test Signals
The file itself has no assertions besides setup failure handling; its signal is whether suite setup completes and whether non-zero test exit is reflected in tracing status.
