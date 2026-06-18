# sources/distributed-fs/ceph-client/fs/btrfs/fiemap.h

## Purpose

`fiemap.h` is the small public header for Btrfs fiemap support. It declares the Btrfs-specific `btrfs_fiemap()` entry point used to implement generic FIEMAP extent reporting for Btrfs inodes.

## Important APIs, Types, And Functions

- Includes `<linux/fiemap.h>` for `struct fiemap_extent_info` and FIEMAP flags.
- Declares `int btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len);`.

## Control Flow

Callers include this header and invoke `btrfs_fiemap()` from inode/file operation paths that service FIEMAP requests. The implementation in `fiemap.c` performs prep, optional sync waits, inode locking, extent walking, and userspace record emission.

## State And Persistence Behavior

The header defines no persistent state. The declared API is observational: it reports mappings and may request synchronization through FIEMAP flags, but it does not itself define on-disk format or state transitions.

## Dependencies And Integration Points

This header depends on the Linux fiemap interface and Btrfs code that already has `struct inode` and `u64` visible. It integrates Btrfs inode operations with the implementation in `fiemap.c`.

## Risks And Edge Cases

- The declaration depends on compatible visibility of `struct inode` and `u64`; include ordering in callers must provide those types.
- Any signature change must be coordinated with Btrfs inode operation wiring and the implementation.

## Test Signals

Build coverage validates the declaration. Runtime coverage comes from FIEMAP ioctl tests that exercise `btrfs_fiemap()` through VFS paths.
