# sources/cloud-native/containers-storage/pkg/system/chtimes_windows_test.go

Purpose: validates Windows access-time behavior for `Chtimes`.

Important APIs, types, and functions: `TestChtimesWindows`.

Control flow: creates a temp file, calls `Chtimes` with epoch, before-epoch, after-epoch, and max-time combinations, then inspects `syscall.Win32FileAttributeData.LastAccessTime`.

State and persistence: mutates timestamps on a temporary file.

Dependencies and integration points: depends on `os`, `syscall`, `testing`, and `time`; uses common test helper and Windows stat structures.

Risks and edge cases: test calls `Chtimes` without checking returned errors, so failures may surface only through timestamp mismatch. It checks atime but not create time despite Windows-specific `setCTime`.

Test signals: confirms Windows atime clamping and valid/max value behavior.
