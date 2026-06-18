<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/common/id_response.go -->
# sources/cloud-native/moby/api/types/common/id_response.go

## Purpose
Defines the common response body for create operations that return a generated identifier.

## Important APIs, Types, And Functions
- Exported types: IDResponse.
- `IDResponse` fields include ID.
- Wire JSON fields include Id.
- Source comments highlight: IDResponse Response to an API call that returns just an Id swagger:model IDResponse
- The JSON tag is `Id`, preserving Docker API wire compatibility even though the Go field is `ID`.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/common/id_response.go -->
