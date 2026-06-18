# sources/distributed-fs/ceph-client/fs/hfsplus/hfsplus_raw.h

## Purpose
`hfsplus_raw.h` is a compatibility wrapper for on-disk HFS+ structure definitions. In this tree it does not define the raw structures directly; it includes `<linux/types.h>` and `<linux/hfs_common.h>`, where the shared HFS/HFS+ constants, CNIDs, volume header, fork, catalog, attribute, extent, Unicode, and permission structures live.

## Important APIs, types, and functions
The header exports no functions and declares no local types beyond its include guard. Its effective API is the set of raw HFS+ types made available through `linux/hfs_common.h`, such as `struct hfsplus_vh`, `struct hfsplus_fork_raw`, catalog entries, attribute keys, extent records, Unicode strings, and constants used throughout the HFS+ driver.

## Control flow
There is no executable control flow. The file is included by `hfsplus_fs.h`, `inode.c`, and `unicode.c` so those files can refer to raw on-disk objects without each including the common header directly.

## State and persistence behavior
The file itself has no state, but it is part of the persistence ABI boundary. Any raw structures transitively included through it describe big-endian on-disk HFS+ metadata and must remain compatible with disk images and Apple Technote 1150 semantics.

## Dependencies and integration points
It depends on Linux fixed-width types and `linux/hfs_common.h`. It integrates the HFS+ driver with common HFS/HFS+ definitions shared outside this local directory.

## Risks and test signals
Risks are mostly indirect: include path changes, raw-structure drift in `hfs_common.h`, or assumptions in implementation files that this header itself owns definitions. Test signals are compile coverage for all HFS+ objects, mount/read of representative HFS+ images, and static checks that raw structures still match expected endian/layout contracts.
