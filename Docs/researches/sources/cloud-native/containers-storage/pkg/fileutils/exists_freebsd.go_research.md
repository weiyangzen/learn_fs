## sources/cloud-native/containers-storage/pkg/fileutils/exists_freebsd.go

Purpose: FreeBSD-specific fast existence checks.

Important APIs/types/functions: `Exists` and `Lexists`.

Control flow: `Exists` uses `unix.Faccessat` with follow behavior. `Lexists` uses `AT_SYMLINK_NOFOLLOW`, and falls back to `os.Lstat` on `EINVAL` for older FreeBSD kernels lacking that flag.

State and persistence: read-only filesystem checks.

Dependencies and integration points: used by generic file utilities and idtools directory creation. Errors are wrapped as `os.PathError` except the Lstat fallback.

Risks: FreeBSD fallback returns raw `os.Lstat` errors, so error shape differs from faccessat path. Access checks use `F_OK` only, not permissions.

Test signals: shared `exists_test.go` compares behavior against `os.Stat`/`os.Lstat` when run on FreeBSD.
