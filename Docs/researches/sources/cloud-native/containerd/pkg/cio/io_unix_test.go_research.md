<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix_test.go -->
# sources/cloud-native/containerd/pkg/cio/io_unix_test.go

Purpose: Unix tests for FIFO path creation, FIFO opening, terminal behavior, direct IO, and copy/close handling.

Important APIs and functions: `TestOpenFifos`, `TestOpenFifosWithTerminal`, `TestNewFIFOSetInDir`, and additional tests over FIFO/direct IO helpers.

Control flow and state: tests create temp FIFO roots, intentionally use invalid directories for error cases, open FIFO sets with/without terminal mode, and assert generated paths and pipe availability. Some tests exercise copy paths with actual FIFO readers/writers.

Dependencies and integration: depends on `containerd/fifo`, Unix syscalls, and testify assertions.

Risks and test signals: covers important cleanup/error cases, but timing-sensitive FIFO copy behavior still depends on goroutine scheduling and correct cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix_test.go -->
