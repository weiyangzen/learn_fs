<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_linux.go -->
# sources/cloud-native/containers-storage/drivers/vfs/copy_linux.go

## Purpose
This Linux-specific VFS helper copies a parent layer directory into a child layer using the optimized driver copy package.

## Important APIs, Types, And Functions
`dirCopy(srcDir, dstDir string) error` calls `copy.DirCopy(srcDir, dstDir, copy.Content, true)`.

## Control Flow
The helper delegates all traversal and copy behavior to the copy package.

## State And Persistence
It materializes a full copy of parent contents in the destination VFS layer directory.

## Dependencies And Integration Points
`driver.go` calls `dirCopy` during `Create` when a parent exists. Linux builds use this implementation instead of tar-based copying.

## Risks And Test Signals
Copy semantics are determined by `drivers/copy`; permissions, xattrs, hardlinks, and special files must remain consistent with graphdriver expectations. VFS graphdriver tests exercise parent snapshot creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/vfs/copy_linux.go -->
