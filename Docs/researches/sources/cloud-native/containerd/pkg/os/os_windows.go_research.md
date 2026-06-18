# sources/cloud-native/containerd/pkg/os/os_windows.go

Purpose: Windows path and symlink resolution for `RealOS`, using Win32 handle APIs to resolve files, directories, volume GUID paths, mount points, and UNC paths.

Important APIs/types/functions: `openPath` opens file or directory handles via `windows.CreateFile` with backup semantics. Constants define `GetFinalPathNameByHandle` flags. `getFinalPathNameByHandle` manages a pooled UTF-16 buffer and retries when larger buffers are needed. `resolvePath` opens a handle, prefers volume GUID final paths, falls back to DOS/UNC handling, and normalizes `\\?\UNC\` to `\\server\share`. `RealOS.ResolveSymbolicLink` evaluates symlinks with Windows-specific handling.

Control flow: resolution is handle-based to avoid fragile manual path parsing. UNC paths get fallback behavior when GUID lookup returns `ERROR_PATH_NOT_FOUND`.

State/persistence: reads filesystem and volume metadata; no writes.

Dependencies/integration: selected on Windows; uses `golang.org/x/sys/windows`. Supports higher-level code needing stable resolved paths, including volume mount points.

Risks: Windows path syntax is complex; extended-length, trailing-dot, mount point, and UNC edge cases can still differ from Go path functions. Handles must always be closed.

Test signals: `os_windows_test.go` outside this work item covers symlinks, VHD volume mount paths, and resolved path behavior.
