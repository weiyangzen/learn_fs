# sources/cloud-native/moby/integration/daemon/nri/main_test.go

Purpose: package-level bootstrap for NRI daemon integration tests.

Important APIs and helpers: package globals `testEnv` and `baseContext`, and `TestMain`. It calls `environment.New`, `environment.EnsureFrozenImagesLinux`, `testEnv.Print`, and OpenTelemetry span status APIs.

Control flow: initializes a tracing span, builds the shared test environment, ensures frozen Linux images are loaded or available, prints environment details, runs all NRI tests, records an error status on nonzero test exit, and exits.

State and persistence: stores execution environment and base context in package-level variables used by NRI tests that start sub-daemons and plugins.

Dependencies and integration: depends on Moby test environment helpers and OpenTelemetry. It prepares the daemon and image fixtures required by NRI integration tests.

Risks: initialization failures panic before individual tests can apply skips. Like other `TestMain` implementations using `os.Exit`, normal defer-based cleanup in `TestMain` is not available.

Test signals: infrastructure file; its success indicates the environment is suitable for the NRI test package.
