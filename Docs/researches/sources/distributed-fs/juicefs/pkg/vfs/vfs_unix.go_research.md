# sources/distributed-fs/juicefs/pkg/vfs/vfs_unix.go

## Purpose
This non-Windows file supplies Unix-specific VFS operations and constants: `O_ACCMODE`, `F_UNLCK`, statfs reporting, permission testing, setattr handling, advisory lock APIs, flock APIs, and Linux-style ioctl flag support.

## Important APIs, Types, and Functions
`Statfs` is a compact filesystem-capacity response type. `StatFS` maps `Meta.StatFS` values to `Total`, `Avail`, `Files`, and `Favail`. `accessTest` implements owner/group/other permission checks for internal nodes and root bypass. `Access` converts Unix `R_OK`, `W_OK`, and `X_OK` to JuiceFS mode masks and delegates to metadata for ordinary inodes. `setattrStr` formats trace output. `SetAttr` handles size changes through `Truncate`, permission checks for mtime changes, writer mtime updates, and metadata setattr. `Getlk`, `Setlk`, and `Flock` wrap metadata lock APIs while recording per-handle lock ownership. `Ioctl` supports flag get/set operations for immutable, append-only, and skip-trash mappings.

## Control Flow and State
`SetAttr` treats internal nodes as immutable metadata-backed pseudo-files and returns their internal attributes. For real files, it truncates first when size is set, then populates a partial attr object for mode, uid, gid, atime, and mtime. Mtime changes may update pending writer slice timestamps before `Meta.SetAttr` persists attributes. Lock operations validate type, reject special nodes, require a valid file handle, call metadata, then update handle-local lock bitfields and owners so `Flush`/`Release` can unlock later.

`Ioctl` distinguishes set from get by command direction bits. Set operations decode 4- or 8-byte input, enforce root-only control over protected flags when permission checks are active, translate supported filesystem flags into `meta.Attr.Flags`, and reject unknown bits. Get operations translate metadata flags back into ext-style flag buffers or `FS_IOC_FSGETXATTR` output.

## Dependencies and Integration Points
The file integrates with `golang.org/x/sys/unix` constants, Go `syscall`, JuiceFS `meta` attribute and lock APIs, and `utils.NativeEndian` for ioctl buffer encoding. `vfs.go` calls these methods through platform build selection.

## Risks and Edge Cases
The simple `accessTest` only checks a single gid, so supplemental group handling is delegated to metadata access for normal inodes. `SetAttr` has special logic around pure size changes; ordering is important to avoid losing length updates. Lock owner handling mixes owner and file handle for flock, and release/flush depends on these fields. `Ioctl` is strict about buffer sizes and unknown flag bits, which may differ from kernel callers' expectations.

## Test Signals
`TestAccessMode`, `TestSetattrStr`, `TestVFSBasic`, and `TestVFSLocks` cover access checks, formatting, setattr effects, flock/POSIX lock behavior, invalid lock types, invalid handles, and special-node rejection.
