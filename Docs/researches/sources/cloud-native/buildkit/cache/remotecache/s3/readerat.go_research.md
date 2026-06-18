# sources/cloud-native/buildkit/cache/remotecache/s3/readerat.go

## Purpose

This file adapts offset-based object reads, such as S3 ranged `GetObject` requests, into a `ReaderAtCloser` implementation for BuildKit content providers.

## Important APIs, Types, and Functions

- `ReaderAtCloser` combines `io.ReaderAt` and `io.Closer`.
- `readerAtCloser` stores the current sequential read stream, current offset, optional native reader-at delegate, opener function, mutex, and closed flag.
- `toReaderAtCloser` constructs the adapter from an `open(offset)` callback.
- `ReadAt` opens or reuses an object stream at the requested offset.
- `Close` marks the adapter closed and closes any active stream.

## Control Flow and State

All operations are serialized by a mutex. `ReadAt` returns `io.EOF` after close. If the currently open stream is absent or its offset does not match the requested `off`, the adapter closes it and calls `open(off)`. If the stream itself implements `io.ReaderAt`, future reads delegate directly to it. Otherwise, the adapter reads sequentially into the caller's buffer and advances its tracked offset by bytes read.

The object state is in-memory and per reader. The underlying S3 object is not mutated.

## Dependencies and Integration Points

`s3.go` uses this adapter in `s3Client.ReaderAt`, passing an opener that performs ranged `GetObject` requests. It satisfies the `content.ReaderAt` expectations when combined with the size wrapper in `s3.go`.

## Risks and Edge Cases

The sequential read loop compares `nn == len(p)` after slicing `p = p[nn:]`, so full-buffer detection is fragile; normally it exits because subsequent reads return zero/EOF. The implementation serializes all reads, so concurrent random `ReadAt` calls will reopen streams often and may be inefficient. Returning `io.EOF` after close is simple but loses distinction between closed and natural EOF.

## Test Signals

No direct tests are included for this adapter. Its behavior is indirectly exercised by any S3 cache import path that materializes remote blobs.
