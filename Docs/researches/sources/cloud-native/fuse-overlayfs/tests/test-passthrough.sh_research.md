# sources/cloud-native/fuse-overlayfs/tests/test-passthrough.sh

## Purpose
`tests/test-passthrough.sh` validates inode passthrough, readdir `d_ino` consistency, xino stability, and behavior when layers are on the same filesystem, different filesystems, or nested FUSE mounts.

## Important APIs, Types, And Functions
It defines `fail` and `test_d_ino`, uses `stat`, `ls -li`, ext2 images, `mke2fs`, `fuse2fs`, and repeated fuse-overlayfs mounts with `lowerdir`, `xino=auto`, and `xino=off`.

## Control Flow
First it overlays same-filesystem lower/upper trees and asserts merged inode numbers match direct access and `ls` d_ino values. Then it creates two ext2 filesystems where first files intentionally share `st_ino`, verifies merged inode uniqueness, checks non-stable behavior across mounts with different filesystems, verifies `xino=auto` produces stable inode numbers across remounts, and confirms double-FUSE layers disable xino/export-like stability expectations.

## State And Persistence
Temporary lower/upper/mnt trees, ext2 image files, fuse2fs mounts, and nested overlay mounts are created and removed. Inode values are sampled and compared across remounts.

## Dependencies And Integration Points
Exercises `OverlayFs::new` same-device detection, inode table mapping, `get_st_ino_with_path`, NFS/filehandle/xino behavior, readdirplus/direntry inode reporting, and FUSE export capability negotiation. Depends on `fuse2fs`, `mke2fs`, FUSE, and stat/ls formats.

## Risks
The test assumes ext2 first-file inode equality; it fails with an explicit message if that setup assumption breaks. Some non-stability cases are informational and do not require difference. Host FUSE capability differences can affect double-FUSE expectations.

## Test Signals
Pass gives strong evidence that inode passthrough is correct on same-device layers, duplicate lower inode numbers are disambiguated across devices, and `xino=auto` gives stable remount-visible inodes when supported.
