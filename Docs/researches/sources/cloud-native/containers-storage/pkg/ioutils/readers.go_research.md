# sources/cloud-native/containers-storage/pkg/ioutils/readers.go

Purpose: defines small reader wrappers for close callbacks, error callbacks, SHA-256 hashing, EOF hooks, and context-cancelable reads.

Important APIs, types, and functions: `NewReadCloserWrapper`, `NewReaderErrWrapper`, `HashData`, `OnEOFReader`, `NewCancelReadCloser`, and methods on `readCloserWrapper`, `readWriteToCloserWrapper`, `readerErrWrapper`, and `cancelReadCloser`.

Control flow: `NewReadCloserWrapper` preserves `io.WriterTo` when the wrapped reader has it. `readerErrWrapper.Read` invokes a callback on any non-nil read error. `HashData` streams into a SHA-256 hash and returns a `sha256:` string. `OnEOFReader` runs its function once on EOF or close. `NewCancelReadCloser` copies the source into an `io.Pipe`; one goroutine transfers bytes, another closes the pipe with the context error when canceled.

State and persistence: no persistence. Runtime state includes once-only callback state in `OnEOFReader.Fn`, pipe reader/writer state, and a private done context for cancelable reads.

Dependencies and integration points: uses `context`, `crypto/sha256`, `encoding/hex`, and `io`. It supports higher-level storage code that needs deterministic cleanup of streamed resources and cancellation of blocking readers.

Risks and edge cases: `NewCancelReadCloser.Close` closes the wrapper with `io.EOF` but does not directly close the underlying reader; the copier goroutine closes it after copy exits. Callback wrappers are not concurrency-protected. `readerErrWrapper` fires on `io.EOF` as well as real errors.

Test signals: `readers_test.go` covers close callback, error callback, no callback on successful read, hash output, and context-deadline cancellation of a perpetual reader.
