<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/common/error_response_ext.go -->
# sources/cloud-native/moby/api/types/common/error_response_ext.go

## Purpose
Adds Go `error` behavior to `ErrorResponse`.

## Important APIs, Types, And Functions
- Exported functions/methods: Error.
- The method returns the response message verbatim, so callers can use decoded API errors in normal Go error paths.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- String/error methods expose compact human-readable representations without mutating receiver state.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/common/error_response_ext.go -->
