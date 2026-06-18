# sources/cloud-native/moby/daemon/internal/system/chtimes_test.go

## Purpose
Cross-platform tests for `Chtimes` modification-time behavior and timestamp clamping.

## Important APIs, Types, And Functions
`TestChtimesModTime` creates a temp file and checks `os.FileInfo.ModTime()` after calls to `Chtimes` with epoch, pre-epoch, valid post-epoch, and `unixMaxTime`.

## Control Flow
Subtests reuse the same file and verify expected mtime after each timestamp update. Invalid pre-epoch values are expected to be replaced by epoch. Max-time comparison truncates to seconds.

## State And Persistence
Only temporary file timestamps are changed.

## Dependencies And Integration Points
Uses standard `os`, `filepath`, and `time`. It validates the shared `Chtimes` logic independent of platform-specific atime/ctime tests.

## Risks And Test Signals
The test ignores atime because it is OS-dependent. It also does not test beyond-max input explicitly, only exactly `unixMaxTime`. Strong signal is that pre-epoch mtime is clamped instead of passed to `os.Chtimes`.
