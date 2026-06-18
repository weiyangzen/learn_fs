<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/auxprogress/push.go -->
# sources/cloud-native/moby/api/types/auxprogress/push.go

## Purpose
Defines auxiliary progress payloads emitted while pushing images when the daemon selects a platform-
specific manifest from an index or reports missing referenced content.

## Important APIs, Types, And Functions
- Exported types: ManifestPushedInsteadOfIndex, ContentMissing.
- `ManifestPushedInsteadOfIndex` fields include ManifestPushedInsteadOfIndex, OriginalIndex, SelectedManifest.
- `ContentMissing` fields include ContentMissing, Desc.
- Wire JSON fields include contentMissing, desc, manifestPushedInsteadOfIndex, originalIndex, selectedManifest.
- Source comments highlight: ManifestPushedInsteadOfIndex is a note that is sent when a manifest is pushed instead of an index. ContentMissing is a note that is sent when push fails because the content is missing.
- These structs are embedded in `jsonstream.Message.Aux` and use OCI descriptors, so clients must treat the payload as API-visible registry/image metadata.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Imports: `github.com/opencontainers/image-spec/specs-go/v1`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses OCI image-spec descriptors/platform structures, so it participates in registry and content-store interoperability.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/auxprogress/push.go -->
