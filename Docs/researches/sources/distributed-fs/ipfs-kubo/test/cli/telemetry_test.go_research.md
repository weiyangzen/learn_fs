# sources/distributed-fs/ipfs-kubo/test/cli/telemetry_test.go

Purpose: validates the telemetry plugin's opt-out behavior, first-run messaging, UUID-file handling, and schema stability.

Important APIs and dependencies: `TestTelemetry` manipulates `Plugins.Plugins.telemetry` config, environment variables such as `IPFS_TELEMETRY` and `GOLOG_LOG_LEVEL`, captures daemon stdout/stderr with `harness.Buffer`, uses `httptest.Server` to receive telemetry JSON, and uses `maps.Keys`/`slices.Sort` for schema comparison.

Control flow: environment opt-out and config opt-out tests enable the plugin but opt out, start daemons with debug logging, expect opt-out log messages, and assert `telemetry_uuid` does not exist. A removal test pre-creates `telemetry_uuid`, opts out, and expects a removal log plus file deletion. Enabled-first-run test starts without opt-out and expects informational text and UUID creation. Schema regression test configures a short delay and mock endpoint, starts a daemon, waits for one POST, and compares the exact set of telemetry fields to an expected list.

State and persistence: `telemetry_uuid` is the primary on-disk state. It should be created when telemetry is enabled and absent/removed when opted out. Config controls endpoint, delay, mode, and plugin disabled status.

Dependencies and integration points: integrates plugin config, daemon startup logging, environment opt-out, filesystem state, HTTP posting, JSON schema, and platform/config collectors.

Risks and test signals: the schema list is intentionally strict and must be updated with legitimate telemetry field changes. Timing depends on daemon startup and the configured delay. Failures indicate privacy opt-out regressions, UUID leakage, missing first-run disclosure, or telemetry schema drift.
