# sources/cloud-native/moby/pkg/process/process_windows.go

Purpose: Windows implementation of process liveness and kill.

APIs and flow: `alive` opens the process with limited query rights, calls `GetExitCodeProcess`, closes the handle, and interprets successful query as alive. On query error it compares exit code with `STATUS_PENDING`. `kill` uses `os.FindProcess` and ignores `os.ErrProcessDone`.

State and dependencies: kernel process handles are opened and closed per call; no persistence.

Integration points: satisfies the common `Alive`/`Kill` dispatch contract on Windows.

Risks and tests: test coverage skips the exited-process case on Windows. The `GetExitCodeProcess` error branch is subtle and tied to Win32 API semantics.
