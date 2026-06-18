# sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux.go

## Purpose
Adds Linux dm-verity formatting support for EROFS layers produced by the EROFS differ.

## Important APIs, Types, And Functions
`getDmverityOptions` selects dm-verity data/hash block sizes based on tar-index mode. `formatDmverityLayer` calculates aligned hash offsets, truncates the EROFS blob to include superblock/hash tree, calls `dmverity.Format`, and writes `DmverityMetadata`.

## Control Flow
Formatting skips when metadata already exists, stats the layer file, computes data blocks and hash offset, asks the verity library for hash-tree size, accounts for optional superblock size, preallocates the combined file, ensures a UUID, formats in place, marshals root hash and original hash offset to JSON metadata, and logs success.

## State And Persistence
Mutates the EROFS layer file by extending it with dm-verity structures and persists a sidecar metadata file used by the mount handler to open the verified block device.

## Dependencies And Integration Points
Depends on `containerd/go-dmverity`, `internal/dmverity`, UUIDs, JSON, and OS file operations. It pairs with the EROFS mount handler, which reads this metadata and opens `/dev/mapper` devices.

## Risks
Hash offset correctness is critical: metadata stores the superblock location, not the hash-tree start. File truncation is destructive if options are wrong. Tar-index layers require 512-byte blocks; using default 4096-byte blocks would make EROFS mounts fail.

## Test Signals
`dmverity_linux_test.go` verifies option selection, idempotency, missing-file errors, and block-aligned hash offsets when dm-verity is available.
