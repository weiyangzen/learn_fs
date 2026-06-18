<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_test.go -->
# sources/cloud-native/moby/integration/network/overlay/main_test.go

Purpose: non-Windows test harness for overlay network integration tests.

Important APIs/types/functions: package globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. It configures tracing, creates the execution environment, ensures frozen Linux images, prints environment info, records exit status attribute, and cleans resources per test.

Control flow: setup failures mark span status, end/shutdown tracing, and panic. `setupTest` starts a child span, protects resources, and schedules cleanup.

State/persistence: package-global test environment and tracing context; overlay tests create their own swarm/daemon state.

Dependencies/integration: Moby `testutil`, `environment`, and OpenTelemetry. Build tag excludes Windows.

Risks: global environment setup is a package-wide prerequisite. Overlay tests additionally depend on swarm support and rootless skips.

Test signals: successful harness startup provides the daemon/image environment required for overlay tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_test.go -->
