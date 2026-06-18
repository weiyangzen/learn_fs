# sources/cloud-native/moby/api/pkg/stdcopy/stdcopy.go

## Purpose
This package demultiplexes Docker/Moby attach, exec, and logs streams that combine stdout, stderr, and daemon error frames into one byte stream. `StdCopy` is the public reader-side counterpart to streams produced by `NewStdWriter` elsewhere in the package history/API, and its frame format is documented by client methods.

## Important APIs, types, and constants
`type StdType byte` identifies frame streams. `Stdin` is `0`, `Stdout` is `1`, `Stderr` is `2`, and `Systemerr` is `3`. The comments define compatibility semantics: stdin frames are routed to stdout, stderr frames go to the error writer, and system-error frames become returned errors.

The frame header length is `8` bytes. Byte `0` is the stream id. Bytes `4..7` hold a big-endian uint32 payload size. `startingBufLen` is `32 KiB + header + 1`, giving enough room for common frames plus overflow handling.

`StdCopy(destOut, destErr io.Writer, multiplexedSource io.Reader) (written int64, _ error)` reads frames, writes payloads to the selected destination, and returns the combined number of payload bytes written to stdout and stderr destinations.

## Control flow
The function maintains a reusable buffer and an `nr` count of buffered bytes. It first reads until at least one full 8-byte header is available. EOF before a complete header is treated as clean stream termination. It switches on the stream byte, selecting `destOut`, `destErr`, nil for `Systemerr`, or returning an unknown-stream error. It parses the frame size with `binary.BigEndian.Uint32`, grows the buffer if needed, then reads until the whole frame is buffered. EOF before a complete payload also returns nil error with bytes written so far. System-error frames return an error with the frame payload text. Normal frames are written once; short writes return `io.ErrShortWrite`. Any leftover buffered bytes after the consumed frame are shifted to the start before the next loop.

## State and persistence behavior
`StdCopy` has no package-level mutable state and no persistence. Its local buffer can grow to the largest seen frame and remains allocated until the function returns. It mutates destination writers by writing payload bytes and consumes the source reader.

## Dependencies
It depends only on standard `encoding/binary`, `errors`, `fmt`, and `io`. The code uses `errors.Is(err, io.EOF)` to tolerate wrapped EOFs. No context cancellation or deadlines are handled directly; those must come from the supplied reader.

## Integration points
Moby client methods for `ContainerAttach`, `ContainerLogs`, and `ContainerExecAttach` document this multiplex format and point users to `stdcopy.StdCopy`. Integration helpers call it to split container stdout/stderr into separate buffers. The package is part of the public API module, so third-party clients may rely on exact stream ids and EOF behavior.

## Risks and edge cases
If `destErr` is nil and a stderr frame arrives, the function will panic when calling `out.Write`; callers must pass a valid writer for streams they request or know will appear. A malicious or corrupt stream can advertise a very large frame size and force a large allocation. Truncated headers or payloads return nil rather than an error, which is compatibility-oriented but can hide transport truncation. Unknown stream ids reset the returned written count to `0`, unlike some later errors that return bytes already written. A writer that accepts partial data without returning an error triggers `io.ErrShortWrite`.

## Test signals
No sibling `stdcopy` test file is present in this subset. Indirect signals appear in client docs and integration helpers that use `StdCopy` for logs and attach results. High-value tests would include frame routing, stdin-to-stdout compatibility, system-error return, unknown stream id, large frame growth, short writes, nil destination behavior, and truncated frame EOF semantics.
