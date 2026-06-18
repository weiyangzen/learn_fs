<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/fs.go

Purpose: defines the filesystem provider interface and the real BeeGFS provider implementation for path normalization, file creation, ranged I/O, directory walking, metadata copying, atomic overwrite, and symlink reading.

Important APIs/types/functions: `Provider`, `NewFromMountPoint`, `NewFromPath`, `BeeGFS`, `GetMountPath`, `GetRelativePathWithinMount`, `Stat`, `Lstat`, `CreatePreallocatedFile`, `CreateWriteClose`, `Remove`, `Open`, `ReadFilePart`, `WriteFilePart`, `CreateDir`, `WalkDir`, `CopyXAttrsToFile`, `CopyContentsToFile`, `CopyOwnerAndMode`, `CopyTimestamps`, `OverwriteFile`, and `Readlink`.

Control flow: provider detection uses `statfs` magic for exact mount paths or walks parents comparing device IDs to find a mount point. BeeGFS methods join the mount point with in-mount paths and delegate to OS/unix syscalls. Xattr copy lists names, dynamically sizes the value buffer, and copies each value. Metadata copy uses chown/chmod and timestamp syscalls. `WalkDir` dispatches to normal or lexicographic walking based on options.

State and persistence: operations mutate the mounted filesystem. Preallocation uses truncate because BeeGFS lacks fallocate support, creating sparse files. Copy/overwrite methods affect content, xattrs, ownership, mode, and timestamps on disk.

Dependencies and integration points: depends on `golang.org/x/sys/unix`, standard filesystem/syscall packages, `common.go` ranged I/O helpers, and `walk.go` traversal. Other packages use `Provider` to abstract real, mock, and unmounted filesystems.

Risks: `GetRelativePathWithinMount` trims `MountPoint` as a string prefix, so `/mnt/beegfs2` with mount `/mnt/beegfs` can be misclassified. `CopyXAttrsToFile` allocates only 255 bytes for the full xattr name list, but Linux listxattr size can exceed that. Symlink detection in `CopyTimestamps` uses `linuxStat.Mode&syscall.DT_LNK`, which mixes file mode bits and dirent type constants. Sparse preallocation does not reserve storage.

Test signals: `fs_test.go` covers sparse file creation and ranged write/read/checksum on a temp directory using `BeeGFS{MountPoint: temp}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs.go -->
