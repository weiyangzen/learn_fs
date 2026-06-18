<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/jsonstream/json_error.go -->
# sources/cloud-native/moby/api/types/jsonstream/json_error.go

## Purpose
Error wraps a concrete Code and Message, Code is an integer error code, Message is the error
message.

## Important APIs, Types, And Functions
- Exported types: Error.
- Exported functions/methods: Error.
- `Error` fields include Code, Message.
- Wire JSON fields include code, message.
- Source comments highlight: Error wraps a concrete Code and Message, Code is an integer error code, Message is the error message.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- String/error methods expose compact human-readable representations without mutating receiver state.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/jsonstream/json_error_test.go` exercises related behavior.
- Package-level tests include `json_error_test.go`, `message_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/jsonstream/json_error.go -->
