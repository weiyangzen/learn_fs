# sources/distributed-fs/eos/namespace/utils/Stat.hh

## Purpose
Provides helpers to derive POSIX-like `mode_t` values from EOS namespace metadata entries. It bridges internal file/container metadata into stat/listing semantics.

## Important APIs, types, and functions
`modeFromMetadataEntry(const std::shared_ptr<IContainerMD>&)` returns the container mode and adds `S_XATTR` when `sys.acl` or `user.acl` exists. `modeFromMetadataEntry(const std::shared_ptr<IFileMD>&)` returns symlink mode for links, otherwise regular-file mode plus either explicit file flags or default `0444` plus owner write. It adds `EOS_TAPE_MODE_T` for files with a tape location.

## Control flow
Container handling is a simple mode read and xattr check. File handling first checks `isLink()`, then starts from `S_IFREG`, chooses explicit flags when non-zero or a default mode otherwise, and applies the tape bit if the file has `EOS_TAPE_FSID`.

## State and persistence
No state is modified. The computed mode is transient but user-visible through stat and listing operations.

## Dependencies and integration points
Depends on `common/FileSystem.hh`, namespace file/container interfaces, and `Mode.hh`. It integrates namespace metadata, ACL display, symlink handling, and tape-resident file presentation.

## Risks and test signals
The default permission branch for zero flags is policy-sensitive. Tests should cover directories with ACL xattrs, files with zero and non-zero flags, symlinks, tape locations, and interactions with `modeToBuffer()`.
