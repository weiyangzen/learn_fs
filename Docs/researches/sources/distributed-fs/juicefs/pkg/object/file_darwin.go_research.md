# sources/distributed-fs/juicefs/pkg/object/file_darwin.go


Purpose: provides Darwin-specific timestamp helpers for local filesystem storage.

Important APIs and flow: `getAtime` extracts access time from `syscall.Stat_t.Atimespec` and falls back to `ModTime` if the stat shape is unexpected. `lchtimes` builds two `unix.Timespec` values, uses Darwin's `UTIME_OMIT` equivalent `Sec: -2, Nsec: -2` for atime, and calls `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW` so only symlink mtime changes.

State and persistence: modifies filesystem timestamps in place, specifically mtime without following symlinks.

Dependencies and integration: used by non-Windows `filestore.Chtimes` from `file_unix.go`. Depends on `golang.org/x/sys/unix` and Darwin syscall stat layout.

Risks: hard-coded `-2` mirrors SDK constants rather than using a named Darwin constant. Behavior depends on filesystem support for no-follow utimes. Atime argument is intentionally ignored.

Test signals: `file_unix_test.go` covers `lchtimes` preserving symlink atime and changing symlink mtime on non-Windows platforms; Darwin-specific execution depends on running tests on macOS.
