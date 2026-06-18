# sources/distributed-fs/ceph-client/fs/stack.c

## Purpose

`stack.c` provides helper functions for stackable filesystems to copy size and attributes from a lower inode to an upper inode.

## Important APIs, Types, and Functions

Exports are `fsstack_copy_inode_size()` and `fsstack_copy_attr_all()`.

## Control Flow

`fsstack_copy_inode_size()` reads lower `i_size` with `i_size_read()`, conditionally locks the source for wide `i_blocks`, then conditionally locks the destination while writing size and block count on architectures where torn reads/writes are possible. `fsstack_copy_attr_all()` copies mode, uid, gid, rdev, atime/mtime/ctime, block bits, flags, and link count.

## State and Persistence Behavior

It mutates only the destination inode fields supplied by callers. There is no persistent module-private state.

## Dependencies and Integration Points

Used by stackable filesystems through exported GPL symbols. It relies on inode locking conventions and VFS timestamp helpers.

## Risks and Edge Cases

The size helper intentionally does not try to make lower `i_size` and `i_blocks` perfectly atomic together. Correctness on 32-bit SMP/preempt systems depends on conditional `i_lock` use around wide fields.

## Test Signals

Stacked filesystem tests on 32-bit and 64-bit builds, concurrent lower-file growth/shrink observations, stat output comparisons, and lockdep coverage.
