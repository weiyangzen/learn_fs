# sources/distributed-fs/ceph-client/fs/smb/client/namespace.c

## Purpose
`namespace.c` implements CIFS automount support for SMB junctions and DFS referrals. It converts a dentry that represents a remote namespace transition into a new submount with an updated device name and filesystem context, then schedules mount expiry for idle automounts.

## Important APIs, types, and functions
The exported helpers are `cifs_build_devname()`, `cifs_release_automount_timer()`, `cifs_d_automount()`, and the `cifs_namespace_inode_operations` table used by automount inodes. Internal helpers include `cifs_expire_automounts()`, `is_dfs_mount()`, `automount_fullpath()`, `fs_context_set_ids()`, and `cifs_do_automount()`.

## Control flow
`cifs_d_automount()` delegates to `cifs_do_automount()`, then attaches the resulting mount to `cifs_automount_list` and schedules delayed expiry. `cifs_do_automount()` rejects root automounts, synchronizes passwords from the root session into the mountpoint superblock context, creates a submount fs context, computes the full automount path either from the dentry path or `tcon->origin_fullpath`, duplicates the current SMB3 context with current user IDs for multiuser cases, parses the new device name, builds the final `source`, marks DFS automount/connection flags, and calls `fc_mount()`.

## State and persistence behavior
Automounts are VFS mounts stored locally and marked for expiry through `cifs_automount_list`; they are not persistent server-side state. The generated fs context carries UNC, prepath, credentials, source, DFS state, and mount options into the submount. Password synchronization prevents redundant retry/password swapping during DFS automounts.

## Dependencies and integration points
This file depends on VFS mount/fs-context APIs, CIFS mount contexts, dentry path building, DFS origin tracking via `tcon->origin_fullpath`, session password synchronization, and the inode operations chosen in `inode.c` for `S_AUTOMOUNT` directories.

## Risks
Risks include malformed referral UNC/prepath handling, buffer underflow/overflow when prefixing `origin_fullpath` into a raw dentry path, stale password context during multiuser automounts, failure to cancel the expiry work while automounts remain, and incorrect DFS flags causing either missed failover behavior or unnecessary DFS connection handling.

## Test signals
Test DFS and non-DFS junction automounts, root dentry rejection, trailing and leading delimiter normalization in `cifs_build_devname()`, prefix-path mounts, `origin_fullpath` automount paths, multiuser uid/gid/cruid inheritance, password rotation before automount, failed `smb3_parse_devname()`, and expiry scheduling/release with active and empty automount lists.
