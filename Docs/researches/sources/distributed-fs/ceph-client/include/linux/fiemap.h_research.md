# sources/distributed-fs/ceph-client/include/linux/fiemap.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fiemap.h` declares the kernel-side FIEMAP extent reporting interface used by filesystems. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

It defines `struct fiemap_extent_info` and declares `fiemap_prep()` and `fiemap_fill_next_extent()`.

## Control Flow

Filesystem fiemap implementations prepare a user request with `fiemap_prep()`, iterate filesystem extents, and call `fiemap_fill_next_extent()` for each logical/physical/length/flag tuple until the user buffer is full or extents are exhausted.

## State and Persistence Behavior

`fiemap_extent_info` tracks request flags, number of extents mapped, max extents, and the userspace destination pointer. It is per-ioctl transient state.

## Dependencies and Integration Points

It includes UAPI FIEMAP definitions and `linux/fs.h`. It integrates with VFS ioctl handling and filesystem extent maps, including distributed filesystems such as CephFS when they expose extent layout.

## Risks and Edge Cases

Userspace pointer handling and extent count limits are sensitive. Filesystems must set accurate flags for unwritten, shared, delayed, encoded, or last extents and validate unsupported flags.

## Test Signals

FIEMAP xfstests for sparse, unwritten, shared/reflinked, inline, encrypted/compressed, and distributed file extents; ioctl fault-injection for userspace copy errors.
