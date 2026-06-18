<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/checkpoint/list.go -->
# sources/cloud-native/moby/api/types/checkpoint/list.go

## Purpose
Defines the compact checkpoint list item returned by checkpoint listing endpoints.

## Important APIs, Types, And Functions
- Exported types: Summary.
- `Summary` fields include Name.
- Source comments highlight: Summary represents the details of a checkpoint when listing endpoints.
- The only persisted API field is the checkpoint name; directory scoping is supplied by the client request options.

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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/checkpoint/list.go -->
