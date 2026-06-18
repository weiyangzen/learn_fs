## sources/cloud-native/containers-storage/pkg/fileutils/exists_unix.go

Purpose: Unix non-Windows, non-FreeBSD fast existence checks.

Important APIs/types/functions: `Exists` and `Lexists`.

Control flow: calls `unix.Faccessat(AT_FDCWD, path, F_OK, AT_EACCESS)` for follow mode and adds `AT_SYMLINK_NOFOLLOW` for link-object checks. Errors are wrapped as `os.PathError`.

State and persistence: read-only.

Dependencies and integration points: used throughout packages that need existence checks without full stat overhead.

Risks: `AT_EACCESS` checks using effective IDs; behavior may differ from `os.Stat` in unusual permission situations. Not used on FreeBSD because of compatibility handling.

Test signals: shared tests compare against `os.Stat`/`os.Lstat` and benchmarks evaluate performance.
