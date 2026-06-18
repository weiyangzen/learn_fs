# sources/cloud-native/soci-snapshotter/util/testutil/tar.go

## Purpose
`tar.go` is a test fixture factory for tar, tar.gz, and zstd-compressed tar archives with configurable entries, metadata, ownership, modes, timestamps, xattrs, and gzip headers.

## Important APIs, Types, and Functions
`TarEntry` abstracts an entry that can append itself to a `tar.Writer`. `BuildTarOptions` carries name prefix and gzip header fields. `BuildTar`, `BuildTarGz`, and `BuildTarZstd` stream archives through `io.Pipe` from goroutines. `WriteTarToTempFile` persists a generated archive and also returns its bytes. `GetFilesAndContentsWithinTarGz`, `GetFilesAndContentsWithinTar`, and `getFilesAndContentsFromTarReader` inspect regular-file contents. Entry constructors include `Dir`, `File`, `Symlink`, `Link`, `Chardev`, `Blockdev`, and `Fifo`, with option types for directory and file metadata. `permAndExtraMode2TarMode` maps Go mode bits to tar mode bits, including suid, sgid, and sticky.

## Control Flow, State, and Persistence
Archive builders return readers immediately while goroutines write entries and close the pipe or close with errors. Temp-file output uses `os.CreateTemp`, `io.MultiWriter`, and leaves deletion to the caller. Metadata is embedded in tar headers; no other state is retained.

## Dependencies and Integration Points
The file depends on `archive/tar`, gzip, zstd, os/io primitives, and time. It is heavily used by ztoc tests to validate metadata construction, compression header edge cases, decompression, serialization, and benchmarks.

## Risks and Test Signals
Errors in builder goroutines surface when the consumer reads from the returned pipe. `Dir` panics if the directory name lacks a trailing slash; `File` returns an error if the file name has one. Hard link and device constructors use current time, which can affect deterministic archive bytes if compared directly. Tests use these helpers to exercise file types, large payloads, and gzip header variations.
