# sources/cloud-native/containers-storage/pkg/system/exitcode.go

Purpose: extracts process exit codes from `exec.ExitError` values.

Important APIs, types, and functions: `GetExitCode` and `ProcessExitCode`.

Control flow: `GetExitCode` type-asserts to `*exec.ExitError`, then to `syscall.WaitStatus`, and returns `ExitStatus`; otherwise returns error. `ProcessExitCode` returns zero for nil error, extracted code for recognized exit errors, and 127 when extraction fails.

State and persistence: no state or persistence.

Dependencies and integration points: depends on `fmt`, `os/exec`, and `syscall`. Used by command-running paths that need shell-like exit code handling.

Risks and edge cases: signal termination and non-Unix wait states may not map cleanly. Non-`ExitError` failures collapse to 127 in `ProcessExitCode`.

Test signals: no direct tests in requested files.
