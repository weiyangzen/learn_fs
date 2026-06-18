# sources/cloud-native/soci-snapshotter/util/ociutil/ociutil.go

## Purpose
`ociutil.go` contains OCI image document validation and platform de-duplication helpers copied or adapted from containerd behavior.

## Important APIs, Types, and Functions
`UnknownDocument` models unvalidated image JSON with raw fields for `mediaType`, `config`, `layers`, `manifests`, and schema-1 `fsLayers`. `ValidateMediaType(b, mt)` unmarshals JSON, rejects schema 1, and checks that the declared media type is consistent with manifest-vs-index fields and embedded `mediaType`. `DedupePlatforms(ps)` returns platforms with strict normalized duplicates removed while preserving first occurrence order.

## Control Flow, State, and Persistence
Validation is stateless and operates entirely on the input byte slice. `DedupePlatforms` builds a list of `platforms.Matcher` values as it scans; each new platform is normalized and compared against already accepted matchers.

## Dependencies and Integration Points
The package depends on `containerd/v2/core/images` for media-type classification, `containerd/platforms` for normalization and strict matching, and OCI image-spec platform structs. It integrates with code that consumes OCI manifests or indexes and wants containerd-compatible semantics.

## Risks and Test Signals
`ValidateMediaType` only checks high-level shape, not full manifest schema validity. It returns nil for unknown media types unless they classify as manifest or index. `DedupePlatforms` treats normalized aliases such as `x86_64` and `amd64` as duplicates; callers needing to preserve original spelling should use the returned first occurrence.
