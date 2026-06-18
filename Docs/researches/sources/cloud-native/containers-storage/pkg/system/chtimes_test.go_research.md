# sources/cloud-native/containers-storage/pkg/system/chtimes_test.go

Purpose: cross-platform tests for modification-time behavior of `Chtimes`.

Important APIs, types, and functions: `prepareTempFile` and `TestChtimes`.

Control flow: creates a temp file, calls `Chtimes` with epoch, before-epoch, after-epoch, and max-time combinations, and compares `os.FileInfo.ModTime`.

State and persistence: mutates temporary file timestamps.

Dependencies and integration points: depends on `os`, `filepath`, `testing`, and `time`; validates `chtimes.go` and platform `maxTime`.

Risks and edge cases: only mtime is checked because atime is OS-dependent. Max-time comparison truncates to seconds.

Test signals: confirms invalid atime/mtime clamping and valid mtime setting across platforms.
