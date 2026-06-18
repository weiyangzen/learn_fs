# sources/cloud-native/moby/daemon/server/router/plugin/plugin_routes.go

## Purpose
`plugin_routes.go` implements plugin API handlers for privilege discovery, pull, upgrade, create, enable/disable, remove, push, set, list, and inspect.

## Important APIs, Types, And Functions
Helpers include `parseHeaders`, `parseRemoteRef`, and `getName`. Handlers include `getPrivileges`, `upgradePlugin`, `pullPlugin`, `createPlugin`, `enablePlugin`, `disablePlugin`, `removePlugin`, `pushPlugin`, `setPlugin`, `listPlugins`, and `inspectPlugin`.

## Control Flow
Registry operations parse `remote`, preserve meta headers, ignore invalid auth headers for compatibility, normalize digest/tag references, derive local plugin names, and stream JSON progress through `WriteFlusher`. Lifecycle operations parse query/body values and delegate to backend option structs. `enablePlugin` parses timeout as an integer and marks bad values invalid.

## State And Persistence
Backend calls persist plugin installation, enabled state, settings, removals, and registry push/pull/upgrade effects. Router state is transient.

## Dependencies And Integration Points
Integrates distribution reference parsing, authconfig, plugin API types, daemon filters, stream formatters, backend plugin option structs, and error classification.

## Risks
Digest-plus-tag parsing is subtle: remote digest tags are preserved for local names but canonical refs drop tags. User-supplied local names cannot include digests. Streaming errors after flush must be formatted into progress output.

## Test Signals
No direct tests here; plugin integration tests cover remote ref handling, privilege negotiation, lifecycle operations, and registry streaming.
