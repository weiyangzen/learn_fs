# sources/cloud-native/moby/integration/system/ping_test.go

## Purpose
Validates `/_ping` HTTP and client behavior: cache headers, GET/HEAD bodies and API version headers, Swarm status header state transitions, and builder version reporting.

## Important APIs, Types, And Functions
- `TestPingCacheHeaders`, `TestPingGet`, and `TestPingHead` use raw request helpers.
- `TestPingSwarmHeader` starts a daemon, checks ping before Swarm init, after init, and after leave.
- `TestPingBuilderHeader` starts daemons with default config and with BuildKit disabled via a generated `daemon.json`.

## Control Flow
Raw ping tests use the shared environment. Swarm and builder tests skip remote/Windows as needed, start isolated daemons, perform daemon state transitions, call `apiClient.Ping`, and compare returned fields.

## State And Persistence
Swarm test mutates daemon Swarm state from inactive to active and back. Builder test writes a `daemon.json` under the test daemon root and starts/stops daemons with different config.

## Dependencies And Integration Points
Touches API router ping endpoint, client ping response parsing, Swarm local node status, BuildKit feature config, daemon startup config-file handling, and raw HTTP request helpers.

## Risks And Edge Cases
Builder default differs on Windows, though the local-daemon builder test skips Windows. The BuildKit-disabled case writes config directly with `os.WriteFile` and assumes daemon root exists before start.

## Test Signals
Signals include no-cache headers, GET body `OK`, empty HEAD body, nonempty `Api-Version`, correct Swarm inactive/active/control flags, and builder version switching from BuildKit default to v1 when disabled.
