# sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler.go

## Purpose
`ztoc_marshaler.go` serializes and deserializes zTOC structs to/from FlatBuffers and returns OCI descriptors for serialized zTOC blobs.

## Important APIs, Types, and Functions
Public APIs are `Marshal(ztoc)` and `Unmarshal(serializedZtoc)`. Internal conversion functions include `flatbufToZtoc`, `flatbufferToTOC`, `ztocToFlatbuffer`, `tocToFlatbuffer`, `prepareMetadataOffset`, `prepareXattrsOffset`, and `compressionAlgorithmToFlatbuf`. `ErrInvalidTOCEntry` signals overlapping/reordered invalid TOC entries during reconstruction.

## Control Flow, State, and Persistence
`Marshal` builds FlatBuffer bytes, creates a digest from those bytes, and returns an `io.Reader` plus descriptor size and digest. `Unmarshal` reads all bytes, recovers panics, parses root metadata, TOC, compression info, span digests, checkpoint bytes, and compression algorithm. TOC deserialization sorts entries by uncompressed offset and reconstructs tar header offsets by 512-byte alignment, rejecting overlap. Serialization sorts xattr keys for deterministic output.

## Dependencies and Integration Points
Dependencies include FlatBuffers generated ztoc code, compression types, `go-digest`, OCI descriptors, bytes/io, sort, strings, and time. It is the persistence boundary between in-memory zTOC and stored OCI/content blobs.

## Risks and Test Signals
`ModTime.UnmarshalText` errors are ignored, which can silently produce zero times for malformed data. `digest.Parse` errors for span digests are ignored. The panic recovery in `ztocToFlatbuffer` returns a generic error without cause. Tests validate positive round trips, invalid overlapping TOCs, deterministic digest/size, invalid format handling, xattr serialization, and extraction after round trip.
