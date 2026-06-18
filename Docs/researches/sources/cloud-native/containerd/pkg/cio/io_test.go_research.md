<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_test.go -->
# sources/cloud-native/containerd/pkg/cio/io_test.go

Purpose: platform-neutral tests for logging URI creator behavior.

Important APIs and functions: tests cover `BinaryIO`, `LogFile`, `LogURIGenerator`, and path handling with Windows/non-Windows prefixes.

Control flow and state: tests build creators with absolute and relative paths, call them with dummy IDs, compare stdout/stderr config strings, and parse generated URLs to validate scheme/path/query encoding.

Dependencies and integration: uses `runtime.GOOS` to adjust drive-letter expectations, testify assertions, and `net/url`.

Risks and test signals: protects against invalid file URI construction, especially Windows `file:///C:/...` handling and rejection of relative paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_test.go -->
