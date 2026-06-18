# sources/cloud-native/containerd/core/transfer/streaming/stream.go

## Purpose
This file implements byte transfer over `streaming.Stream` using `Data` frames and window updates.

## Important APIs, Types, and Functions
Constants `maxRead` and `windowSize` define frame and credit sizes. `SendStream` reads from an `io.Reader` and sends data subject to remote credit. `ReceiveStream` returns an `io.Reader` backed by an `io.Pipe`. `GenerateID` creates stream IDs.

## Control Flow
`SendStream` starts one goroutine to receive `WindowUpdate` messages and another to read chunks and send `Data`. It honors credit and closes the stream at EOF. `ReceiveStream` periodically sends window updates, receives data frames, writes them into a pipe, and closes the pipe on EOF or error.

## State and Persistence
All state is transient: pooled buffers, window credit, pipes, and stream IDs. No durable storage.

## Dependencies and Integration Points
Used by archive import/export, registry debug logs, and transfer proxy progress/byte streaming. Depends on transfer protobuf types, typeurl, logging, crypto random, and `core/streaming`.

## Risks
Several TODOs note lack of explicit remote error messages. Read errors other than EOF are logged and end the stream. `GenerateID` ignores random read errors and uses nanosecond plus three random bytes, sufficient for low collision risk but not a durable identifier.

## Test Signals
`stream_test.go` fuzzes send/receive, chained streams, writer path, and EOF-with-data behavior.
