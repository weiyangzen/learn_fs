# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_fshead.h` defines the on-disk FreeVxFS fileset header subset consumed by the Linux driver. The complete 43-line file was read for this report.

## Important APIs, Types, and Functions

The key type is `struct vxfs_fsh`, containing version/index/time fields, inode counts, IAU information, inode-list inode numbers, and link-count table inode number.

## Control Flow

There is no runtime flow. `vxfs_fshead.c` copies this structure from metadata blocks and reads selected fields through endian helpers.

## State and Persistence Behavior

The structure models persistent fileset metadata. The header intentionally stops before version/port-specific trailing fields, so the driver only relies on the common prefix it needs to locate inode lists.

## Dependencies and Integration Points

It depends on `__fs32` from `vxfs.h` and integrates with `vxfs_read_fshead()` during mount.

## Risks and Edge Cases

The main risk is ABI mismatch across VxFS variants. If a supported image has a different common-prefix layout, the driver may choose the wrong inode-list inode. The comments explicitly acknowledge that later fields vary by version and port.

## Test Signals

Mount tests against HP-UX and SCO images, endian conversion checks, and fileset-header fixture parsing across VxFS versions 2-4 are useful.
