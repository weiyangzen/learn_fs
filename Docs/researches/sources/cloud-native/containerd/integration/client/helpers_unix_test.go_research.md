<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix_test.go -->
# sources/cloud-native/containerd/integration/client/helpers_unix_test.go

## Purpose
Supplies Unix test helper implementations for process commands, exit statuses, newlines, exec argument mutation, and direct FIFO-backed IO.

## APIs, Types, And Functions
The file defines `newLine`, `withExitStatus`, `withProcessArgs`, `withCat`, `withTrue`, `withExecExitStatus`, `withExecArgs`, and `newDirectIO`.

## Control Flow And State
Spec options mutate OCI process args to shell commands such as `sh -c "exit N"`, `cat`, and `true`, or delegate to `oci.WithProcessArgs`. Exec helpers mutate an existing `specs.Process`. `newDirectIO` creates a FIFO set via `cio.NewFIFOSetInDir`, wraps it with `cio.NewDirectIO`, and returns the test package's `directIO` wrapper.

## Persistence And Integration Points
The direct IO helper creates FIFO directories/files that must be closed/deleted by tests. The command helpers are consumed by container lifecycle tests and map generic test intent to Unix process semantics.

## Risks And Test Signals
Incorrect command translation would invalidate many cross-platform assertions about exit codes, line endings, stdin/stdout, and exec behavior. FIFO leaks or missed `Delete` calls are detectable through tests hanging or filesystem cleanup failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix_test.go -->
