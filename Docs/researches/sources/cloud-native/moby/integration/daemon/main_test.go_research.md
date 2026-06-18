# sources/cloud-native/moby/integration/daemon/main_test.go

Purpose: package-level test bootstrap for daemon integration tests.

Important APIs and helpers: package globals `testEnv` and `baseContext`, and `TestMain`. It calls `environment.New`, `environment.EnsureFrozenImagesLinux`, `testEnv.Print`, and OpenTelemetry span status APIs.

Control flow: `TestMain` creates a root tracing span, initializes the execution environment, ensures frozen Linux images are available, prints environment details, runs the package tests, records a tracing error on nonzero exit, and exits with the test code.

State and persistence: stores environment and context in package globals consumed by daemon tests. It may load or verify frozen images in the daemon test environment before tests execute.

Dependencies and integration: depends on Moby internal test environment helpers and OpenTelemetry. It integrates package tests with shared daemon metadata, image fixtures, and tracing.

Risks: initialization failure panics before individual tests can skip. `os.Exit` bypasses deferred cleanup in `TestMain`, so explicit span ending happens only on initialization failures in this file.

Test signals: not a behavioral test itself, but it is required infrastructure for consistent daemon integration environment setup.
