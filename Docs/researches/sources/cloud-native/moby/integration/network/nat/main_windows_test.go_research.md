<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/nat/main_windows_test.go

Purpose: Windows NAT network package test harness.

Important APIs/types/functions: declares `testEnv`, `baseContext`, `TestMain`, and `setupTest`, configuring tracing and the test execution environment for NAT tests.

Control flow: `TestMain` initializes environment state, calls `EnsureFrozenImagesLinux`, prints environment details, records failed exit status on the span, shuts down tracing, and exits. `setupTest` starts a child span and schedules environment cleanup.

State/persistence: package-global environment and tracing context; per-test environment cleanup.

Dependencies/integration: Moby `testutil`, `environment`, and OpenTelemetry. Although the file is Windows-named, it shares the same environment setup pattern as other network packages.

Risks: `EnsureFrozenImagesLinux` in a Windows-named harness is surprising and may rely on the broader integration test environment's conventions. If Windows image preparation diverges, this harness may need adjustment.

Test signals: package setup success allows the Windows NAT behavior test to run against `testEnv.APIClient()`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/main_windows_test.go -->
