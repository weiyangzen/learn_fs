# sources/cloud-native/containers-storage/pkg/ioutils/writeflusher.go

Purpose: wraps a writer and optional flusher so every write is followed by a flush and close can stop future writes.

Important APIs, types, and functions: `WriteFlusher`, `NewWriteFlusher`, `Write`, `Flush`, `Flushed`, `Close`, the private `flusher` interface, and `errWriteFlusherClosed`.

Control flow: `Write` checks the `closed` channel, writes to the underlying writer, then calls `Flush` regardless of write error. `Flush` closes the `flushed` channel once and invokes the underlying flusher if still open. `Close` uses a mutex to close the `closed` channel once and returns `io.EOF` if already closed.

State and persistence: no persistence. State is channel-based lifecycle tracking plus a `sync.Once` that records the first flush event.

Dependencies and integration points: depends on `io` and `sync`. It integrates with streaming HTTP-like paths where immediate flushing and post-close write suppression are needed. `NopFlusher` from `writers.go` is used when the writer lacks `Flush`.

Risks and edge cases: `Flushed` is explicitly racy and only suitable for weak observation. `Write` flushes even after a partial/error write. `Close` does not close the underlying writer; it only closes the wrapper.

Test signals: no requested direct tests for `WriteFlusher`; behavior should be covered by callers or future tests around flush-on-write and close races.
