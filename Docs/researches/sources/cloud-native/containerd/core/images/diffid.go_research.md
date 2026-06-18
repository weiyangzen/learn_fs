# sources/cloud-native/containerd/core/images/diffid.go

## Purpose

This file computes a layer DiffID, which is the digest of the uncompressed layer stream. DiffIDs are used to verify unpacked rootfs layers and to connect compressed content blobs to unpacked layer identity.

## Important APIs, Types, and Functions

`GetDiffID(ctx, cs, desc)` is the sole exported function. It returns the descriptor digest immediately for already-uncompressed Docker or OCI tar layers, consults the content info label `containerd.io/uncompressed` as a cache for compressed layers, and otherwise streams/decompresses the blob to compute the canonical digest. It uses `content.Store.Info`, `ReaderAt`, `content.NewReader`, and `compression.DecompressStream`.

## Control Flow

The function first checks media type. For compressed or otherwise non-fast-path descriptors, it loads content info, parses the cached uncompressed label if present, opens a reader, decompresses it, copies the uncompressed bytes into a canonical digest hash, and closes readers. It then stores the computed DiffID back into the content metadata labels via `cs.Update(ctx, info, "labels")`; update failure is only logged as a warning and does not fail the digest result.

## State and Persistence Behavior

The persistent state is the optional cache label written to the content store. Existing labels are preserved, and a nil labels map is initialized before writing. The source blob itself is not changed. The function closes both the decompressor and reader, with an explicit reader close checked before returning the digest.

## Dependencies and Integration Points

`GetDiffID` is a bridge between image descriptor media types, the content store, archive compression, OpenContainers digests, and containerd label conventions. It feeds rootfs verification, unpack workflows, and any code that needs the uncompressed identity of a packed layer.

## Risks and Edge Cases

Malformed cached label values fail through `digest.Parse`. Unknown or mislabeled compressed media types rely on `compression.DecompressStream` to detect compression. A content-update failure leaves the computation correct but uncached. The function returns the descriptor digest for uncompressed foreign/non-distributable layers without validating that the content is actually tar data.

## Test Signals

Good coverage includes uncompressed layer fast paths, cached-label parsing, cache miss computation for gzip/zstd layers, invalid cached labels, decompression errors, update failures logged but not returned, and ensuring computed labels are visible to subsequent calls.
