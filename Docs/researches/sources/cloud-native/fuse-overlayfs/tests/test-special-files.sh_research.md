# sources/cloud-native/fuse-overlayfs/tests/test-special-files.sh

## Purpose
`tests/test-special-files.sh` validates special-file creation and preservation plus fallocate, statfs, chmod, chown, truncate, timestamp updates, and directory metadata updates.

## Important APIs, Types, And Functions
The script checks host `mknod` capability, then uses `mknod`, `mkfifo`, Python Unix sockets, `fallocate`, `stat`, `chmod`, `chown`, `truncate`, `touch`, and standard fuse-overlayfs mounts.

## Control Flow
Fourteen scenarios cover creating char/block devices when permitted, FIFO creation, Unix socket bind, fallocate size growth, statfs output, chmod/chown/truncate of lower files through copy-up, timestamp updates on files and dirs, preserving lower-layer devices and FIFOs, and chmod/chown on directories.

## State And Persistence
Temporary overlay trees hold created devices, FIFOs, sockets, files, and metadata changes. Tests inspect merged view and sometimes lower/upper behavior indirectly.

## Dependencies And Integration Points
Exercises `mknod`, `create`, `fallocate`, `statfs`, `setattr`, type conversion in `mode_to_filetype`, device rdev preservation, copy-up for metadata operations, and raw syscall wrappers in `sys/fs.rs`/`sys/io.rs`. Requires FUSE, Python, and optional device-node privilege.

## Risks
Device-node tests are skipped when host privileges are insufficient. Some filesystems may not support fallocate as expected. Chown tests require privilege to set arbitrary owners. Socket test depends on Python and Unix-domain socket support.

## Test Signals
Pass indicates overlay operations preserve and create special file types correctly, report filesystem stats, and apply metadata/size/time changes through FUSE-visible paths.
