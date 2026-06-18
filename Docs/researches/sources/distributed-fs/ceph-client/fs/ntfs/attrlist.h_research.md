# sources/distributed-fs/ceph-client/fs/ntfs/attrlist.h

## Purpose

`attrlist.h` declares the small public interface for NTFS `$ATTRIBUTE_LIST` management.

## Important APIs, Types, And Functions

- `ntfs_attrlist_need(struct ntfs_inode *ni)` checks whether an inode still requires an attribute list.
- `ntfs_attrlist_entry_add(struct ntfs_inode *ni, struct attr_record *attr)` inserts a new list entry for an attribute record.
- `ntfs_attrlist_entry_rm(struct ntfs_attr_search_ctx *ctx)` removes the current list entry from the base inode.
- `ntfs_attrlist_update(struct ntfs_inode *base_ni)` persists the in-memory attribute-list bytes to the `$ATTRIBUTE_LIST` stream.

## Control Flow And Usage

Callers in the attribute engine invoke these helpers after creating, moving, deleting, or resizing attribute records. The header includes `attrib.h` because removal uses `struct ntfs_attr_search_ctx` and add uses `struct attr_record`/`struct ntfs_inode` from the NTFS attribute model.

## State And Persistence Behavior

The declared functions mutate `base_ni->attr_list` and persist `AT_ATTRIBUTE_LIST`. This header does not own state, but its APIs are part of the transaction boundary for MFT record changes that affect attribute-list entries.

## Dependencies And Integration Points

The header is consumed by `attrib.c` and implemented by `attrlist.c`. It is tied to MFT record layout, attribute search context lifecycle, and inode flags that indicate whether an attribute list exists or is non-resident.

## Risks And Edge Cases

The interface does not encode whether `ni` is a base or extent inode; implementations normalize in some paths. Callers must ensure the supplied search context still points at the entry to remove and has not been invalidated by a relookup or record movement.

## Test Signals

Build coverage should ensure prototypes stay aligned with implementation. Runtime coverage comes from attribute add/remove/move tests that validate correct `$ATTRIBUTE_LIST` bytes and persistence.
