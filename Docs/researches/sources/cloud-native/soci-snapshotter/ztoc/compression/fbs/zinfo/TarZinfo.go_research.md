# sources/cloud-native/soci-snapshotter/ztoc/compression/fbs/zinfo/TarZinfo.go

## Purpose
Generated FlatBuffers accessors for the tar zinfo schema used by `compression.TarZinfo`.

## Important APIs, Types, and Functions
`TarZinfo` wraps `flatbuffers.Table`. Root helpers read size-prefixed or normal roots. Accessors expose `Version()`, `SpanSize()`, and `Size()`, with mutators for each. Builder functions include `TarZinfoStart`, `TarZinfoAddVersion`, `TarZinfoAddSpanSize`, `TarZinfoAddSize`, and `TarZinfoEnd`.

## Control Flow, State, and Persistence
The file reads and writes fields within FlatBuffers byte buffers. Persistent representation is the flatbuffer byte layout consumed by `tar_zinfo.go`.

## Dependencies and Integration Points
It depends on `github.com/google/flatbuffers/go` and is generated code. `compression.TarZinfo.Bytes` writes through these builder functions; `newTarZinfo` reads through these accessors.

## Risks and Test Signals
Generated code assumes valid flatbuffer layout and may panic on malformed input; callers recover in `tar_zinfo.go`. Any schema change must regenerate this file and keep serializer/deserializer compatibility.
