# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionAlgorithm.go

## Purpose
Generated FlatBuffers enum support for zTOC compression algorithms.

## Important APIs, Types, and Functions
`CompressionAlgorithm` is an `int8` enum with values for `Gzip`, `Zstd`, and `Uncompressed`. Maps translate enum values to names and names to enum values. `String()` returns the generated name.

## Control Flow, State, and Persistence
The enum value is persisted inside `CompressionInfo` FlatBuffers. Runtime conversion in `ztoc_marshaler.go` lowers the string when reading and performs case-insensitive lookup when writing.

## Dependencies and Integration Points
No external dependencies beyond generated Go code. It integrates with `CompressionInfo.go` and `ztoc_marshaler.go`.

## Risks and Test Signals
Generated names are capitalized, while SOCI compression constants are lowercase, so conversion helpers are required. Unknown algorithms fail during marshaling.
