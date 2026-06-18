# sources/cloud-native/soci-snapshotter/ztoc/zinfo_builder.go

## Purpose
`zinfo_builder.go` builds the compression-info portion of a zTOC, including algorithm-specific checkpoints, compressed archive size, per-span digests, and max span ID.

## Important APIs, Types, and Functions
`ZinfoBuilder` defines `ZinfoFromFile(filename, spanSize)`. `gzipZinfoBuilder` and `tarZinfoBuilder` implement it via `compression.NewZinfoFromFile`. `getPerSpanDigests` computes a digest for each compressed span using `io.NewSectionReader`. `getFileSize` wraps `os.Stat`.

## Control Flow, State, and Persistence
The builder creates a zinfo object, stats file size, iterates span IDs from 0 through max span ID, digests each compressed span boundary reported by the zinfo, serializes checkpoints, and returns a `CompressionInfo`. Checkpoints and span digests become persisted zTOC fields.

## Dependencies and Integration Points
It depends on os/io, `go-digest`, and the compression package. `Builder.BuildZtoc` dispatches to these builders by algorithm.

## Risks and Test Signals
Digest generation trusts zinfo span boundaries. Error messages for digest failures omit the underlying `digest.FromReader` error. Tar and gzip are implemented; zstd requires external registration. ztoc tests validate consistency, extraction, and serialization using these builders.
