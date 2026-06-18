<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/volume/prune_report.go -->
# sources/cloud-native/moby/api/types/volume/prune_report.go

## Purpose
PruneReport contains the response for Engine API: POST "/volumes/prune"

## Important APIs, Types, And Functions
- Exported types: PruneReport.
- `PruneReport` fields include VolumesDeleted, SpaceReclaimed.
- Source comments highlight: PruneReport contains the response for Engine API: POST "/volumes/prune"

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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/volume/prune_report.go -->
