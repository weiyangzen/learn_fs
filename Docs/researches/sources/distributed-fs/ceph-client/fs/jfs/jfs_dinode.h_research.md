# sources/distributed-fs/ceph-client/fs/jfs/jfs_dinode.h

## Purpose
Defines the 512-byte on-disk JFS inode layout and extended mode/file attribute bits.

## Important APIs, types, and functions
`struct dinode` includes base POSIX fields, inode extent descriptor, size/block counts, link/uid/gid/mode, timestamps, ACL/EA descriptors, directory index state, and a union for directory roots or file/special data. It defines inline directory table, dtree root, xtree root, special-device data, fast symlink data, inline EA area, and Linux-visible flags.

## Control flow
Disk inode read/write code maps these fields into VFS and JFS in-core inode state. Directory, extent, symlink, xattr, and ioctl code interpret the union based on type and mode bits.

## State and persistence behavior
This is persistent on-disk metadata. Inline symlink and EA regions share storage, so mode bits and layout compatibility matter.

## Dependencies and integration points
Depends on JFS descriptor and tree types; consumed by inode manager, xtree/dtree, xattr, symlink, and ioctl code.

## Risks and test signals
Test layout compatibility, endian handling, fast/long symlinks, inline/external EAs, device inodes, directory indexes, and user-visible flags after remount.
