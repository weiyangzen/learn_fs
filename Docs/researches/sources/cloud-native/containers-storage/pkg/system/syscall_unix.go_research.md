# sources/cloud-native/containers-storage/pkg/system/syscall_unix.go

Purpose: Unix syscall convenience wrappers used by shared storage code.

Important APIs/types/functions: `Unmount(dest string) error`, `CommandLineToArgv(commandLine string) ([]string, error)`, and `IsEBUSY(err error) bool`.

Control flow: `Unmount` calls `unix.Unmount(dest, 0)`. `CommandLineToArgv` returns the whole string as a single element because Unix command-line parsing belongs to shells/callers. `IsEBUSY` uses `errors.Is`.

State/persistence: `Unmount` mutates mount state; the others are pure.

Dependencies/integration: `EnsureRemoveAll` uses `IsEBUSY` and mount cleanup uses `Unmount`; command-line parsing gives cross-platform callers a compile-compatible helper.

Risks: no unmount flags are exposed. The Unix `CommandLineToArgv` behavior is intentionally not shell-like and should not be used for parsing shell commands.

Test signals: tests should verify busy error recognition and unmount behavior through higher-level removal tests.
