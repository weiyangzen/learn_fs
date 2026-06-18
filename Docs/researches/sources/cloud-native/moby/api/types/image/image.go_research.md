<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/image.go -->
# sources/cloud-native/moby/api/types/image/image.go

## Purpose
Metadata contains engine-local data about the image.

## Important APIs, Types, And Functions
- Exported types: Metadata, PruneReport.
- `Metadata` fields include LastTagTime.
- `PruneReport` fields include ImagesDeleted, SpaceReclaimed.
- Source comments highlight: Metadata contains engine-local data about the image. PruneReport contains the response for Engine API: POST "/images/prune"

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/image.go -->
