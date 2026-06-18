# sources/cloud-native/containerd/core/transfer/streaming/reader.go

## Purpose
This file adapts a containerd object stream into an `io.ReadCloser` with explicit window-based flow control.

## Important APIs, Types, and Functions
`ReadByteStream` returns a `readByteStream`. `readByteStream.Read` receives `Data` messages and buffers overflow bytes. `Close` closes the underlying stream.

## Control Flow
A goroutine sends `WindowUpdate` messages until the local receive window reaches `windowSize`, then waits for reads to consume window. `Read` first drains `remaining`, checks context/error channels, receives a message, unmarshals it, copies data into the caller buffer, decreases window, and signals for another update when below threshold.

## State and Persistence
State is per-stream memory: window credit, buffered remaining bytes, update/error channels, and context.

## Dependencies and Integration Points
Consumes `core/streaming.Stream`, transfer protobuf `Data` and `WindowUpdate`, and `typeurl`. It is a lower-level helper for transfer stream endpoints.

## Risks
The window sender may block writing `errCh` if no reader consumes errors. Unknown message types return errors. Remaining-byte handling must preserve data when caller buffers are smaller than frames.

## Test Signals
Streaming fuzz tests cover byte roundtrips and edge cases through related send/receive helpers; direct `ReadByteStream` coverage is limited.
