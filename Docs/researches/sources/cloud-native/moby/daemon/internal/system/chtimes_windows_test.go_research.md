# sources/cloud-native/moby/daemon/internal/system/chtimes_windows_test.go

## Purpose
Windows-specific tests for `Chtimes` access-time behavior using Win32 file attribute data.

## Important APIs, Types, And Functions
`TestChtimesATimeWindows` writes a temp file, calls `Chtimes`, reads `os.Stat`, and extracts `LastAccessTime.Nanoseconds()` from `syscall.Win32FileAttributeData`.

## Control Flow
The same timestamp scenarios as the Linux atime and cross-platform mtime tests are covered: epoch, pre-epoch clamping, valid post-epoch, and max time.

## State And Persistence
Only temporary file timestamps are mutated.

## Dependencies And Integration Points
Windows build only. It validates that the shared clamping logic and Windows `os.Chtimes` interaction set access time as expected.

## Risks And Test Signals
Creation time, the Windows-specific `setCTime` behavior, is not explicitly checked. Filesystem timestamp precision can vary, so max-time checks truncate to seconds. The main signal is parity with Unix atime clamping behavior.
