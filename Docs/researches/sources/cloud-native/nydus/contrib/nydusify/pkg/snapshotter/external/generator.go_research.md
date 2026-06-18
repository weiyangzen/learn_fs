<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator.go

## Purpose

This file converts backend chunk descriptions into the binary external metadata format consumed by nydusd/external snapshotter logic. It also carries through backend configuration and file attributes into a generated `Result`.

## Important APIs, Types, and Functions

`Result` contains generated `Meta`, `Backend`, and `Files`. `MetaGenerator` embeds header, chunk meta, object meta, and slices of chunk/object records. `NewGenerators` deduplicates object metadata by chunk object ID and msgpack-encodes object content. `(*Generators).Generate` wraps `MetaGenerator.Generate`. `(*MetaGenerator).Generate` lays out header, chunk table, object meta, object-offset table, and encoded object bodies.

## Control Flow

`NewGenerators` iterates chunks in input order. Each new `ObjectID` gets an object index and msgpack payload; every chunk receives a `ChunkOndisk` pointing at that object index and its object offset. Binary generation computes offsets using `unsafe.Sizeof`, detects fixed object entry sizes, and writes all structs with little-endian encoding.

## State and Persistence Behavior

No files are written here. The generated metadata byte slice is deterministic for a fixed chunk order and msgpack encoding. The generator mutates its embedded header/meta/offset fields as part of `Generate`.

## Dependencies and Integration Points

It depends on the external backend on-disk structs and constants, `encoding/binary`, `unsafe`, and `vmihailenco/msgpack/v5`. It is called by `external.Handle` before writing `MetaOutput`.

## Risks and Test Signals

Binary layout depends on Go struct layout and `unsafe.Sizeof`; any struct definition change can break compatibility. Object deduplication is by object ID only, so conflicting contents under the same ID are silently collapsed. Tests cover normal and empty generation but do not decode or version-verify the binary stream.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/generator.go -->
