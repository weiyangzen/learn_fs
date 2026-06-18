# sources/cloud-native/containerd/internal/cri/server/container_execsync_test.go

## Purpose
This unit test file validates helper behavior around synchronous exec output truncation and IO draining after exec process exit.

## Important APIs, Types, and Functions
Tests are `TestCWWrite`, `TestCWClose`, and `TestDrainExecSyncIO`. The local `fakeExecProcess` implements `containerd.Process` enough to record method calls such as `Delete`.

## Control Flow, State, and Persistence
`TestCWWrite` writes past the remaining byte cap and confirms the caller still receives full write counts while the underlying buffer is capped. `TestDrainExecSyncIO` uses timed channel closure to distinguish normal attach completion from timeout-driven process deletion. State is in-memory only.

## Dependencies and Integration Points
The tests depend on `cioutil.NewNopWriteCloser`, containerd process interfaces, and wall-clock timers. They directly exercise helper contracts used by `ExecSync`.

## Risks and Test Signals
The important signal is that output truncation is silent to the writer, matching CRI response-size behavior, and that stuck IO triggers `Delete` with process kill. Timer-based tests can be slow or flaky if durations are too tight, but the chosen values are broad.
