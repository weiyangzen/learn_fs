<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/summary.go -->
# sources/cloud-native/moby/api/types/image/summary.go

## Purpose
Defines Docker image API model API surface for Summary.

## Important APIs, Types, And Functions
- Exported types: Summary.
- `Summary` fields include Containers, Created, ID, Labels, ParentID, Descriptor, Manifests, RepoDigests, RepoTags, SharedSize, Size.
- Wire JSON fields include Containers, Created, Descriptor, Id, Labels, Manifests, ParentId, RepoDigests, RepoTags, SharedSize, Size.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/summary.go -->
