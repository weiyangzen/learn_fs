# sources/distributed-fs/ceph-client/fs/jfs/jfs_xattr.h

## Purpose
`jfs_xattr.h` defines the on-disk extended-attribute list format, helper macros for walking variable-length EA records, maximum EA sizes, xattr operation declarations, and the optional security-label initialization hook.

## Important APIs, types, and functions
The persistent structures are `struct jfs_ea` and `struct jfs_ea_list`. Macros include `MAXEASIZE`, `MAXEALISTSIZE`, `EA_SIZE()`, `NEXT_EA()`, `FIRST_EA()`, `EALIST_SIZE()`, and `END_EALIST()`. Exported functions are `__jfs_setxattr()`, `__jfs_getxattr()`, `jfs_listxattr()`, `jfs_xattr_handlers`, and `jfs_init_security()` when `CONFIG_JFS_SECURITY` is enabled. Without security support, `jfs_init_security()` is an inline no-op.

## Control flow
Xattr implementation code includes this header to parse an EA list from its size header, start at `FIRST_EA()`, advance through records with `NEXT_EA()`, and stop at `END_EALIST()`. Set/get/list operations use the declarations here; inode creation calls `jfs_init_security()` to attach security attributes when configured.

## State and persistence behavior
Each EA stores an unused flag byte, name length, little-endian value length, and a flexible name field that includes a NUL terminator, with the value immediately following the name. The list begins with a little-endian total size. The macros compute sizes from on-disk fields, so validation in implementation code must ensure records remain inside `EALIST_SIZE()`.

## Dependencies and integration points
The header depends on Linux xattr APIs and JFS transaction IDs/inodes from included compile context. It integrates with transaction manager EA extent logging through `txEA()`, inode create security hooks, and VFS xattr handlers.

## Risks
Variable-length parsing is vulnerable to corrupt size, name length, or value length fields if callers do not bounds-check before using `NEXT_EA()`. `MAXEASIZE` is 65535, so callers must reject larger buffers. The name includes a null terminator despite a stored length for OS/2 compatibility; code that assumes ordinary C strings without checking `namelen` can misparse malformed attributes.

## Test signals
Tests should cover empty EA lists, multiple packed attributes, max-size attributes, corrupt list size and truncated records, names with expected NUL terminators, set/get/list VFS behavior, EA extent allocation/free logging, and security xattr initialization with and without `CONFIG_JFS_SECURITY`.
