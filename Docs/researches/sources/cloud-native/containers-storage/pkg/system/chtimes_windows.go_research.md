# sources/cloud-native/containers-storage/pkg/system/chtimes_windows.go

Purpose: implements Windows creation-time setting after `os.Chtimes`.

Important APIs, types, and functions: `setCTime(path string, ctime time.Time) error`.

Control flow: converts the requested time to Windows timespec/filetime, opens the path with `FILE_WRITE_ATTRIBUTES` and backup semantics, defers handle close, and calls `windows.SetFileTime` with the creation time pointer.

State and persistence: mutates Windows file creation time metadata.

Dependencies and integration points: depends on `time` and `golang.org/x/sys/windows`; selected on Windows and called by common `Chtimes`.

Risks and edge cases: requires permission to write file attributes. Path conversion can fail. Directories need backup semantics, which are included.

Test signals: `chtimes_windows_test.go` validates access-time behavior under Windows; creation-time setting is not explicitly asserted in requested tests.
