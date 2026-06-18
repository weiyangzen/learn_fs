# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/TOC.go

## Purpose
Generated FlatBuffers code for the TOC table that contains a vector of file metadata entries.

## Important APIs, Types, and Functions
`TOC.Metadata(obj, j)` initializes a `FileMetadata` at index `j`; `MetadataLength()` returns the vector length. Builder helpers start the TOC, add the metadata vector, start the vector, and end the table.

## Control Flow, State, and Persistence
The table is a container for ordered metadata offsets in a zTOC FlatBuffer. Serialization in `ztoc_marshaler.go` builds the vector in reverse as required by FlatBuffers.

## Dependencies and Integration Points
It depends on `flatbuffers/go` and `FileMetadata.go`. The zTOC root table references this table.

## Risks and Test Signals
Generated accessors rely on valid vector offsets. Marshaler tests check round-trip ordering and invalid overlap detection after deserialization.
