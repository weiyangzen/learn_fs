<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/hwaddr.go -->
# sources/cloud-native/moby/api/types/network/hwaddr.go

## Purpose
A HardwareAddr represents a physical hardware address.

## Important APIs, Types, And Functions
- Exported types: HardwareAddr.
- Exported functions/methods: UnmarshalText, MarshalText, String.
- Source comments highlight: A HardwareAddr represents a physical hardware address.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- String/error methods expose compact human-readable representations without mutating receiver state.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `encoding`, `fmt`, `net`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/network/hwaddr_test.go` exercises related behavior.
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/hwaddr.go -->
