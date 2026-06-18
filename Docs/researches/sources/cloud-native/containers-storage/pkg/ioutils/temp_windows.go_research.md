# sources/cloud-native/containers-storage/pkg/ioutils/temp_windows.go

Purpose: provides the Windows implementation of `TempDir` that returns a long-path-safe directory name.

Important APIs, types, and functions: `TempDir(dir, prefix string) (string, error)`.

Control flow: calls `os.MkdirTemp`, returns any creation error, then wraps the resulting path with `longpath.AddPrefix`.

State and persistence: creates a temporary directory on disk; the returned path may include `\\?\` or `\\?\UNC\` to bypass legacy Windows path length limits.

Dependencies and integration points: depends on `os` and `github.com/containers/storage/pkg/longpath`. It is selected only on Windows and aligns temp directory handling with other Windows filesystem helpers.

Risks and edge cases: callers must tolerate long-path-prefixed strings. Cleanup APIs generally accept the prefix, but external tools may not. Directory removal remains caller-owned.

Test signals: covered indirectly by longpath tests for prefix construction; no direct `TempDir` Windows test in the requested files.
