<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_test.go -->
# sources/cloud-native/moby/integration/network/macvlan/main_test.go

Purpose: non-Windows test harness for macvlan integration tests.

Important APIs/types/functions: defines `testEnv`, `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes the execution environment, ensures frozen Linux images, prints environment details, records the exit code as an OpenTelemetry attribute, and cleans test resources.

Control flow: `TestMain` sets up package-global state, panics on initialization/image errors after marking span status, runs tests, records non-zero status, and exits. `setupTest` starts per-test spans and schedules environment cleanup.

State/persistence: package-global environment and tracing state. Individual tests manage host interfaces and daemons beyond this harness.

Dependencies/integration: `testutil`, `environment`, OpenTelemetry `attribute`/`codes`. Build tag excludes Windows.

Risks: global setup failure stops the package. Environment cleanup does not replace explicit cleanup needed for host networking objects.

Test signals: successful startup means macvlan tests have a prepared daemon environment and frozen images.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_test.go -->
