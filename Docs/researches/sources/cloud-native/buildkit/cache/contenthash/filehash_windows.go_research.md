# sources/cloud-native/buildkit/cache/contenthash/filehash_windows.go

Purpose: Windows stub for Unix-specific file hash metadata.

Important APIs/types/functions: `setUnixOpt` returns nil without mutating the stat.

Control flow: no-op.

State and persistence behavior: no state. Windows file hashes omit Unix uid/gid/device/xattr additions.

Dependencies and integration points: keeps `filehash.go` cross-platform while preserving a shared call site.

Risks: digest compatibility differs from Unix where uid/gid/xattrs/device metadata are included. This is expected but relevant for cross-platform cache comparisons.

Test signals: Windows compile/test coverage plus shared checksum tests where supported.
