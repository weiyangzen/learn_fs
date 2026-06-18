<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/main_test.go -->
# sources/cloud-native/moby/integration/network/bridge/main_test.go

Purpose: shared test harness for the Linux bridge integration package.

Important APIs/types/functions: exports package-level `testEnv`, `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes environment metadata/client access, preloads frozen Linux images, prints environment details, and wraps tests with resource protection/cleanup.

Control flow: `TestMain` establishes `baseContext`, handles initialization errors by marking the root span and panicking, then runs the package tests. `setupTest` starts a span from `baseContext`, calls `environment.ProtectAll`, and schedules `testEnv.Clean`.

State/persistence: package-global environment and tracing context. Per-test cleanup resets Docker resources managed by the environment helper.

Dependencies/integration: depends on `testutil`, `environment`, and OpenTelemetry. All bridge tests use it to acquire an API client, daemon feature flags, firewall backend, rootless status, and cleanup behavior.

Risks: image setup is Linux-specific; a failure in global setup prevents all bridge tests from running. Tests that manually start daemons or mutate host state still need their own cleanup beyond environment cleanup.

Test signals: harness success indicates the bridge suite can rely on a configured daemon environment and frozen images.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/main_test.go -->
