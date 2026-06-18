# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Xattr.go

## Purpose
Generated FlatBuffers code for a key/value xattr entry inside file metadata.

## Important APIs, Types, and Functions
`Xattr` exposes `Key()` and `Value()` byte slices plus builder functions to start, add key/value string offsets, and end the table.

## Control Flow, State, and Persistence
Xattrs are persisted as a vector of key/value tables. The marshaler sorts keys before serialization for deterministic output.

## Dependencies and Integration Points
It depends on `flatbuffers/go` and is used by `FileMetadata.go` and `ztoc_marshaler.go`.

## Risks and Test Signals
Only string-like byte values are represented. Deterministic ordering is enforced outside this generated file.
