# sources/cloud-native/containers-storage/pkg/system/chmod.go

Purpose: wraps `os.Chmod` with retry-on-interrupted-system-call behavior.

Important APIs, types, and functions: `Chmod(name string, mode os.FileMode) error`.

Control flow: calls `os.Chmod`; while the returned error matches `syscall.EINTR`, retries. Returns the final error.

State and persistence: mutates file mode on disk if successful. No package-level state.

Dependencies and integration points: depends on `errors`, `os`, and `syscall`. Used by filesystem code that wants robust chmod behavior around signals.

Risks and edge cases: retries indefinitely if `EINTR` repeats forever. Other transient errors are not retried. `errors.Is` is used for wrapped EINTR matching.

Test signals: no direct test in requested files.
