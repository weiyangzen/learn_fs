<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows_test.go -->
# sources/cloud-native/containerd/integration/client/helpers_windows_test.go

## Purpose
Supplies Windows test helper implementations matching the Unix helper API while using `cmd /c` command semantics and in-memory direct IO.

## APIs, Types, And Functions
The file defines `newLine`, `withExitStatus`, `withProcessArgs`, `withCat`, `withTrue`, `withExecExitStatus`, `withExecArgs`, `bytesBuffer`, and `newDirectIO`.

## Control Flow And State
Spec and exec helpers prefix process args with `cmd /c` where needed and use `more` as the cat equivalent. `bytesBuffer` wraps `bytes.Buffer` with a no-op `Close`. `newDirectIO` builds a `cio.DirectIO` from in-memory readers/writers instead of FIFOs, then wraps it in the shared `directIO` type.

## Persistence And Integration Points
The helper avoids filesystem FIFO state on Windows and is consumed by cross-platform container/task/exec tests. It integrates with Windows container command interpretation and CRLF output expectations.

## Risks And Test Signals
Command quoting and prefixing are the main risks because a small mismatch changes observed exit codes or stdout. In-memory IO can hide FIFO-specific behavior, so Windows-specific failures may differ from Unix direct IO failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows_test.go -->
