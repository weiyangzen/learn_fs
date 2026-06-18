# sources/distributed-fs/ceph-client/fs/ntfs3/xattr.c

## Purpose
`xattr.c` implements NTFS3 extended attributes, POSIX ACL storage over EAs, system xattrs for DOS/NTFS attributes and security descriptors, WSL permission xattrs, and VFS xattr handler registration.

## Important APIs and Functions
EA helpers size and scan `EA_FULL` records. `ntfs_read_ea()` loads and validates `ATTR_EA_INFO` and `ATTR_EA`. `ntfs_list_ea()`, `ntfs_get_ea()`, and `ntfs_set_ea()` implement listing, retrieval, creation, replacement, removal, resizing, and persistence. ACL support is provided by `ntfs_get_acl()`, `ntfs_set_acl()`, and `ntfs_init_acl()` when configured. `ntfs_acl_chmod()`, `ntfs_listxattr()`, `ntfs_getxattr()`, `ntfs_setxattr()`, `ntfs_save_wsl_perm()`, and `ntfs_get_wsl_perm()` are the public integration points.

## Control Flow
EA operations lock the NTFS inode unless already locked. `ntfs_set_ea()` reads existing EAs with extra capacity, removes or appends aligned records, checks packed and unpacked limits, creates missing EA attributes, resizes `ATTR_EA`, writes resident or nonresident data, updates `EA_INFO`, toggles `NI_FLAG_EA`, and marks dirty. System xattrs dispatch before falling back to ordinary NTFS EAs.

## State and Persistence Behavior
EAs persist in `ATTR_EA`; summary metadata persists in `ATTR_EA_INFO`. DOS/NTFS attribute writes update standard information. Security xattrs insert descriptors into `$Secure`. WSL xattrs can override uid, gid, mode, and device on inode load.

## Dependencies and Integration Points
The file depends on NTFS attribute operations, run loading, VFS ACL/xattr APIs, security descriptor validation, `$Secure`, and inode dirtying. It is used by inode operations, create, setattr/chmod, and inode load paths.

## Risks
Variable-length EA blobs create size, alignment, and overflow risks. Resident/nonresident transitions and partial WSL writes are sensitive. Some failing setxattr paths still update ctime/dirty state.

## Test Signals
Test xattr list/get/set/remove, create/replace flags, large EAs, resident-to-nonresident growth, ACL inheritance/chmod, DOS/NTFS endian variants, security descriptor get/set, WSL round trips, forced shutdown, and corrupted EA validation.
