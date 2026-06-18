# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.go

## Purpose
`gzip_zinfo.go` is the Go cgo wrapper implementing the `Zinfo` interface for gzip streams using the C checkpoint engine.

## Important APIs, Types, and Functions
`GzipZinfo` wraps `*C.struct_gzip_zinfo`. Constructors `newGzipZinfo` and `newGzipZinfoFromFile` deserialize checkpoint bytes or generate checkpoints from a gzip file. Methods implement `Close`, `Bytes`, `MaxSpanID`, `SpanSize`, offset-to-span mapping, buffer/file extraction, compressed/uncompressed span boundaries, and gzip header verification. Private methods wrap C offset and bit accessors.

## Control Flow, State, and Persistence
The wrapper converts Go byte slices and strings to C pointers, delegates all checkpoint operations to C, and converts return codes into Go errors. `Bytes` allocates a Go byte slice of `get_blob_size` and asks C to serialize into it. Span start subtracts one compressed byte when a checkpoint has pending bits because raw inflate needs the byte before the checkpoint.

## Dependencies and Integration Points
It depends on cgo, `gzip_zinfo.h`, `libz.a`, Go `compress/gzip`, and `unsafe`. It is instantiated through `compression.NewZinfo` and `NewZinfoFromFile`, and consumed by ztoc builders and extraction paths.

## Risks and Test Signals
`Close` frees only `cZinfo` via `C.free`; because C allocates `list` separately, this may leak unless allocation/free behavior is adjusted elsewhere. `ExtractDataFromBuffer` returns a partially filled byte slice alongside an error when C extraction fails. `VerifyHeader` only checks that `gzip.NewReader` accepts the reader. Unit tests cover malformed zinfo bytes and guard clauses for empty buffers and negative/zero sizes; ztoc integration tests cover real extraction.
