<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/capability.go -->
# sources/cloud-native/moby/api/types/plugin/capability.go

## Purpose
Defines plugin capability identifiers and custom text/JSON marshal behavior.

## Important APIs, Types, And Functions
- Exported types: CapabilityID.
- Exported functions/methods: String, UnmarshalText, MarshalText.
- `CapabilityID` fields include Capability, Prefix, Version.
- The implementation keeps capability IDs compact and validates round-trips used by plugin privilege negotiation.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- String/error methods expose compact human-readable representations without mutating receiver state.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Imports: `bytes`, `encoding`, `fmt`, `strings`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/plugin/capability_test.go` exercises related behavior.
- Package-level tests include `capability_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/capability.go -->
