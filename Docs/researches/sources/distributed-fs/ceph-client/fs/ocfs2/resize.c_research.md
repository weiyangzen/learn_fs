# sources/distributed-fs/ceph-client/fs/ocfs2/resize.c

## Purpose
`resize.c` implements OCFS2 online volume growth for the global bitmap. It can extend the final existing cluster group or add a new group descriptor, updating bitmap chains, group descriptors, the global bitmap inode, the primary superblock, and backup superblocks.

## Important APIs, types, and functions
The exported entry points are `ocfs2_group_extend` and `ocfs2_group_add`. Important helpers include `ocfs2_calc_new_backup_super`, `ocfs2_update_last_group_and_inode`, `update_backups`, `ocfs2_update_super_and_backups`, `ocfs2_check_new_group`, and `ocfs2_verify_group_and_input`. The code manipulates `struct ocfs2_dinode`, `struct ocfs2_chain_list`, `struct ocfs2_chain_rec`, `struct ocfs2_group_desc`, and userspace-provided `struct ocfs2_new_group_input`.

## Control flow
`ocfs2_group_extend` validates the request, locks the global bitmap system inode, verifies the bitmap geometry supports online resize, reads the last group descriptor, ensures the new clusters fit in that group, starts a transaction, grows the group bit count and free count, marks any newly covered backup superblock bits allocated, updates chain totals and bitmap inode size/cluster count, and finally writes the superblock/backups. `ocfs2_group_add` reads a prepared group descriptor from the newly available disk region, validates the descriptor and input against chain order and size limits, links the new group into the selected chain, updates chain and bitmap totals, grows inode size, and writes superblock backups.

## State and persistence
Persistent mutations include global bitmap group descriptors, chain records, bitmap inode `i_clusters`, bitmap totals/used/free counts, primary superblock cluster count, and backup superblock copies. The in-memory bitmap inode cluster count and VFS size are updated under `ip_lock`. Resize work is journaled for bitmap metadata, while superblock backup writes are attempted after metadata changes and treated as repairable by fsck if they fail.

## Dependencies and integration points
The file depends on global bitmap system-file lookup, inode cluster locks, OCFS2 journaling, group descriptor validation, suballocator helpers, backup-superblock layout, and emergency read-only state checks. It is invoked by OCFS2 resize ioctl/control paths that pass either a group extension count or a validated new-group input.

## Risks and test signals
Risks include accepting malformed group descriptors, overflow in cluster totals, extending a non-full last group through the wrong path, backup superblock bitmap accounting mistakes, partial superblock backup updates, and chain linking rollback after journal access failure. Test signals include online grow by final-group extension, adding groups to existing and next-free chains, backup-superblock feature enabled/disabled, old-small-disk rejection, invalid group input fuzzing, emergency read-only behavior, and fsck after injected backup write failures.
