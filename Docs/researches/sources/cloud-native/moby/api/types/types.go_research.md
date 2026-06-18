<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/types.go -->
# sources/cloud-native/moby/api/types/types.go

## Purpose
MediaType represents an HTTP media type (MIME type) used in API Content-Type and Accept headers.

## Important APIs, Types, And Functions
- Exported types: MediaType.
- Constants: MediaTypeRawStream.
- Source comments highlight: MediaType represents an HTTP media type (MIME type) used in API Content-Type and Accept headers.

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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/types.go -->
