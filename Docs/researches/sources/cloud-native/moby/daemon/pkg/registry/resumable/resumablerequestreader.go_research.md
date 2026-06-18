# sources/cloud-native/moby/daemon/pkg/registry/resumable/resumablerequestreader.go

## Purpose
Implements an `io.ReadCloser` that can transparently retry and resume HTTP response body reads by issuing Range requests after transport or body-read failures. It is used for registry pulls where network interruption should not restart an entire download.

## Important APIs, Types, And Functions
`requestReader` stores the `http.Client`, original request, byte offset (`lastRange`), total content size, current response, retry counters, and backoff duration. `NewRequestReader` starts without a response; `NewRequestReaderWithInitialResponse` continues from an already opened response. `Read`, `Close`, and `cleanUpResponse` implement the reader lifecycle.

## Control Flow
`Read` validates client/request, sets a `Range` header when resuming, optionally sleeps, performs the HTTP request when no response is active, and retries request creation errors until `maxFailures` is reached. It handles a final 416 response as EOF when the offset equals total size, rejects non-206 fresh resume responses, auto-detects total size from `ContentLength`, reads from the response body, advances `lastRange`, and suppresses non-EOF body-read errors so a later read can resume.

## State And Persistence
State is in-memory and mutable across reads: `lastRange`, `failures`, `totalSize`, `currentResponse`, and the original request header. Response bodies are closed whenever a request completes, errors, or is replaced. `Close` clears client/request references.

## Dependencies And Integration Points
Uses `net/http`, `io`, `time`, and containerd logging. It integrates with registry download code expecting a standard `io.ReadCloser`; callers must provide a request whose server supports byte ranges for resumed reads.

## Risks And Edge Cases
The code mutates the original request header, so reused requests can retain Range. The constructed range uses `bytes=start-totalSize`, which depends on server interpretation of an inclusive end. Non-EOF body errors are returned as nil after logging, so callers must continue reading for recovery. A zero or negative content length can fail auto-detection, and servers without Range support cause a hard error after the first resume attempt.

## Test Signals
The paired tests cover nil configuration, retry thresholds, read-error suppression, 416 EOF, servers without byte-range support, total-size auto-detection, normal reads, and initial-response reads.
