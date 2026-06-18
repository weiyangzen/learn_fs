<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/httpreadseeker.go -->
# sources/cloud-native/containerd/core/remotes/docker/httpreadseeker.go

## Purpose
Provides a reconnectable `io.ReadCloser`/`io.Seeker` abstraction for HTTP-backed content. It lazily opens a response at the current offset and can reopen after seeks or unexpected EOFs.

## Important APIs, Types, And Functions
- `httpReadSeeker` stores total size, current offset, active reader, open callback, closed flag, and retry count for no-progress errors.
- `newHTTPReadSeeker(size, open)` constructs the object.
- `Read` opens lazily, advances offset, retries on `io.ErrUnexpectedEOF`, and closes at EOF for progress tracking.
- `Seek` supports start/current/end when size is known, rejects negative offsets and invalid whence values, and closes existing bodies when moving.
- `reader` opens a new body unless offset is at/after known size, where it returns an empty reader.

## Control Flow
Reads call `reader`, then delegate to the active response body. On unexpected EOF, the current body is closed and a reopen is attempted at the same updated offset; repeated zero-progress failures are capped by `maxRetry`. Seeks mutate offset and clear the current body to force the next read to call the fetcher's open function.

## State And Persistence
All state is in-memory and per-reader. The active HTTP body is the only external resource; it is closed on EOF, explicit close, seek movement, and reconnect.

## Dependencies And Integration Points
Used by `dockerFetcher.Fetch` and `FetchByDigest` to expose seekable registry content to content copy paths. Uses containerd `errdefs` to classify closed/invalid seek errors and `log` for close failures.

## Risks And Edge Cases
Unknown-size readers cannot seek from end. Repeated unexpected EOF without progress eventually returns the error. Returning an empty reader at exact content size avoids unnecessary range requests but relies on caller size accounting.

## Test Signals
Covered indirectly by `fetcher_test.go` offset, EOF, and range scenarios. There is no dedicated test file for closed seek behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/httpreadseeker.go -->
