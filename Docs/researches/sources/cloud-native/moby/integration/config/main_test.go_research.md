## sources/cloud-native/moby/integration/config/main_test.go

Purpose: package-level setup for integration config tests. It initializes tracing and the Moby test environment, ensures frozen Linux images, prints environment diagnostics, runs the package tests, and provides per-test cleanup.

Control flow mirrors other integration packages: `TestMain` creates a root context/span, calls `environment.New`, loads frozen images, runs `m.Run`, records nonzero exit status on the span, shuts tracing down, and exits. `setupTest` starts a span from `baseContext`, protects all resources, and schedules `testEnv.Clean`.

State includes global `testEnv`, `baseContext`, tracing spans, protected resources, and environment cleanup. Dependencies are `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. Risks are global setup failure blocking all config tests and cleanup mistakes leaking swarm/config resources between tests. Test signals are successful environment setup and deterministic cleanup isolation for `config_test.go`.
