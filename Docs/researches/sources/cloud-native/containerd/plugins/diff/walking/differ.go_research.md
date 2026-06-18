# sources/cloud-native/containerd/plugins/diff/walking/differ.go

## Purpose
Implements the generic walking filesystem differ that compares mounted lower and upper filesystems and writes OCI layer tar diffs to the content store.

## Important APIs, Types, And Functions
`walkingDiff` holds a content store. `NewWalkingDiff` returns a `diff.Comparer`. `Compare` mounts lower and upper sets, writes `archive.WriteDiff`, handles compression/custom compressors, commits content, and returns descriptors. `uniqueRef` generates upload references.

## Control Flow
Compare applies diff options and source-date epoch, chooses compression from media type or custom compressor, mounts lower and read-only upper temp mounts, opens/truncates a content writer, streams a tar diff with optional source-date normalization, records the uncompressed digest label for compressed media, commits by writer digest, repairs missing labels on existing blobs, and returns content info.

## State And Persistence
Persists diff blobs and labels in the content store. Temporary mounts and ingest refs are cleaned up on errors; new references are aborted when open writes fail.

## Dependencies And Integration Points
Uses containerd mount helpers, archive diff generation, compression, epoch, content store, labels, OCI media types, and errdefs. It is the default generic differ on most Unix platforms and part of Windows fallback ordering.

## Risks
Custom compressor requires explicit media type. Existing-blob label repair assumes a computed uncompressed digest. Mount lifecycle and writer cleanup are critical for failures. This generic implementation may be slower than snapshotter-specific differs.

## Test Signals
No direct tests in this subset. It is heavily exercised by rootfs diff and content integration paths.
