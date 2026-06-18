# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/FileMetadata.go

## Purpose
Generated FlatBuffers code for a single file metadata entry in a zTOC.

## Important APIs, Types, and Functions
Accessors expose name, type, uncompressed offset and size, link name, mode, uid/gid, uname/gname, mod time text, device major/minor, and xattr vector entries. Builder helpers add each field and start/end the xattr vector.

## Control Flow, State, and Persistence
This table persists tar-derived metadata. It does not include `TarHeaderOffset`; the deserializer reconstructs that offset by sorting entries and aligning data boundaries.

## Dependencies and Integration Points
It depends on `flatbuffers/go` and `Xattr.go`. `ztoc_marshaler.go` is the primary consumer.

## Risks and Test Signals
Because tar header offsets are reconstructed, malformed or overlapping entries can be detected only after sort/alignment in `flatbufferToTOC`. Generated mutators are available but not used by main code.
