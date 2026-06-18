# sources/distributed-fs/ceph-client/fs/ntfs/object_id.c

## Purpose
`object_id.c` removes object ID index entries from `$Extend/$ObjId` when an inode with an `AT_OBJECT_ID` attribute is deleted.

## Important APIs and Types
It defines packed index key/data structures matching `$ObjId`, exports `objid_index_name` as `$O`, and provides `ntfs_delete_object_id_index()`. Internal helpers are `open_object_id_index()` and `remove_object_id_index()`.

## Control Flow and State
Opening the index converts `$ObjId` to NTFS Unicode, loads `FILE_Extend`, looks up `$ObjId` by name under the extend directory MFT lock, opens that inode, and obtains an index context for `$O`. Deletion opens the target inode's `AT_OBJECT_ID` attribute, opens the system index, locks the index inode's MFT record, reads the GUID key from the attribute value, looks up the key, removes the matching index entry, marks the index entry and MFT record dirty, and drops all references.

## Dependencies and Integration
Deletion is called from `ntfs_delete()` when the file-name link count reaches zero. It depends on `ntfs_attr_iget()`, Unicode conversion, inode lookup, directory lookup by name, index context management, index lookup/removal, and MFT dirty marking.

## Risks
If `$ObjId` cannot be opened, `ntfs_delete_object_id_index()` silently returns success with no index removal. If the object-id attribute is malformed or short, removal returns `-ENODATA`. Correctness depends on packed struct layout and GUID byte ordering. Failure after attribute removal elsewhere can leave stale `$ObjId` entries.

## Test Signals
Create/delete files with object IDs, missing `$ObjId`, malformed short object-id attributes, absent index entries, and injected index removal failures. Validate that the `$O` entry disappears and that index inode MFT dirtying triggers persistence.
