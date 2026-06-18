# sources/cloud-native/soci-snapshotter/ztoc/toc_builder.go

## Purpose
`toc_builder.go` builds the tar table-of-contents portion of a zTOC for gzip, zstd, or uncompressed tar input by walking tar headers and recording file metadata and uncompressed offsets.

## Important APIs, Types, and Functions
`TarProvider` converts a compressed `*os.File` to an `io.Reader`. Providers exist for gzip, zstd, and tar. `TocBuilder` stores algorithm-to-provider registrations. Public methods include `NewTocBuilder`, `RegisterTarProvider`, `CheckCompressionAlgorithm`, and `TocFromFile`. Internal functions `getFileMetadata`, `metadataFromTarReader`, and `getType` do the actual tar traversal and file-type mapping.

## Control Flow, State, and Persistence
`TocFromFile` verifies provider support, opens the file, wraps it through the chosen provider, tracks uncompressed stream position with `ioutils.NewPositionTrackerReader`, and iterates `tar.Reader.Next`. For each header it stores file metadata, current payload offset, size, header offset, link/device/owner/time/PAX data, and updates the next tar header offset by aligning payload end to 512 bytes.

## Dependencies and Integration Points
Dependencies include `archive/tar`, gzip, zstd, `ioutils`, os/io, and compression offset types. `Builder.BuildZtoc` uses this TOC alongside compression info.

## Risks and Test Signals
Unsupported tar entry types fail the build. Provider/algorithm mismatch surfaces as reader errors. The TOC builder supports zstd metadata traversal, but default zTOC builder does not include a zstd zinfo builder. Tests cover gzip, zstd, uncompressed tar, unsupported algorithms, and mismatch failures.
