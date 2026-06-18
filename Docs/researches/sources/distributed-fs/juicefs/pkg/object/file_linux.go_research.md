# sources/distributed-fs/juicefs/pkg/object/file_linux.go


Purpose: provides Linux-specific timestamp helpers for local filesystem storage.

Important APIs and flow: `getAtime` extracts access time from `syscall.Stat_t.Atim`, falling back to mtime when unavailable. `lchtimes` uses `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW`, sets atime to `unix.UTIME_OMIT`, and sets mtime from the caller's value.

State and persistence: updates mtime on the filesystem path without following symlinks and leaves atime unchanged.

Dependencies and integration: used by `filestore.Chtimes` in `file_unix.go`. Depends on Linux stat fields and `golang.org/x/sys/unix`.

Risks: filesystem or kernel support for no-follow timestamp updates can vary. Atime input is ignored by design. Error wrapping returns an `os.PathError` with operation `"lchtimes"`.

Test signals: `TestLChtimes` in `file_unix_test.go` validates symlink mtime changes and atime preservation on non-Windows, including Linux.
