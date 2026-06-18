# sources/cloud-native/containers-storage/pkg/system/lstat_windows.go

Purpose: implements Windows `Lstat` using `os.Lstat` and package stat conversion.

Important APIs, types, and functions: `Lstat(path string) (*StatT, error)`.

Control flow: calls `os.Lstat`; returns error directly on failure; passes the `os.FileInfo` pointer to `fromStatT` on success.

State and persistence: reads filesystem metadata without following symlinks where Windows supports that distinction.

Dependencies and integration points: depends on `os`; selected on Windows. Uses Windows-specific `fromStatT` defined elsewhere.

Risks and edge cases: error wrapping differs from Unix implementation. Conversion takes a pointer to an interface value, matching this package's Windows stat helper expectations.

Test signals: no Windows lstat tests in requested files.
