# sources/cloud-native/containerd/core/images/mediatypes.go

## Purpose

This file centralizes containerd image media-type constants and classification helpers. It covers Docker schema 2, OCI, checkpoint, encrypted, EROFS, and in-toto media types, plus helpers that map descriptors to GC label classes.

## Important APIs, Types, and Functions

Constants define Docker layer/config/manifest/list, checkpoint/restore, schema1 manifest, encrypted layers, EROFS layers, and in-toto media types. `DiffCompression` reports layer compression as `gzip`, `zstd`, empty, or `unknown`, or returns `ErrNotImplemented` for non-layer types. `parseMediaTypes` splits a media type into base and sorted suffixes. Classification helpers are `IsNonDistributable`, `IsLayerType`, `IsDockerType`, `IsManifestType`, `IsIndexType`, `IsConfigType`, `IsKnownConfig`, and `IsAttestationType`. `ChildGCLabels` and `ChildGCLabelsFilterLayers` choose GC reference label keys for child descriptors.

## Control Flow

`DiffCompression` strips suffixes, switches on base media type, and rejects wrapped Docker media types by returning empty compression. OCI layer types inspect the final sorted suffix for gzip or zstd. `IsLayerType` accepts OCI layer prefixes, known Docker layer bases after suffix parsing, and EROFS. `ChildGCLabels` prioritizes referrer subject annotations, then config, manifest, layer, and generic content label keys.

## State and Persistence Behavior

There is no persistence here. The functions produce classification values and label key strings used by traversal and metadata code to persist GC references elsewhere.

## Dependencies and Integration Points

The file integrates with OCI image-spec media types, `errdefs.ErrNotImplemented`, and `AnnotationManifestSubject` from the images package. Its GC label output is consumed by `SetChildrenLabels` and metadata garbage collection reference scanning.

## Risks and Edge Cases

`parseMediaTypes` sorts suffixes, so `DiffCompression` looking at the last suffix can be order-insensitive but can also change semantics for complex wrappers where suffix order matters. Docker uncompressed media types return `unknown` because legacy data may be compressed despite the media type. Prefix-based OCI layer detection can classify future layer variants broadly. Deprecated non-distributable types are still supported for compatibility.

## Test Signals

Tests should cover Docker and OCI gzip/zstd/uncompressed variants, encrypted/wrapped suffix behavior, EROFS classification, non-distributable detection, attestation/config/index/manifest classification, referrer-specific GC labels, layer filtering, and `ErrNotImplemented` on non-layer media types.
