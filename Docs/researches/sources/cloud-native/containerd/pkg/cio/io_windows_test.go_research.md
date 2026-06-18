<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows_test.go -->
# sources/cloud-native/containerd/pkg/cio/io_windows_test.go

Purpose: Windows tests for named-pipe FIFOSet creation and Windows log URI behavior.

Important APIs and functions: `TestNewFifoSetInDir_NoTerminal`, `TestNewFifoSetInDir_Terminal`, `TestLogFileBackslash`, and `TestLogURIGenerator`.

Control flow and state: tests create FIFO sets for terminal and non-terminal modes, assert stdin/stdout/stderr presence or absence, and verify backslash paths normalize to valid file URLs.

Dependencies and integration: uses testify and URL generation helpers from `cio`.

Risks and test signals: specifically protects the HCSShim terminal contract that stderr must be empty, and URI normalization for Windows paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows_test.go -->
