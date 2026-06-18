# sources/distributed-fs/ceph-client/fs/xfs/xfs_icreate_item.h

## Purpose
`xfs_icreate_item.h` declares the in-memory icreate log item and the API for logging inode chunk creation. The complete 22-line header was read.

## Important APIs, Types, and Functions
`struct xfs_icreate_item` embeds a generic `struct xfs_log_item` and the formatted `struct xfs_icreate_log`. The header declares the global slab cache `xfs_icreate_cache` and `xfs_icreate_log`.

## Control Flow
Inode allocation code calls `xfs_icreate_log` with transaction, AG location, inode count, inode size, allocation length, and generation. The implementation owns allocation, formatting, transaction joining, and later recovery behavior.

## State and Persistence Behavior
The header defines only the incore wrapper for a journal record. Persistent behavior is the log item record that recovery interprets to initialize inode chunks.

## Dependencies and Integration Points
It is used by inode allocation and transaction code that needs compact inode-create logging. It depends on XFS transaction, AG, inode geometry, and log item types supplied by other XFS headers.

## Risks and Edge Cases
The header is small, but callers must pass geometry-consistent values because recovery validates and depends on them. Slab cache initialization/teardown must match use of `xfs_icreate_cache`.

## Test Signals
Compile coverage of callers, slab cache lifetime tests, and recovery tests for records produced by `xfs_icreate_log` are the relevant signals.
