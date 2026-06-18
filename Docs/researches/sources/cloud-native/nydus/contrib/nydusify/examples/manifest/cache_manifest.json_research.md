# sources/cloud-native/nydus/contrib/nydusify/examples/manifest/cache_manifest.json

## Purpose
This JSON file is a sample OCI image manifest representing a Nydus build-cache image. It illustrates how cache records are stored as alternating Nydus blob and bootstrap layers.

## Important APIs, Types, and Functions
Important fields are `mediaType`, `schemaVersion`, `config`, `layers`, and manifest-level `annotations`. Layers use Nydus blob media type `application/vnd.oci.image.layer.nydus.blob.v1` and bootstrap tar gzip media type with annotations such as `containerd.io/snapshot/nydus-bootstrap`, `containerd.io/snapshot/nydus-source-chainid`, `containerd.io/uncompressed`, and `containerd.io/snapshot/nydus-reference-blob-ids`.

## Control Flow
The file is static data consumed by humans or tests as an example. Cache import/export code in `pkg/cache` uses the same annotation conventions to reconstruct `Record` objects.

## State, Persistence, and Dependencies
It models persisted registry manifest state. The referenced digests and sizes are sample values.

## Integration Points
This sample aligns with the cache package’s `Manifest` and `Record` conversion logic. It also documents how Nydus build cache layers can reference shared blob IDs.

## Risks and Test Signals
Because it is static, it can drift from current annotation names or media types. It is not itself a test, but it is a strong format signal for maintainers and users.
