# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/converter.go

## Purpose
Normalizes image manifests whose config descriptor uses legacy `application/octet-stream`, rewriting them to Docker schema2 config media type and storing the corrected manifest in the content store.

## Important APIs, Types, And Functions
`LegacyConfigMediaType` identifies the legacy media type. `ConvertManifest(ctx, store, desc)` is the main function.

## Control Flow
The function only handles Docker schema2 and OCI image manifests. It reads the manifest blob, unmarshals to `ocispec.Manifest`, returns unchanged if config media type is already modern, rewrites the config media type, marshals indented JSON, recalculates digest and size, creates GC labels for config and layers, and writes the new blob under `remotes.MakeRefKey`.

## State And Persistence
Writes a new content blob and labels into the content store. The original manifest is not deleted; comments note later GC will remove it.

## Dependencies And Integration Points
Uses containerd content APIs, image media-type constants, OCI descriptors, and `remotes.MakeRefKey`. This is a compatibility bridge for pull/import paths that expect schema2 config media type.

## Risks And Edge Cases
Manifest lists/indexes are intentionally skipped. Invalid JSON or missing content fails. Rewriting changes manifest digest, so callers must use the returned descriptor.

## Test Signals
`converter_fuzz.go` fuzzes `ConvertManifest` against random descriptors and local content stores. No regular unit test in this subset asserts positive rewrite content.
