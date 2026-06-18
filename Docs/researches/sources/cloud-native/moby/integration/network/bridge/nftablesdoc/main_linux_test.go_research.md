<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/main_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/nftablesdoc/main_linux_test.go

Purpose: package-level test harness for bridge nftables documentation generation.

Important APIs/types/functions: defines `testEnv`, `baseContext`, `TestMain`, and `setupTest`, matching the iptables documentation harness. It configures tracing, creates the test environment, ensures frozen Linux images, prints environment details, and wraps individual tests in cleanup.

Control flow: initialization failures mark the root span and panic; otherwise `m.Run()` decides the exit code. `setupTest` starts a span and protects/cleans environment resources.

State/persistence: holds process-global test environment and tracing context. Per-test cleanup is scheduled through the environment helper.

Dependencies/integration: OpenTelemetry, Moby `testutil`, and `environment`. The nftables documentation test uses `testEnv` to detect rootless/firewall backend state.

Risks: Linux image availability and environment initialization are package-wide prerequisites. Because this package documents nftables output, an incorrectly detected firewall backend can skip or run the wrong test.

Test signals: package startup success provides a daemon-capable environment with frozen images for nftables rule generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/main_linux_test.go -->
