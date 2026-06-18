<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/main_test.go -->
# sources/cloud-native/moby/integration/network/main_test.go

Purpose: shared test harness for the general `integration/network` package.

Important APIs/types/functions: declares `testEnv`, `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment info, tracks non-zero package exits on the root span, and protects/cleans resources per test.

Control flow: global setup runs before all tests and panics on environment/image failures. `setupTest` starts a per-test span, calls `environment.ProtectAll`, and registers `testEnv.Clean`.

State/persistence: package-global environment and tracing context. Per-test cleanup resets daemon resources known to the environment helper.

Dependencies/integration: `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. General network tests use `testEnv` for daemon info, rootless/remote flags, API client, and firewall backend.

Risks: image setup is Linux-oriented even though some package files have Windows behavior; platform-specific skips must prevent incompatible execution. Host-level mutations in tests still need explicit cleanup.

Test signals: successful harness setup is a prerequisite for all general network integration tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/main_test.go -->
