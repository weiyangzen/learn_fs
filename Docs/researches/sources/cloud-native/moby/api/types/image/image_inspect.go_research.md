<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/image_inspect.go -->
# sources/cloud-native/moby/api/types/image/image_inspect.go

## Purpose
Defines image inspect response structures including rootfs layers, OCI descriptors, storage driver
data, manifests, and signature identity metadata.

## Important APIs, Types, And Functions
- Exported types: RootFS, InspectResponse, SignatureTimestampType, SignatureType, KnownSignerIdentity.
- Constants: SignatureTimestampTlog, SignatureTimestampAuthority, SignatureTypeBundleV03, SignatureTypeSimpleSigningV1, KnownSignerDHI.
- `RootFS` fields include Type, Layers.
- `InspectResponse` fields include ID, RepoTags, RepoDigests, Comment, Created, Author, Config, Architecture, Variant, Os, OsVersion, Size, GraphDriver, RootFS, and others.
- Wire JSON fields include Descriptor, GraphDriver, Id, Identity, Manifests.
- Source comments highlight: RootFS returns Image's RootFS description including the layer IDs. InspectResponse contains response of Engine API: GET "/images/{name:.*}/json" SignatureTimestampType is the type of timestamp used in the signature.
- It is a high-fanout compatibility contract for CLI inspect output, API clients, and image provenance features.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `github.com/moby/docker-image-spec/specs-go/v1`, `github.com/moby/moby/api/types/storage`, `github.com/opencontainers/image-spec/specs-go/v1`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses OCI image-spec descriptors/platform structures, so it participates in registry and content-store interoperability.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/image_inspect.go -->
