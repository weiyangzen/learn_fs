<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_test.go -->
# sources/cloud-native/moby/daemon/command/daemon_test.go

## Purpose
Exercises daemon CLI configuration loading, TLS option defaults, duplicate/conflicting labels, registry options, daemon log setup, CDI spec-dir resolution, and an OpenTelemetry meter allocation regression.

## Important APIs, Types, And Functions
`defaultOptions` builds a `daemonOptions` with common and platform config flags installed. The tests call `loadDaemonCliConfig`, `configureDaemonLogs`, and `otel.Meter().Int64Counter`.

## Control Flow
Each test creates a temporary daemon JSON file or empty option set, mutates flags/env-derived fields, then asserts merged config fields or expected conflict errors. `TestCDISpecDirs` table-drives feature-flag and flag interactions.

## State And Persistence Behavior
State is test-local through temp files and process-wide logging/debug settings. The OTEL test reads runtime memory counters but does not persist data.

## Dependencies And Integration Points
Depends on `daemon/config`, `pflag`, `gotest.tools`, containerd logging, and OpenTelemetry. It protects the command package boundary where CLI flags become daemon config.

## Risks And Test Signals
Key signals are conflict errors for labels/node resources, TLS implicit enablement, log level stability after bad input, CDI defaults, and low allocation count for repeated OTEL counter lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_test.go -->
