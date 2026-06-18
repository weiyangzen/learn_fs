# sources/cloud-native/containerd/internal/dmverity/dmverity.go

## Purpose
Defines platform-neutral dm-verity options and metadata helpers shared by Linux and non-Linux implementations.

## Important APIs, Types, And Functions
`DmverityOptions` holds salt, hash algorithm, block sizes, data blocks, hash offset, hash type, superblock mode, and UUID. `DefaultDmverityOptions` returns sha256/4096-byte defaults. `MetadataPath`, `DevicePath`, `DmverityMetadata`, and `ReadMetadata` handle metadata file naming and JSON parsing.

## Control Flow
`ReadMetadata` maps a layer blob path to `*.dmverity`, reads JSON, unmarshals `roothash` and `hashoffset`, and rejects missing root hashes.

## State And Persistence
The metadata file is persistent sidecar state for dm-verity-enabled layer blobs. Options are caller-owned in memory.

## Dependencies And Integration Points
Uses JSON, filesystem reads, and string/path formatting. Linux code consumes these options when formatting/opening verity devices.

## Risks
Only root hash presence is validated here; hash format validation happens later. `MetadataPath` blindly appends `.dmverity` based on suffix and does not sanitize paths.

## Test Signals
`dmverity_test.go` covers metadata path/device path helpers, valid and invalid metadata JSON, and missing file/root hash cases.
