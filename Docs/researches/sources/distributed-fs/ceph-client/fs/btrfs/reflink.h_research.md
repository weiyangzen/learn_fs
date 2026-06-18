# sources/distributed-fs/ceph-client/fs/btrfs/reflink.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/reflink.h` declares the Btrfs file-range remap entry point implemented by `reflink.c`. The source was read as a complete 14-line file.

## Important APIs, Types, and Functions

The only public declaration is `loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags);`. It forwards `struct file` and includes Linux integer/types support.

## Control Flow

There is no runtime control flow in the header. It connects Btrfs file operation tables or call sites to the implementation that handles clone and dedupe.

## State and Persistence Behavior

The header owns no state. Persistent behavior is entirely in `reflink.c`, where destination extent items and inode metadata are updated.

## Dependencies and Integration Points

The header depends only on `<linux/types.h>` and a forward declaration of `struct file`. It is included by Btrfs file-operation code that exposes VFS remap support.

## Risks and Edge Cases

The signature must match the VFS remap-file-range expectations and the implementation. Callers must pass file objects from the same Btrfs filesystem after VFS-level checks, and must interpret a non-negative return as the number of bytes remapped.

## Test Signals

Compile coverage catches prototype drift. Functional signals are the reflink and dedupe tests that call the public entry point through VFS operations.
