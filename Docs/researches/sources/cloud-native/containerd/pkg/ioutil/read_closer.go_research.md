# sources/cloud-native/containerd/pkg/ioutil/read_closer.go

Purpose: adapts an `io.Reader` into an `io.ReadCloser` whose `Close` can interrupt reads and whose background copy closes pipe ends when input drains.

Important APIs/types/functions: `wrapReadCloser` stores an `io.PipeReader` and `io.PipeWriter`; `NewWrapReadCloser(r)` starts a goroutine that copies `r` into the pipe writer, then closes both pipe ends; `Read` delegates to the pipe reader and maps `io.ErrClosedPipe` to `io.EOF`; `Close` closes both pipe ends and returns nil.

Control flow: construction immediately starts an asynchronous `io.Copy`. Consumers read from the pipe. Close interrupts future reads and unblocks the copy path through closed pipe errors.

State/persistence: in-memory pipe state and one goroutine per wrapper. No persistence.

Dependencies/integration: general helper for code expecting an `io.ReadCloser` around a plain reader.

Risks: caller must eventually close or drain the wrapper to avoid goroutine leakage, as documented. Errors from `io.Copy` and pipe closes are discarded. Closing both ends can hide the original underlying reader error.

Test signals: `read_closer_test.go` verifies sequential byte reads and EOF behavior after explicit close.
