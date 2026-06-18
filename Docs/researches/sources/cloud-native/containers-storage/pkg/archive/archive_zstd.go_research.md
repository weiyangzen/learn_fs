# sources/cloud-native/containers-storage/pkg/archive/archive_zstd.go

## Purpose
This file adds zstd compression and decompression support for archive streams when external `zstd` filtering is unavailable or when writing zstd streams.

## Important APIs
`zstdReader(buf)` creates a `zstd.Decoder`, wraps it with `io.NopCloser`, and returns it. `zstdWriter(dest)` returns a `zstd.Encoder` as an `io.WriteCloser`. Both use `github.com/klauspost/compress/zstd`.

## Control Flow and State
There is no package state. Reader and writer constructors allocate codec instances and return stream wrappers. Callers in `archive.go` own closing returned writers/readers.

## Dependencies and Integration Points
The file depends on `io` and `github.com/klauspost/compress/zstd`. `DecompressStream` calls `zstdReader` if the external filter path is not used. `CompressStream` calls `zstdWriter` for zstd output.

## Risks and Edge Cases
Codec construction errors are propagated. Because `zstdReader` uses `io.NopCloser`, closing the reader does not close an underlying source; `DecompressStream` wraps buffering separately in some paths, so ownership must be understood by callers.

## Test Signals
Generic compression tests in this subset do not explicitly exercise zstd. Coverage may exist elsewhere; within this subset, zstd support is mostly validated by build and integration with `CompressStream`/`DecompressStream`.
