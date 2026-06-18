# sources/cloud-native/containers-storage/pkg/system/lchown.go

Purpose: wraps `syscall.Lchown` with retry-on-EINTR and path error wrapping.

Important APIs, types, and functions: `Lchown(name string, uid, gid int) error`.

Control flow: calls `syscall.Lchown`; while error is `EINTR`, retries. Non-nil final errors are wrapped in `os.PathError` with operation `lchown`.

State and persistence: mutates symlink/file ownership metadata without following symlinks.

Dependencies and integration points: depends on `os` and `syscall`; used by filesystem metadata application code.

Risks and edge cases: may retry forever if interrupted indefinitely. Permission and platform semantics are passed through as `PathError`.

Test signals: no direct tests in requested files.
