<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/jsonstream/message.go -->
# sources/cloud-native/moby/api/types/jsonstream/message.go

## Purpose
Message defines a message struct.

## Important APIs, Types, And Functions
- Exported types: Message.
- `Message` fields include Stream, Status, Progress, ID, Error, Aux.
- Wire JSON fields include aux, errorDetail, id, progressDetail, status, stream.
- Source comments highlight: Message defines a message struct.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.

## Dependencies And Integration Points
- Imports: `encoding/json`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/jsonstream/message_test.go` exercises related behavior.
- Package-level tests include `json_error_test.go`, `message_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/jsonstream/message.go -->
