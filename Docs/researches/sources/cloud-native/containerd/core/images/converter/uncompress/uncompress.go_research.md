# sources/cloud-native/containerd/core/images/converter/uncompress/uncompress.go

## Purpose

This file implements the image-converter function that rewrites compressed layer blobs into uncompressed tar layer blobs. It is used when a conversion pipeline wants OCI or Docker layer descriptors to point at plain tar content while retaining relevant content labels.

## Important APIs, Types, and Functions

`LayerConvertFunc` satisfies `converter.ConvertFunc`. It accepts a content store and descriptor, returns nil for non-layer or already-uncompressed layers, otherwise writes decompressed content back to the store and returns a descriptor with updated digest, size, and media type. `IsUncompressedType` classifies Docker and OCI tar layer media types that should not be decompressed again. `convertMediaType` maps gzip and zstd layer media types to their uncompressed equivalents, including deprecated non-distributable OCI layer forms.

## Control Flow

The converter gates on `images.IsLayerType` and `IsUncompressedType`, reads the source content metadata and blob, wraps the blob in a section reader of descriptor size, and passes it through `compression.DecompressStream`. It opens a deterministic writer reference derived from the source digest, truncates any prior interrupted writer state, copies the uncompressed stream, closes the decompressor, commits the writer, and then builds a descriptor from the original with new digest and size. `errdefs.IsAlreadyExists` is tolerated during commit so conversion can reuse already committed uncompressed blobs.

## State and Persistence Behavior

The only durable mutation is a new content-store blob under `convert-uncompress-from-<digest>`. Existing labels from the compressed blob are reused, but the uncompressed diff label `containerd.io/uncompressed` is removed because the new blob digest is already the uncompressed layer digest. The code mutates the `info.Labels` map returned by the content store in place, so callers should not assume that map remains unchanged.

## Dependencies and Integration Points

The function sits in `core/images/converter/uncompress` and integrates with the generic `converter` package, `core/content` stores, media-type helpers from `core/images`, archive compression detection, label constants, and OCI descriptors. It is relevant to image conversion, export, unpack, and distribution flows that need uncompressed layers.

## Risks and Edge Cases

Compression detection errors abort conversion. The copy path trusts `desc.Size` for the section reader, so mismatched descriptor sizes can truncate or fail reads. The commit passes size `0` and empty expected digest, relying on writer-computed values rather than explicit validation. Existing interrupted writer state is intentionally truncated, which is correct for this ref but assumes no concurrent conversion writer is using the same deterministic ref. Label map mutation can panic if `info.Labels` is nil before `delete`, depending on store behavior.

## Test Signals

Useful tests should cover nil result for non-layer and uncompressed media types, gzip and zstd conversion media-type rewrites, label preservation with `LabelUncompressed` removal, interrupted-writer truncation, already-exists commits, decompression failures, and descriptor digest/size correctness after conversion.
