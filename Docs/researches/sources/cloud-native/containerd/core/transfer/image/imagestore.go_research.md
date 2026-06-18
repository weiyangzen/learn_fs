# sources/cloud-native/containerd/core/transfer/image/imagestore.go

## Purpose
This file implements a local image store endpoint that can act as image source, destination, lookup target, platform filter, unpack request carrier, and transfer-proxy serializable object.

## Important APIs, Types, and Functions
`Store` holds image name, labels, platform filters, all-metadata mode, manifest limit, extra references, and unpack requests. Options include `WithImageLabels`, `WithPlatforms`, `WithManifestLimit`, `WithAllMetadata`, `WithNamedPrefix`, `WithDigestRef`, `WithExtraReference`, and `WithUnpack`. `Store`, `Get`, `Lookup`, `ImageFilter`, `Platforms`, `UnpackPlatforms`, `MarshalAny`, and `UnmarshalAny` implement transfer interfaces.

## Control Flow
`ImageFilter` wraps a child handler with platform filtering, mapped labels, all-metadata behavior, and manifest limits. `Store` resolves image records from explicit names or import annotations, creates digest and prefix-derived references, applies GC back-reference labels to extra refs when a primary image exists, then create-or-update loops in the image store. `Lookup` retrieves explicit references only. Marshal/unmarshal converts references, platforms, labels, and unpack configs to protobuf.

## State and Persistence
Persistent state is `images.Image` records in `images.Store`. Extra references may include `containerd.io/gc.bref.image` and immediate `containerd.io/gc.expire` labels so they are tied to the primary image.

## Dependencies and Integration Points
Integrates `core/images`, `core/images/archive` reference helpers, `remotes` filtering, `transfer/plugins`, `core/streaming`, protobuf transfer types, and OCI platform conversion.

## Risks
Reference derivation is subtle: annotation refs, containerd refs, OCI tag-only refs, digest refs, overwrite permission, and skip-named-digest have distinct behavior. `Store` mutates descriptor annotations by deleting the import ref-source marker. Prefix lookup for export is intentionally unimplemented.

## Test Signals
`imagestore_test.go` has table coverage for prefix, overwrite, tag-only, digest, skip digest, missing refs, no annotation, extra refs, GC labels, update-on-existing, and lookup behavior.
