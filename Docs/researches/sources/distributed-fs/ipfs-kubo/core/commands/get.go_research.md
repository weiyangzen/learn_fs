<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/get.go

## Purpose

Implements `ipfs get`, fetching UnixFS content and writing it to disk as extracted files, tar archives, or gzip-compressed streams.

## Important APIs, Types, and Functions

`GetCmd` defines output, archive, compress, compression-level, and progress options. Helpers include `getCompressOptions`, `getOutPath`, `getWriter.Write`, `writeArchive`, `writeExtracted`, `fileArchive`, `newMaybeGzWriter`, `progressBarForReader`, and `makeProgressBar`.

## Control Flow

`PreRun` validates compression options. The handler resolves the path, fetches UnixFS content, sets response length, wraps content into a tar or gzip stream with `fileArchive`, closes the reader on context cancellation, sets content type, and emits the stream. The CLI post-run receives the stream, computes output path, resolves compression/archive/progress options, and writes either an archive file or extracted files through a tar extractor.

## State and Persistence Behavior

The handler is read-only against IPFS data but the CLI post-run writes files to the local filesystem using `os.Create` or tar extraction. It may fetch blocks from the network unless offline.

## Dependencies and Integration Points

Uses CoreAPI UnixFS, boxo files/tar, gzip, archive/tar PAX format, shared progress helpers, command response streams, and `cmdutils.PathOrCidPath`.

## Risks and Edge Cases

Compression level is valid only 1 through 9 when compression is enabled. Without `--archive` and without compression, data is still transported internally as tar and then extracted. Output path defaults to the final path component and can be overridden. Context cancellation closes the generated reader to stop background goroutines.

## Test Signals

`get_test.go` covers default and explicit output path selection. Missing tests include compression validation, archive filename suffixing, extraction errors, progress behavior, and context cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get.go -->
