## sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_linux.go

Purpose: Counts file descriptors used by the current daemon process on Linux.

Important API: `GetTotalUsedFds(ctx context.Context) int` returns the count or `-1` on failure/cancellation.

Control flow: The function starts a containerd tracing span, builds `/proc/<pid>/fd`, and first tries the Linux 6.2 fast path where `stat.Size` on the proc fd directory contains the open descriptor count. If unavailable, it opens the directory and repeatedly calls `Readdirnames(100)`, checking `ctx.Done()` between batches. It logs and returns `-1` on open/read errors or cancellation. The slow path includes the descriptor for the opened `/proc/<pid>/fd` directory itself.

State and persistence: Reads kernel procfs state only. No persistence.

Dependencies and integration: Uses `x/sys/unix.Stat`, `os.Getpid`, containerd tracing/logging, and procfs. Useful for daemon diagnostics and resource monitoring.

Risks: Procfs semantics are Linux-version dependent. The fallback count can differ from the fast path by one because it opens the fd directory. Returning `-1` instead of an error requires callers to handle sentinel values.

Test signals: `filedescriptors_linux_test.go` benchmarks allocations/performance but does not assert correctness.
