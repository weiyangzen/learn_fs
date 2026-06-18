## sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux_test.go

Purpose: Provides a benchmark for Linux fd counting.

Important API: `BenchmarkGetTotalUsedFds` loops over `GetTotalUsedFds(context.Background())` and reports allocations.

Control flow and state: It does not set up fd fixtures or validate counts; it measures whichever fast or slow path the current kernel supports.

Dependencies and integration: Uses Go benchmark support and the Linux implementation in-package.

Risks and gaps: This is performance coverage only. It will not detect off-by-one behavior between fast and slow paths, procfs read errors, or cancellation handling.

Persistence: None.
