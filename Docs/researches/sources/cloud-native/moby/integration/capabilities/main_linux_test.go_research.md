## sources/cloud-native/moby/integration/capabilities/main_linux_test.go

Purpose: test harness setup for the Linux capabilities integration package. It configures tracing, creates the shared test environment, ensures frozen Linux images are available, prints environment information, runs tests, and cleans tracing state.

Control flow in `TestMain` starts an OpenTelemetry span, calls `environment.New`, calls `environment.EnsureFrozenImagesLinux`, runs `m.Run`, marks the span on failure, ends tracing, and exits with the test code. `setupTest` starts a per-test span, protects all known resources, and registers environment cleanup.

State includes global `testEnv` and `baseContext`, tracing spans, protected images/resources, and environment-managed cleanup state. Dependencies are `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. Risks are fatal setup failure if environment discovery or frozen-image loading fails; all package tests depend on this global setup. Test signals are package startup success and cleanup isolation.
