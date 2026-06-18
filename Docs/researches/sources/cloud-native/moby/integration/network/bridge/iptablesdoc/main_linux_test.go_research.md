<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/main_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/iptablesdoc/main_linux_test.go

Purpose: package-level test harness for the iptables documentation integration package.

Important APIs/types/functions: declares package globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. `TestMain` configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment info, records non-zero test exit status on the span, shuts tracing down, and exits with `m.Run()`'s code. `setupTest` starts a child span, protects all environment resources, and schedules environment cleanup.

Control flow: all tests in the package share the initialized execution environment. Errors during environment creation or image setup panic after marking the tracing span.

State/persistence: owns process-wide test environment state and base tracing context. Cleanup is per-test through `environment.ProtectAll` and `testEnv.Clean`.

Dependencies/integration: integrates `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. The documentation test depends on this for daemon API access and image availability.

Risks: harness failures abort the package before any documentation test runs. It calls `EnsureFrozenImagesLinux`, so Windows or image-preload changes can alter package startup behavior.

Test signals: successful package startup means the environment can create daemons with frozen BusyBox images and has tracing configured for per-test spans.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/main_linux_test.go -->
