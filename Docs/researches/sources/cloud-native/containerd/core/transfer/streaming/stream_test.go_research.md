# sources/cloud-native/containerd/core/transfer/streaming/stream_test.go

## Purpose
This file fuzz-tests transfer byte streaming correctness across send, receive, chained stream, writer, and EOF edge cases.

## Important APIs, Types, and Functions
`FuzzSendAndReceive` seeds representative byte slices. Helpers run send/receive, chained streams, and `WriteByteStream`. `TestSendReceiveEOFWithData` covers the `io.Reader` contract where a final read returns data and `io.EOF`. `pipeStream` and `testStream` implement an in-memory bidirectional stream.

## Control Flow
Each fuzz run copies expected bytes into a stream-backed writer/reader setup, reads all output, and compares byte equality. Chained tests route bytes through three stream conversions.

## State and Persistence
No persistence. In-memory channels simulate stream send/recv and closure.

## Dependencies and Integration Points
Exercises `SendStream`, `ReceiveStream`, `WriteByteStream`, `windowSize`, and `core/streaming.Stream` behavior.

## Risks
The in-memory stream is simpler than gRPC/TTRPC streams and may not expose transport buffering or cancellation races. Fuzzing still provides strong byte-preservation coverage.

## Test Signals
Strong signal for empty input, single byte, over-window data, repeated data, chained transfer, writer transfer, and EOF-with-data preservation.
