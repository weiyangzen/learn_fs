<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_example_test.go -->
# sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_example_test.go

Purpose: documents and tests example usage of `stdcopymux.NewStdWriter` with Docker's `stdcopy.StdCopy` demultiplexer.

Important APIs and types: `ExampleNewStdWriter`.

Control flow: creates an `io.Pipe`, starts a goroutine demuxing to stdout/stderr, writes alternating stdout and stderr messages through mux writers, writes a `Systemerr` message, waits for demux completion, and verifies example output.

State and persistence: uses in-memory pipe and process stdout for example output.

Dependencies and integration: demonstrates interoperability between daemon `stdcopymux` writer and API `stdcopy` reader.

Risks: example sleeps to interleave output and writes to `os.Stdout`; timing changes could affect perceived behavior, though expected output is deterministic by write order.

Test signals: executable documentation that system-error frames terminate demuxing with an error message.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stdcopymux/stdcopy_example_test.go -->
