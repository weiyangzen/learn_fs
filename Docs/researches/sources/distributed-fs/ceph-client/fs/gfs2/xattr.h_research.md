# sources/distributed-fs/ceph-client/fs/gfs2/xattr.h

## Purpose
`xattr.h` defines GFS2 extended attribute layout macros, request/location structs, and exported xattr APIs.

## Important APIs, Types, And Macros
Layout macros compute record and data lengths (`GFS2_EA_REC_LEN`, `GFS2_EA_DATA_LEN`), complete record size (`GFS2_EA_SIZE`), stuffed request size, stuffed/last flags, and pointer arithmetic from headers to names, data, data-pointer arrays, next records, and the first EA record in a buffer.

`struct gfs2_ea_request` carries the requested name, value, name length, value length, and GFS2 EA type. `struct gfs2_ea_location` records the buffer, matching EA header, and previous record for replacement/removal.

Exports include `__gfs2_xattr_set`, `gfs2_listxattr`, `gfs2_ea_dealloc`, and `gfs2_xattr_acl_get`.

## Control Flow And State
The macros encode the on-disk EA grammar used by `xattr.c`: stuffed data is stored after the name, unstuffed data stores an aligned array of block pointers, records are 8-byte aligned, and the last record fills the block. The API expects callers to hold appropriate glocks or use the VFS handlers that acquire them.

## Dependencies And Integration Points
This header is used by xattr implementation, ACL code, inode eviction, and superblock xattr handler exports. It depends on GFS2 on-disk EA header definitions and Linux inode types.

## Risks And Test Signals
Pointer arithmetic bugs here affect every xattr operation and can become metadata corruption. Test signals include xattr boundary-size tests, ACL get/set tests, malformed image rejection, and fsck after xattr create/replace/remove.
