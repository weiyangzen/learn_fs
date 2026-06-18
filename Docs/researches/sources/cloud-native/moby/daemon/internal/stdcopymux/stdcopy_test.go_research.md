<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_test.go -->
# sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_test.go

Purpose: tests mux writer framing and compatibility/error behavior with `stdcopy.StdCopy`.

Important APIs and types: `TestNewStdWriter`, `TestWriteWithUninitializedStdWriter`, `TestWriteWithNilBytes`, `TestWrite`, `errWriter`, `TestWriteWithWriterError`, `TestWriteDoesNotReturnNegativeWrittenBytes`, `getSrcBuffer`, `TestStdCopyWriteAndRead`, `customReader`, and many `StdCopy` error-path tests plus `BenchmarkWrite`.

Control flow: tests validate writer construction, nil/uninitialized writes, header-adjusted byte counts, negative count clamping, round-trip multiplexing of large stdout/stderr frames, read header/frame errors, truncated/corrupted frame behavior, invalid header handling, write errors, short writes, and system-error stream propagation. Benchmark repeatedly writes framed data to discard.

State and persistence: in-memory buffers/readers/writers only.

Dependencies and integration: tests `stdcopymux.NewStdWriter` against public `github.com/moby/moby/api/pkg/stdcopy.StdCopy`.

Risks: tests call into API package demuxer, so failures may reflect reader or writer changes. They do not exercise concurrent writes to the same underlying writer.

Test signals: strong coverage of mux frame format, byte accounting, and error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_test.go -->
