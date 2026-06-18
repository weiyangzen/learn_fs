# Research: sources/cloud-native/buildkit/cmd/buildctl/main_unix.go

Purpose: applies Unix-specific process initialization for `buildctl` by zeroing the process umask and telling fsutil copy that the umask is zero.

Important APIs and flow: the `init` function calls `syscall.Umask(0)` and sets `copy.UmaskIsZero = true`. This affects file mode behavior for operations that rely on fsutil copy semantics.

State and dependencies: changes process-global umask on non-Windows builds. It depends on `syscall` and `github.com/tonistiigi/fsutil/copy`.

Risks and test signals: a process-wide umask change can affect any files created by buildctl commands, though this is intentional for reproducible copy/export behavior. There are no direct tests in this subset.
