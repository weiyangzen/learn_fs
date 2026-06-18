# sources/distributed-fs/openafs/src/vol/volinodes.h

## Purpose
Defines the common table describing special volume inodes and provides `init_inode_info`, which adapts that table to a specific `VolumeHeader` instance.

## Important APIs, Types, and Functions
`NO_LINK_TABLE` is platform-dependent: namei builds use link tables, while non-namei builds mark them obsolete. `MAXINODETYPE` is `VI_LINKTABLE`, the highest special inode type tracked.

`struct afs_inode_info` describes a special inode by expected `versionStamp`, `inodeType`, fixed header size, pointer to the inode field in a `VolumeHeader`, human description, and an `obsolete` flag.

`afs_common_inode_info` lists volume info (`VI_VOLINFO`), small vnode index, large vnode index, ACL, mount table, and link table. ACL and mount table are obsolete; link table is obsolete outside namei. `init_inode_info` copies the common table and converts stored `offsetof(struct VolumeHeader, field)` values into actual pointers into the caller's `VolumeHeader`.

## Control Flow
The header has one inline loop in `init_inode_info`. Salvager code creates a temporary `VolumeHeader`, calls this helper, fills inode fields from discovered special inodes, and passes each `afs_inode_info` entry to `SalvageHeader`.

## State and Persistence Behavior
This table defines which special inodes must exist, how much header data must be read to validate magic/version, which `VolumeHeader` fields reference them, and which old inode types the salvager may delete or ignore. It therefore drives persistent volume header repair and special-inode recreation.

## Dependencies and Integration Points
Requires `VolumeHeader`, `versionStamp`, `Inode`, volume magic/version constants, and `VI_*` special inode constants. It is used by vutil and salvager logic to keep volume header interpretation consistent.

## Risks
The comment notes `inodeType` is redundant because the table must be ordered. If `VI_*` numbering or `VolumeHeader` layout changes without updating this table, the salvager can validate or write the wrong inode field. The offset-to-pointer cast is deliberate but sensitive to structure layout and include definitions.

## Test Signals
Tests that recreate missing volume info, vnode index, and namei link-table inodes validate this mapping. Platform builds should verify namei versus non-namei obsolete behavior. Corrupt magic tests verify the expected stamps and sizes.

## Source Notes
Read as C header; 113 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
