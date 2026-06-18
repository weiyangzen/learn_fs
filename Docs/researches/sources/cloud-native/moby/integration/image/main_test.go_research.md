# sources/cloud-native/moby/integration/image/main_test.go

Purpose: package-level setup and per-test cleanup helper for image integration tests.

Important APIs and helpers: globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. It calls tracing setup, `environment.New`, `environment.EnsureFrozenImagesLinux`, `environment.ProtectAll`, and `testEnv.Clean`.

Control flow: `TestMain` configures tracing, creates the execution environment, ensures frozen images, prints environment details, and runs tests. `setupTest` starts a per-test span, protects existing resources, schedules environment cleanup, and returns a context.

State and persistence: maintains shared test environment and context. `setupTest` preserves baseline images/resources and removes test-created state after each test through the environment cleaner.

Dependencies and integration: depends on Moby internal test environment and tracing helpers. It integrates all image tests with consistent frozen image availability and cleanup.

Risks: initialization failures panic. `os.Exit(m.Run())` means the tracing shutdown call after normal test completion is not reached in this file as written.

Test signals: infrastructure-only; successful setup is required for reliable image test isolation.
