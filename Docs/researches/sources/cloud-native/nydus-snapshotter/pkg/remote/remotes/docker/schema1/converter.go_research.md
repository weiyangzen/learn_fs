# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/schema1/converter.go

## Purpose
Converts deprecated Docker schema1 manifests into OCI or Docker schema2 manifests during pull while fetching layer blobs, calculating diff IDs, detecting empty layers, and writing converted config/manifest content.

## Important APIs, Types, And Functions
`Converter`, `NewConverter`, `Handle`, `Convert`, `UseDockerSchema2`, `ReadStripSignature`, `fetchManifest`, `fetchBlob`, `reuseLabelBlobState`, `schema1ManifestHistory`, `isEmptyLayer`, `stripSignature`, and `blobStateCalculator`.

## Control Flow
`Handle` first fetches and parses schema1 manifests, validates history/layer counts, and returns non-empty layer descriptors in reverse order. For layer descriptors, it fetches or reuses blobs, decompresses content through a tee, calculates uncompressed diff ID and empty status, updates labels, and records mappings. `Convert` builds OCI history/rootfs from schema1 history, creates config and manifest descriptors, adds GC labels, and writes both blobs. Signature stripping reads up to 8MB, decodes the protected JWS block, and reconstructs unsigned manifest bytes.

## State And Persistence
The converter holds the pulled manifest plus maps from compressed digest to blob state and diff ID to layer descriptor. It writes fetched blobs via content writers, updates labels, and writes converted config/manifest blobs.

## Dependencies And Integration Points
Integrates with containerd content store, image media types, compression helpers, remotes fetcher/ref keys, labels, errgroup, OCI specs, and Docker schema1 compatibility in `resolver.go`.

## Risks And Edge Cases
Schema1 is deprecated and fragile. Signature stripping depends on legacy JWS protected metadata. Existing blobs without labels require decompression to reconstruct state. Empty-layer detection from history is conservative. Manifest size is capped at 8MB.

## Test Signals
No direct tests in this subset, but resolver digest computation uses `ReadStripSignature` for schema1 manifests. Behavior is inherited from containerd-style conversion logic.
