<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/history_response_item.go -->
# sources/cloud-native/moby/api/types/image/history_response_item.go

## Purpose
HistoryResponseItem HistoryResponseItem individual image layer information in response to
ImageHistory operation swagger:model HistoryResponseItem

## Important APIs, Types, And Functions
- Exported types: HistoryResponseItem.
- `HistoryResponseItem` fields include Comment, Created, CreatedBy, ID, Size, Tags.
- Wire JSON fields include Comment, Created, CreatedBy, Id, Size, Tags.
- Source comments highlight: HistoryResponseItem HistoryResponseItem individual image layer information in response to ImageHistory operation swagger:model HistoryResponseItem

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/history_response_item.go -->
