# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/httpreadseeker.go

## Purpose
Provides a seekable, retrying `io.ReadCloser` wrapper over HTTP range requests.

## Important APIs, Types, And Functions
`newHTTPReadSeeker`, `httpReadSeeker.Read`, `Seek`, `Close`, and internal `reader` implement the behavior.

## Control Flow
The reader lazily opens the current offset using the supplied `open(offset)` callback. `Seek` closes any active body and updates the offset. `Read` advances the offset by bytes read; on `io.ErrUnexpectedEOF`, it closes the body and attempts to reopen at the current offset, allowing up to `maxRetry` no-progress retries. If the current offset equals known size, it returns an empty reader instead of making another HTTP request.

## State And Persistence
State is in-memory: size, current offset, active read closer, closed flag, and no-progress retry count.

## Dependencies And Integration Points
Used by `dockerFetcher.Fetch` and `FetchByDigest`. Depends on `errdefs` for closed/invalid seek errors and logging for close failures.

## Risks And Edge Cases
No synchronization is provided, so it is not safe for concurrent reads/seeks. Unknown-size readers cannot seek from end. Retrying unexpected EOF can mask transient connection drops but may loop until retry cap if the server repeatedly makes no progress.

## Test Signals
No dedicated test file in this subset, but fetcher tests exercise offset reopen behavior through `dockerFetcher.open`.
