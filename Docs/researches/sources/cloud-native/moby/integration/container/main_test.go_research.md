# sources/cloud-native/moby/integration/container/main_test.go

Purpose: Shared test harness for the `integration/container` package.

Important APIs and flow: `TestMain` configures tracing, creates the global `environment.Execution`, ensures frozen Linux images are available, prints the environment, runs tests, records tracing status, shuts tracing down, and exits with the test code. `setupTest` starts a per-test span from `baseContext`, protects shared test environment state with `environment.ProtectAll`, and registers cleanup through `testEnv.Clean`.

State and dependencies: Defines package globals `testEnv` and `baseContext`. It centralizes API client/environment access and cleanup for all tests in this package. Dependencies include `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry.

Risks and signals: Any issue here impacts every container integration test. It controls image availability, environment isolation, and cleanup, so regressions can cause cross-test contamination, missing images, or incomplete tracing/cleanup.
