# sources/distributed-fs/ceph-client/fs/gfs2/dentry.c

## Purpose
Provides GFS2 dentry operations for cluster-coherent dentry revalidation, name hashing, and dentry deletion hints.

## Important APIs, Types, And Functions
`gfs2_drevalidate()` verifies that a dentry still matches its parent directory entry under the parent inode glock. `gfs2_dhash()` computes GFS2's on-disk CRC hash for dentry names. `gfs2_dentry_delete()` asks VFS to drop dentries whose iopen glock is being demoted. `gfs2_dops` registers these operations.

## Control Flow
Revalidation rejects RCU mode, rejects bad inodes, bypasses checks when no lock module mount operation exists, conditionally takes the parent shared glock, and calls `gfs2_dir_check()`. Positive dentries are valid on successful check; negative dentries are valid only when the name is still absent. Delete returns true only for positive dentries with initialized iopen glock marked for demotion.

## State And Persistence
No persistent writes. It observes directory entries and glock state and influences dcache retention. Name hash must match directory-entry hash persisted on disk.

## Dependencies And Integration Points
Depends on directory checking, glocks, lock module state, dcache operations, and GFS2 hash helpers. Used by inode/super operation setup for dentries.

## Risks
Skipping RCU revalidation is required because glock locking can sleep. Incorrect negative-dentry validation would hide newly created remote names. Hash mismatch with `dir.h` would break lookup consistency.

## Test Signals
Test positive and negative dentry revalidation after remote create/delete/rename, bad inode handling, lockless/nolock mount behavior, iopen demote deletion, and hash compatibility with directory entries.
