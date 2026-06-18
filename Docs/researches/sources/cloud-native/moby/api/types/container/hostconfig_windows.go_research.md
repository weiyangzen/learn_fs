<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/hostconfig_windows.go -->
# sources/cloud-native/moby/api/types/container/hostconfig_windows.go

## Purpose
Provides Windows-specific `NetworkMode` validation and classification.

## Important APIs, Types, And Functions
- Exported functions/methods: IsValid, IsBridge, IsHost, IsUserDefined, NetworkName.
- It intentionally rejects bridge/host behavior that is not valid for Windows container networking.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- Predicate/validation methods compare string modes or enum values against known constants and return booleans or formatted errors.

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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/hostconfig_windows.go -->
