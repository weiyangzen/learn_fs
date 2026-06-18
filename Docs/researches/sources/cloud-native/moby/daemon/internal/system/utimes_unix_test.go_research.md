# sources/cloud-native/moby/daemon/internal/system/utimes_unix_test.go

## Purpose
Tests `LUtimesNano` on Linux/FreeBSD for symlink no-follow timestamp updates and missing-path errors.

## Important APIs, Types, And Functions
`prepareFiles` creates a real file, an invalid path, and a symlink to the file. `TestLUtimesNano` captures the target file's original stat, sets symlink times to zero, checks `os.Lstat` on the symlink, checks `os.Stat` on the target, and verifies missing-path error behavior.

## Control Flow
The test first validates that the symlink mtime differs after `LUtimesNano`, then confirms the target file mtime remains the same. It finally calls the function on a nonexistent path and expects an error.

## State And Persistence
All files live in a temporary test directory.

## Dependencies And Integration Points
Requires symlink support and the Unix `UtimesNanoAt` path. It validates metadata preservation behavior used by archive extraction.

## Risks And Test Signals
Comparisons use Unix seconds, so subsecond precision changes are not asserted. On platforms where `ENOSYS` is ignored, the symlink-change assertion could expose unsupported behavior.
