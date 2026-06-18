# sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader_test.go

## Purpose
Validates the resumable request reader's error handling, retry limits, byte-range assumptions, EOF handling, and successful read paths.

## Important APIs, Types, And Functions
The tests instantiate `requestReader` directly for internal state cases and use `NewRequestReader`/`NewRequestReaderWithInitialResponse` for public constructors. `errorReaderCloser` simulates a body read failure. `httptest.Server` provides successful responses and range-support failures.

## Control Flow
Individual tests exercise nil client/request and bad total size, request-level failures under and over `maxFailures`, non-EOF body errors, 416 responses at the known end offset, a server that ignores Range, auto-detected content length, explicit total size, and a pre-opened initial response.

## State And Persistence
Each test owns fresh readers, servers, and requests. Readers are closed with `defer` where needed to close response bodies and clear internal references. No external state persists.

## Dependencies And Integration Points
Uses Go `net/http/httptest`, `io.ReadAll`, and `gotest.tools` assertions. It pinpoints behavior expected by registry download consumers rather than making real registry calls.

## Risks And Edge Cases
The timeout/backoff tests reduce `waitDuration` manually to avoid slow tests; production uses five-second waits. The "server does not support byte ranges" test checks only missing partial-content response semantics, not full RFC Range parsing.

## Test Signals
Passing tests confirm the reader can be used as a robust `io.ReadCloser`: transient request errors can be retried, terminal errors surface, non-EOF body errors trigger resumability, and successful reads return exact payload data.
