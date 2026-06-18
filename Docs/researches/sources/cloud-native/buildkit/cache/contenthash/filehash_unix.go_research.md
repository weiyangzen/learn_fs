# sources/cloud-native/buildkit/cache/contenthash/filehash_unix.go

Purpose: Unix metadata enrichment for file hashing.

Important APIs/types/functions: `setUnixOpt(path, fi, stat)`.

Control flow: casts `fi.Sys()` to `*syscall.Stat_t`, copies uid/gid, records major/minor device numbers for block/character devices, lists xattrs with `sysx.LListxattr`, and reads each xattr with `sysx.LGetxattr` into the fsutil stat.

State and persistence behavior: no direct persistence. The enriched stat feeds tar-header hashing and therefore persisted `CacheRecord` digests.

Dependencies and integration points: uses containerd continuity `sysx`, fsutil stat types, syscall stat data, and `golang.org/x/sys/unix` device helpers.

Risks: assumes `fi.Sys()` is `*syscall.Stat_t`; incompatible FileInfo implementations will panic. Xattr read errors are ignored per attribute after a successful list, which can hide volatile xattr races.

Test signals: Unix contenthash tests exercise normal uid/gid and mode behavior; device/xattr-specific coverage is indirect or external.
