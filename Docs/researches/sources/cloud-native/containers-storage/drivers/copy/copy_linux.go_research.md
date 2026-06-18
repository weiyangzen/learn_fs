# sources/cloud-native/containers-storage/drivers/copy/copy_linux.go

## Purpose
`copy_linux.go` implements Linux/cgo directory and regular-file copy helpers for storage drivers. It preserves metadata, hardlinks, selected xattrs, special files, and directory mtimes, while trying accelerated data copy paths first.

## Important APIs, Types, And Functions
`Mode` selects `Content` or `Hardlink`. `CopyRegularToFile` tries `FICLONE`, then `copy_file_range`, then buffered copy. `CopyRegular` opens a destination exclusively and delegates. `DirCopy` walks a source tree and recreates entries. Helpers include `doCopyWithFileRange`, `legacyCopy`, `copyXattr`, `doCopyXattrs`, `fileID`, and `dirMtimeInfo`.

## Control Flow
`DirCopy` walks source paths, rebases each path to the destination, handles regular files, directories, symlinks, FIFOs, sockets, and devices, then applies ownership, xattrs, mode, and times. It records already-copied regular-file inode IDs so content-copy mode still preserves hardlink relationships. Directory mtimes are delayed until after children are copied.

## State And Persistence
The destination tree is fully materialized on disk. Runtime state tracks copied inode IDs and delayed directory timestamp updates. The `copyWithFileRange` and `copyWithFileClone` booleans are mutated to disable unsupported acceleration after errors.

## Dependencies And Integration Points
It depends on Linux syscalls, cgo `FICLONE`, `idtools`, `system`, `unshare`, and storage buffer pools. Overlay and other drivers can use it for layer copying.

## Risks
Accelerated copy fallback is subtle: `EXDEV`, `ENOSYS`, and ioctl failures adjust future behavior. Rootless mode silently skips device creation. Xattr copying is selective and rootless cannot copy `trusted.overlay.opaque`. `copy_file_range` loops until file size bytes are copied and assumes progress from the syscall.

## Test Signals
`copy_test.go` covers regular copies with and without acceleration flags, recursive metadata-preserving directory copy, and hardlink preservation.
