# sources/cloud-native/soci-snapshotter/util/ioutils/positiontrackerreader.go

Purpose: this file wraps an `io.Reader` and tracks how many bytes have been returned to callers.

Important API: `PositionTrackerReader` contains the underlying reader and current `pos`. `NewPositionTrackerReader` initializes position to zero. `Read` delegates to the underlying reader and increments `pos` by `n` even when an error is also returned. `CurrentPos` returns the accumulated byte count.

Control flow: the wrapper follows normal Go reader semantics: bytes read before an error still count. It does not inspect or transform data.

State and persistence: position is process-local mutable state. There is no locking, so concurrent reads are not safe unless the caller serializes access.

Dependencies and integration points: used wherever streamed reads need offset tracking, such as compression or archive processing code.

Risks: not concurrency-safe; no reset or seek support; position can diverge if the underlying reader has side-channel seeking. It increments on any positive `n`, including custom readers that return data with non-EOF errors.

Test signals: `positiontrackerreader_test.go` covers full read, short read, and read with `io.ErrUnexpectedEOF`.
