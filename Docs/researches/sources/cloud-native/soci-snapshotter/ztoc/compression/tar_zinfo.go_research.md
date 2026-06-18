# sources/cloud-native/soci-snapshotter/ztoc/compression/tar_zinfo.go

## Purpose
`tar_zinfo.go` implements `Zinfo` for uncompressed tar streams. For tar, compressed and uncompressed offsets are identical, so checkpoint metadata only needs version, span size, and archive size.

## Important APIs, Types, and Functions
`TarZinfo` stores `version`, `spanSize`, and `size`. Constructors deserialize from FlatBuffers bytes or stat a tar file. Methods implement the full `Zinfo` interface: serialization, max span calculation, span size, offset-to-span mapping, buffer/file extraction, span boundary calculations, and no-op header verification.

## Control Flow, State, and Persistence
`Bytes` serializes fields with generated FlatBuffers builders. `newTarZinfo` recovers panics from malformed FlatBuffers access. Extraction from buffers slices relative to the requested span start; extraction from files uses `ReadAt`. Span boundaries are simple multiples of `spanSize`, with the final span ending at the supplied file size.

## Dependencies and Integration Points
The file depends on generated zinfo FlatBuffers, `flatbuffers/go`, os/io, and the shared compression types. It is selected by `NewZinfo` for `Uncompressed` and `Unknown` and by `NewZinfoFromFile` for `Uncompressed`.

## Risks and Test Signals
`MaxSpanID` can underflow when `size == 0` or `spanSize == 0`. `ExtractDataFromBuffer` does not bounds-check the computed slice and can panic on invalid offsets or sizes. `VerifyHeader` intentionally accepts all input because unknown/uncompressed is a catch-all. ztoc tests exercise uncompressed tar ztoc generation and extraction.
