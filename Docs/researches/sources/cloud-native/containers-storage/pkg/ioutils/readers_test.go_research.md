# sources/cloud-native/containers-storage/pkg/ioutils/readers_test.go

Purpose: tests reader helper wrappers from `readers.go`.

Important APIs, types, and functions: `errorReader`, `perpetualReader`, `TestReadCloserWrapperClose`, `TestReaderErrWrapperReadOnError`, `TestReaderErrWrapperRead`, `TestHashData`, and `TestCancelReadCloser`.

Control flow: tests build string/error/perpetual readers, wrap them with callbacks, and verify callbacks and returned errors. The cancel test creates a deadline context and reads repeatedly until `context.DeadlineExceeded` is returned by the wrapped pipe.

State and persistence: no persistence. Test state is callback booleans, in-memory readers, and deadline-controlled goroutines.

Dependencies and integration points: uses `context`, `fmt`, `io`, `strings`, `testing`, `time`, and `testify/assert`. It provides regression signals for consumers relying on cleanup callbacks and cancelable streams.

Risks and edge cases: the cancel test relies on timeouts and a perpetual reader, so it exercises cancellation but not early source EOF or explicit close races. It does not cover `OnEOFReader` or `WriterTo` preservation.

Test signals: verifies expected error propagation, callback invocation boundaries, fixed SHA-256 digest formatting, and cancelable reader context error behavior.
