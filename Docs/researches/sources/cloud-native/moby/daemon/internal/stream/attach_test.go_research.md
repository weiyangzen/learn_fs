# sources/cloud-native/moby/daemon/internal/stream/attach_test.go

## Purpose
Regression-tests attach stream cancellation for stream combinations that have no active I/O. The goal is to ensure `CopyStreams` closes enough pipes for all goroutines to exit when the container context is canceled.

## Important APIs, Types, And Functions
`TestAttachNoIO` runs subtests for stdin only, stdout only, stderr only, stdout+stderr, stdin+stdout, stdin+stderr, and all three streams. `testStreamCopy` builds an `AttachConfig`, calls `NewConfig`, `AttachStreams`, `CopyStreams`, cancels the context, and waits for the returned error.

## Control Flow
Each subtest creates `io.Pipe` endpoints but does not write data. `testStreamCopy` first verifies that `CopyStreams` does not immediately report an unexpected error, then cancels the context and waits for either `context.Canceled` or a 10-second timeout.

## State And Persistence
All pipes and stream configs are in-memory and closed via defers. No external state is touched.

## Dependencies And Integration Points
Uses the same public attach APIs that daemon attach code uses. Assertions come from `gotest.tools/v3/assert`.

## Risks And Test Signals
This test does not validate byte transfer, detach keys, close-stdin semantics, or error propagation. Its strong signal is leak prevention: cancellation must unblock `io.Copy` across every requested stream shape.
