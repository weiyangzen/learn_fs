# sources/cloud-native/containers-storage/pkg/system/utimes_unix_test.go

Purpose: Linux/FreeBSD test coverage for `LUtimesNano`.

Important APIs/types/functions: `prepareFiles` creates a temp file, invalid path, and symlink; `TestLUtimesNano` updates symlink times and verifies target preservation.

Control flow: captures file mtime, sets symlink times to epoch, checks `os.Lstat` on symlink changed, checks `os.Stat` on target did not change, and expects an error for a missing path.

State/persistence: creates temporary files/symlinks and mutates symlink timestamps.

Dependencies/integration: supports both utime and stat tests.

Risks: compares seconds via `Unix()`, so subsecond precision issues are not covered. Filesystems with unusual symlink timestamp semantics may affect results.

Test signals: strong regression signal that `AT_SYMLINK_NOFOLLOW` is used and missing paths are not silently ignored.
