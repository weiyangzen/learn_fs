# sources/cloud-native/containerd/core/transfer/streaming/writer.go

## Purpose
This file adapts a containerd object stream into an `io.WriteCloser` with window-based backpressure.

## Important APIs, Types, and Functions
`WriteByteStream` returns a `writeByteStream`. `writeByteStream.Write` sends `Data` messages while consuming atomic window credit. `Close` closes the stream.

## Control Flow
A goroutine receives `WindowUpdate` messages and increments remaining credit. `Write` waits for credit, slices input into at most `maxRead` and available-credit chunks, marshals each chunk, sends it, and decrements credit.

## State and Persistence
State is transient atomic credit, update channel, context, and stream reference.

## Dependencies and Integration Points
Used by archive export unmarshal and registry debug-log streaming. Depends on transfer protobuf types, typeurl, logging, and `core/streaming`.

## Risks
Context cancellation during a blocked write returns `io.ErrShortWrite`. Send errors end the write. The receiver goroutine logs unexpected message types and continues, so protocol misuse may not fail immediately.

## Test Signals
`runWriterFuzz` in `stream_test.go` validates byte preservation through this writer path.
