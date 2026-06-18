# sources/cloud-native/moby/internal/testutil/archive.go

## Purpose
Computes the canonical digest of an uncompressed tar stream from a potentially compressed tar reader.

## Important APIs, Types, And Functions
- `UncompressedTarDigest(compressedTar io.Reader) (digest.Digest, error)` wraps `compression.DecompressStream`, streams decompressed bytes into `digest.Canonical.Digester`, and returns the digest.

## Control Flow
The function opens a decompressor, defers close, copies all decompressed data into the canonical hash, propagates decompression or copy errors, then returns the computed digest.

## State And Persistence
No persistent state. It streams data and allocates only decompressor/hash state.

## Dependencies And Integration Points
Uses `github.com/moby/go-archive/compression` and `github.com/opencontainers/go-digest`. Useful in tests comparing image/archive contents independent of compression.

## Risks And Edge Cases
All input is consumed. Invalid compression or read errors return errors. Digest is over raw uncompressed tar bytes, so tar metadata ordering and headers still affect the result.

## Test Signals
No direct tests in this item; callers can verify known compressed tar inputs produce expected canonical digests.
