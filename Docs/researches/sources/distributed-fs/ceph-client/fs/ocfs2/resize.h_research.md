# sources/distributed-fs/ceph-client/fs/ocfs2/resize.h

## Purpose
`resize.h` declares the OCFS2 online resize entry points for extending the current last group or adding a new bitmap group.

## Important APIs, types, and functions
The header exposes `ocfs2_group_extend(struct inode *inode, int new_clusters)` and `ocfs2_group_add(struct inode *inode, struct ocfs2_new_group_input *input)`. `ocfs2_new_group_input` is defined in OCFS2 disk-format headers and carries the prepared group block, target chain, total clusters, and free clusters.

## Control flow
Resize callers include this header and choose `ocfs2_group_extend` when the current final group can absorb additional clusters, or `ocfs2_group_add` when a fully prepared new group descriptor must be linked into the global bitmap chain.

## State and persistence
The header has no state. The declared functions persist changes to global bitmap metadata and superblock cluster counts through the implementation in `resize.c`.

## Dependencies and integration points
It depends on declarations of `struct inode` and `struct ocfs2_new_group_input` from surrounding OCFS2/Linux headers. It is part of the filesystem control-plane interface used by resize ioctl code.

## Risks and test signals
Risks are primarily interface misuse: passing a negative extension, calling group-add before userspace has initialized the on-disk group descriptor, or using extend when the last group is already full. Test signals are compile coverage for resize callers and online resize tests that exercise both declared paths.
