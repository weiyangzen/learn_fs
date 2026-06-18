<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/manifest.go -->
# sources/cloud-native/moby/api/types/image/manifest.go

## Purpose
Defines manifest summary models for images, attestations, availability, size accounting, platform
data, unpacked state, and container references.

## Important APIs, Types, And Functions
- Exported types: ManifestKind, ManifestSummary, ImageProperties, AttestationProperties.
- Constants: ManifestKindImage, ManifestKindAttestation, ManifestKindUnknown.
- `ManifestSummary` fields include ID, Descriptor, Available, Size, Content, Total, Kind, ImageData, AttestationData.
- `ImageProperties` fields include Platform, Identity, Size, Unpacked, Containers.
- `AttestationProperties` fields include For.
- Wire JSON fields include AttestationData, Available, Containers, Content, Descriptor, For, ID, Identity, ImageData, Kind, Platform, Size, Total, Unpacked.
- It integrates OCI descriptors and digests with Moby's higher-level image listing and inspect workflows.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `github.com/opencontainers/go-digest`, `github.com/opencontainers/image-spec/specs-go/v1`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses OCI image-spec descriptors/platform structures, so it participates in registry and content-store interoperability.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/manifest.go -->
