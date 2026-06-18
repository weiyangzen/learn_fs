# sources/cloud-native/fuse-overlayfs/tests/test-mmap.sh

## Purpose
`tests/test-mmap.sh` validates that mmap-heavy dynamic linking/compilation works when lower layers can contain files with identical inode numbers on different backing filesystems.

## Important APIs, Types, And Functions
The script creates ext2 images with `truncate` and `mke2fs`, mounts them via `fuse2fs`, copies compiler shared-library dependencies split across the two filesystems, mounts fuse-overlayfs lower-only, and runs `gcc` with `LD_LIBRARY_PATH=mnt/`.

## Control Flow
It prepares two ext2-backed FUSE mounts, alternates copied `cc1` dependencies between them, overlays `ext2:ext1`, compiles a trivial C program against libraries resolved from the overlay, and cleans up all mounts/images.

## State And Persistence
Temporary ext2 image files, fuse2fs mounts, overlay mount, copied libraries, and compiled `a.out` are created and removed. No repository state is changed.

## Dependencies And Integration Points
Depends on `mke2fs`, `fuse2fs`, GCC, `ldd`, FUSE, and shared-library availability. It integrates with inode mapping, read/mmap behavior, and lower-only overlay mode.

## Risks
Highly environment-sensitive: missing fuse2fs, mke2fs, GCC, or library paths will fail the test. It assumes copied dependencies are enough for a trivial compile. Cleanup prints `FAILED` on trapped exits, which can be noisy if unmounts fail.

## Test Signals
Pass indicates same-number backing inodes across layers do not break mmap/dynamic-link workloads through the overlay.
