# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Ztoc.go

## Purpose
Generated FlatBuffers root table for serialized zTOC documents.

## Important APIs, Types, and Functions
`Ztoc` exposes version, build tool identifier, compressed and uncompressed archive sizes, nested `TOC`, and nested `CompressionInfo`. Builder helpers add all root fields and finish the table.

## Control Flow, State, and Persistence
This root table is the durable zTOC representation returned by `ztoc.Marshal` and consumed by `ztoc.Unmarshal`.

## Dependencies and Integration Points
It depends on `flatbuffers/go`, `TOC.go`, and `CompressionInfo.go`. It is central to zTOC storage in OCI/content-store descriptors.

## Risks and Test Signals
The generated API does not validate semantic consistency between root sizes, TOC entries, and compression info. Higher-level tests validate deterministic digest/size and successful extraction after round trip.
