<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/jsonstream/progress.go -->
# sources/cloud-native/moby/api/types/jsonstream/progress.go

## Purpose
Progress describes a progress message in a JSON stream.

## Important APIs, Types, And Functions
- Exported types: Progress.
- `Progress` fields include Current, Total, Start, HideCounts, Units.
- Wire JSON fields include current, hidecounts, start, total, units.
- Source comments highlight: Progress describes a progress message in a JSON stream.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `json_error_test.go`, `message_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/jsonstream/progress.go -->
