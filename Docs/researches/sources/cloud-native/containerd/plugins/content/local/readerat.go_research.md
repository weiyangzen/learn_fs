<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/readerat.go -->
# sources/cloud-native/containerd/plugins/content/local/readerat.go

## Purpose
Filesystem-backed content.ReaderAt implementation for blobs.

## Important APIs, Types, And Functions
sizeReaderAt, OpenReader, ReadAt, Size, Close, and Reader.

## Control Flow
OpenReader stats and opens a blob path, returning ErrNotFound-wrapped errors for missing files. ReadAt delegates to os.File.ReadAt; Reader returns a LimitReader of the open file.

## State And Persistence
Holds an open file descriptor and immutable size captured at open time.

## Dependencies And Integration Points
Used by store.ReaderAt to serve blob reads through content.Store.

## Risks And Edge Cases
Reader() shares the same file offset as the underlying file, while ReadAt is offset-independent. Missing files are normalized to errdefs.ErrNotFound.

## Test Signals
Covered by content testsuite through ReaderAt operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/readerat.go -->
