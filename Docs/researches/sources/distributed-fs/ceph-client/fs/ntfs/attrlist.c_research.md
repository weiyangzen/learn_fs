# sources/distributed-fs/ceph-client/fs/ntfs/attrlist.c

## Purpose

`attrlist.c` manages the `$ATTRIBUTE_LIST` attribute for NTFS inodes whose attributes span multiple MFT records. It determines whether an attribute list is still needed, persists the in-memory list to its attribute stream, and adds/removes list entries when attribute records are created, moved, or deleted.

## Important APIs, Types, And Functions

- `ntfs_attrlist_need()` walks `ni->attr_list` and returns whether any list entry points to an MFT record other than the base inode. It returns `1` when an extent record is referenced, `0` when all entries are local, and negative errno on invalid state.
- `ntfs_attrlist_update()` opens the unnamed `AT_ATTRIBUTE_LIST` attribute inode, truncates it to `base_ni->attr_list_size`, writes the in-memory `base_ni->attr_list` bytes, updates non-resident attribute-list state, marks the base list dirty, and drops the attribute inode.
- `ntfs_attrlist_entry_add()` builds a new sorted `struct attr_list_entry` for an attribute record, inserts it into a newly allocated copy of the list, swaps it into the base inode, persists it, and frees the old list on success.
- `ntfs_attrlist_entry_rm()` removes `ctx->al_entry` from the base inode's list by copying all other entries into a new buffer and then persists the result.

## Control Flow And Algorithms

Adding an entry first maps the MFT record containing the attribute to capture a correct MFT reference and sequence number. If the caller passed an extent inode, the function switches to the base inode. It locates the insertion position with `ntfs_attr_lookup()` using the target type, name, lowest VCN, and resident value ordering, then constructs an aligned list entry with type, name, `lowest_vcn`, `mft_reference`, and instance. The list is replaced only after the new buffer is complete; on persistence failure the old pointer and size are restored.

Updating the on-disk list is done through normal attribute I/O rather than by direct MFT manipulation. It truncates the attribute stream, handles a special recovery case for `$MFT` where an `-ENOSPC` truncate tries to reset and retry, writes the entire list with `ntfs_inode_attr_pwrite()`, and marks the in-memory state dirty.

Removal computes the new length, allocates a replacement buffer, copies the prefix and suffix around the removed entry, swaps it into `base_ni`, and calls `ntfs_attrlist_update()`.

## State And Persistence Behavior

The primary state is `base_ni->attr_list`, `base_ni->attr_list_size`, `NInoAttrList`, `NInoAttrListNonResident`, and `NInoAttrListDirty`. Persistence happens by resizing and writing the `AT_ATTRIBUTE_LIST` attribute stream. Entry add is rollback-aware for the in-memory pointer/size if persistence fails; entry remove swaps the in-memory list before update and does not restore it if the update fails.

## Dependencies And Integration Points

The file includes `mft.h`, `attrib.h`, and `attrlist.h`. It relies on `ntfs_attr_iget()`, `ntfs_attr_truncate_i()`, `ntfs_attr_truncate()`, `i_size_write()`, `ntfs_inode_attr_pwrite()`, MFT map/unmap helpers, `ntfs_attr_get_search_ctx()`, and `ntfs_attr_lookup()`. It is called from `attrib.c` when records are added, removed, moved, or when mapping-pair updates need list metadata refreshed.

## Risks And Edge Cases

- `ntfs_attrlist_need()` trusts list entry lengths enough to advance; corrupt zero-length entries would be dangerous if validation has not already happened.
- `ntfs_attrlist_entry_add()` uses `attr->data.non_resident.lowest_vcn` in a duplicate check even in the branch after lookup succeeds; resident attributes rely on earlier lookup parameters to avoid misuse.
- Removal does not roll back `base_ni->attr_list` if `ntfs_attrlist_update()` fails, so in-memory and on-disk state can diverge until higher-level error handling reacts.
- Attribute-list updates can recurse into attribute resizing and allocation paths, so lock ordering and ENOSPC behavior are sensitive.

## Test Signals

Tests should create enough attributes to force `$ATTRIBUTE_LIST`, add records in sorted and unsorted type/name/VCN order, move records to extent MFT records, remove entries until the list is no longer needed, verify non-resident list updates, and inject write/truncate failures to check rollback and error reporting.
