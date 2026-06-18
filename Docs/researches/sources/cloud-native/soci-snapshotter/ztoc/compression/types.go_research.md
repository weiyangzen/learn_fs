# sources/cloud-native/soci-snapshotter/ztoc/compression/types.go

## Purpose
`types.go` defines shared primitive types and compression algorithm string constants for zTOC compression support.

## Important APIs, Types, and Functions
`Offset` is `int64` and represents file sizes and offsets. `SpanID` is `int32`. Constants are `Gzip`, `Zstd`, `Uncompressed`, and `Unknown`, intentionally matching containerd `DiffCompression` names.

## Control Flow, State, and Persistence
No runtime behavior exists here. These types are persisted indirectly in zTOC structs and FlatBuffers.

## Dependencies and Integration Points
There are no imports. The constants are used by ztoc builders, zinfo factory functions, marshal/unmarshal conversion, tests, and CI-visible behavior for supported compression algorithms.

## Risks and Test Signals
Using plain strings makes unsupported values possible until factory checks run. Zstd is declared but zinfo creation is not implemented in this subset.
