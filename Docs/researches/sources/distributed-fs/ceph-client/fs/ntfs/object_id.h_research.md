# sources/distributed-fs/ceph-client/fs/ntfs/object_id.h

## Purpose
`object_id.h` exposes the minimal object-id cleanup interface for NTFS namespace deletion.

## Important APIs
It declares the `$ObjId` index name symbol `objid_index_name[]` and `ntfs_delete_object_id_index(struct ntfs_inode *ni)`.

## Control Flow and State
The header carries no control flow. Its contract is that callers pass the base NTFS inode whose `AT_OBJECT_ID` attribute should be unindexed before final deletion.

## Dependencies and Integration
`namei.c` includes this header and invokes the function when a file's link count reaches zero. Implementation requires `struct ntfs_inode` definitions through including translation units.

## Risks
The header does not include `inode.h`, so it relies on prior declarations in users. The API only covers deletion/unindexing, not creation or update, so callers must not assume full object-id lifecycle support here.

## Test Signals
Build coverage should confirm all users include the necessary NTFS inode declarations. Deletion tests should verify the function is called only for final unlink.
