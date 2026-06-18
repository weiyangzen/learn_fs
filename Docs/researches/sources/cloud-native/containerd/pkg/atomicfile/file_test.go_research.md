<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file_test.go -->
# sources/cloud-native/containerd/pkg/atomicfile/file_test.go

Purpose: validate atomicfile publish behavior for normal and concurrent writers.

Important APIs and functions: `TestFile` and `TestConcurrentWrites` exercise `New`, `Write` through `fmt.Fprint`, `Close`, and reading the destination path.

Control flow and state: tests create temp dirs, open one or two atomic writers to the same final path, write different contents, close in a controlled order, and assert the visible file contents after each close.

Dependencies and integration: uses testify assertions and standard filesystem operations.

Risks and test signals: confirms last closer wins without partial content. It does not test `Cancel`, post-close `ErrClosed`, sync/rename failure cleanup, or concurrent goroutine races during `Write`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file_test.go -->
