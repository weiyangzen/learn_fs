<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/network_settings.go -->
# sources/cloud-native/moby/api/types/container/network_settings.go

## Purpose
NetworkSettings exposes the network settings in the api

## Important APIs, Types, And Functions
- Exported types: NetworkSettings, NetworkSettingsSummary.
- `NetworkSettings` fields include SandboxID, SandboxKey, Ports, Networks.
- `NetworkSettingsSummary` fields include Networks.
- Source comments highlight: NetworkSettings exposes the network settings in the api NetworkSettingsSummary provides a summary of container's networks in /containers/json

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `github.com/moby/moby/api/types/network`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/network_settings.go -->
