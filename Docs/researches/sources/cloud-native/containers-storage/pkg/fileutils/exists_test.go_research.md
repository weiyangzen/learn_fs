## sources/cloud-native/containers-storage/pkg/fileutils/exists_test.go

Purpose: behavioral tests and benchmarks for `Exists` and `Lexists`.

Important APIs/types/functions: `TestExist`, `BenchmarkExists`, and `BenchmarkStat`.

Control flow: creates a temp directory, working symlink, and dangling symlink; compares `Exists` with `os.Stat` and `Lexists` with `os.Lstat`, including error type and Linux errno equality. Benchmarks compare faccess-based helpers with stat calls.

State and persistence: creates temporary symlinks and directories.

Dependencies and integration points: validates platform-specific existence helpers that are used by file utilities and idtools.

Risks: symlink creation may not be available or permitted on some platforms. One assertion compares `pathErr1.Path` to itself, so it does not actually validate path equality between errors.

Test signals: good coverage for follow versus no-follow semantics; local execution blocked by missing `go`.
