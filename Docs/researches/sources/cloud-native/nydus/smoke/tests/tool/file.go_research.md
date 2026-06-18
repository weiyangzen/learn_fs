# sources/cloud-native/nydus/smoke/tests/tool/file.go

## Purpose
This helper captures filesystem metadata and content digests for comparing source layers with Nydus-mounted trees.

## Important APIs, Types, And Functions
`File` stores path, size, mode, rdev, symlink target, uid, gid, xattrs, and digest hash. `GetXattrs` lists and reads xattrs with lget semantics. `NewFile` uses `os.Lstat`, symlink reads, `syscall.Stat_t`, xattrs, and SHA256 digesting for regular files. `Compare` normalizes directory size to zero and asserts structural equality with `require.Equal`.

## Control Flow
Layer builders and verifiers call `NewFile` while walking source or mount trees. Comparisons are pairwise by target path.

## State And Persistence
The helper only reads filesystem state. It records an in-memory snapshot of metadata and content digests.

## Dependencies And Integration Points
It depends on Linux stat fields, `github.com/pkg/xattr`, OpenContainers digest, and `testify/require`. It is foundational for `tool.Layer.recordFileTree`, `tool.Nydusd.Verify`, and external backend comparison.

## Risks
It assumes `stat.Sys()` is `*syscall.Stat_t`, making it Unix/Linux-specific. Xattr availability and permission to read `security.*` xattrs can vary. Directory size normalization avoids filesystem-specific directory sizes but only inside `Compare`.

## Test Signals
A failed comparison pinpoints metadata/content drift between source and mounted Nydus files.
