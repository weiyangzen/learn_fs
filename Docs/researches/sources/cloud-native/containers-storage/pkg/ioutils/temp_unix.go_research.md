# sources/cloud-native/containers-storage/pkg/ioutils/temp_unix.go

Purpose: provides the Unix implementation of `TempDir`.

Important APIs, types, and functions: `TempDir(dir, prefix string) (string, error)`.

Control flow: directly delegates to `os.MkdirTemp` and returns its path and error unchanged.

State and persistence: creates a temporary directory on disk, with lifecycle controlled by the caller.

Dependencies and integration points: depends on `os`; selected for all non-Windows builds. It gives package callers a platform-neutral API paired with the Windows long-path implementation.

Risks and edge cases: inherits all `os.MkdirTemp` behavior around permissions, naming, and cleanup. Unlike Windows, no path normalization or long-path prefix is applied.

Test signals: no direct test in the requested set; behavior is simple stdlib delegation and is indirectly used where callers create temp directories.
