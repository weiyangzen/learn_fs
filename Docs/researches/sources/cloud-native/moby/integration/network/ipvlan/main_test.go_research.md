<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_test.go -->
# sources/cloud-native/moby/integration/network/ipvlan/main_test.go

Purpose: non-Windows test harness for the ipvlan integration package.

Important APIs/types/functions: package globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment info, records failed exit code on the span, and wraps tests with environment protection/cleanup.

Control flow: initialization errors mark the span, end tracing, shut down, and panic. `setupTest` starts a per-test span from `baseContext`, calls `environment.ProtectAll`, and schedules `testEnv.Clean`.

State/persistence: holds package-global environment state and OpenTelemetry base context. Per-test cleanup is delegated to the environment helper, while individual ipvlan tests clean host links/daemons.

Dependencies/integration: `testutil`, `environment`, and OpenTelemetry. The build tag excludes Windows.

Risks: frozen Linux image setup is mandatory for the package; failures abort all ipvlan tests. Host link mutations still rely on test-specific cleanup.

Test signals: package startup success indicates the ipvlan suite has daemon/image resources and tracing context available.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_test.go -->
