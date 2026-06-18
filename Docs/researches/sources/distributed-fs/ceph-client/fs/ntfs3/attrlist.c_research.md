# sources/distributed-fs/ceph-client/fs/ntfs3/attrlist.c

## Purpose
Manages NTFS attribute lists for files whose attributes span multiple MFT records. It loads resident/nonresident lists, enumerates sorted entries, finds matching segments, inserts/removes entries, and writes dirty lists back to the attribute.

## Important APIs, Types, And Functions
`ntfs_load_attr_list()` initializes `ni->attr_list` from a resident or nonresident `ATTR_LIST` attribute. `al_enumerate()` safely walks entries with boundary checks. `al_find_le()` and `al_find_ex()` locate entries by type/name/VCN. `al_add_le()` inserts a sorted entry and grows the backing `ATTR_LIST` attribute through `attr_set_size_ex()`. `al_remove_le()` removes an entry in memory. `al_update()` resizes and writes the list back, resident or nonresident. `al_destroy()` frees runlist and list memory.

## Control Flow
Loading validates size and run offsets, allocates an aligned list buffer, unpacks runlists for nonresident lists, then reads the list into memory. Insertions compute the sorted insertion position, grow/reallocate the in-memory list, populate the new entry, then resize the on-disk/list attribute; on failure the memmove is undone. Updates shrink or grow the `ATTR_LIST` attribute and copy or write the buffer depending on resident state.

## State And Persistence
Runtime state is `ni->attr_list.le`, `size`, `run`, and `dirty`. Persistent state is the `$ATTRIBUTE_LIST` attribute payload and, for nonresident lists, its runlist/data size. Entries store type, name, starting VCN, MFT reference, and attribute id.

## Dependencies And Integration Points
Used heavily by `attrib.c`, inode/MFT segment loading, and record mutation code. Depends on runlist unpacking, NTFS read/write run helpers, name comparison, and attribute resizing.

## Risks And Edge Cases
Sorted-order correctness is critical because lookup returns the previous matching VCN when an exact entry is not found. Bad entry sizes, name offsets, zero-size lists, and invalid nonresident `svcn` are rejected. Insert rollback only undoes the in-memory move if `attr_set_size_ex()` fails; later writeback failures can leave dirty in-memory state that must be retried.

## Test Signals
Create fragmented files requiring multiple MFT records, verify list ordering by type/name/VCN, test resident-to-nonresident list growth, remove segments during truncate/punch, inject ENOMEM during insertion, and validate persisted lists after remount.
