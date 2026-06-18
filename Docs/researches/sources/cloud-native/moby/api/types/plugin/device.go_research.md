<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/device.go -->
# sources/cloud-native/moby/api/types/plugin/device.go

## Purpose
Device device swagger:model Device

## Important APIs, Types, And Functions
- Exported types: Device.
- `Device` fields include Description, Name, Path, Settable.
- Wire JSON fields include Description, Name, Path, Settable.
- Source comments highlight: Device device swagger:model Device

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `capability_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/device.go -->
