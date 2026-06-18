# sources/distributed-fs/ceph-client/fs/tracefs/internal.h

## Purpose
This header defines private tracefs/eventfs structures, flags, and helper declarations shared by tracefs implementation files.

## Important APIs, Types, and Functions
It defines tracefs flags `TRACEFS_EVENT_INODE`, `TRACEFS_GID_PERM_SET`, `TRACEFS_UID_PERM_SET`, and `TRACEFS_INSTANCE_INODE`; `struct tracefs_inode`; `struct eventfs_attr`; `struct eventfs_inode`; and inline `get_tracefs()`. It declares creation helpers and eventfs remount/dentry release hooks.

## Control Flow and State
There is no runtime control flow. The state model is important: `tracefs_inode` embeds the VFS inode plus list/flags/private metadata, while `eventfs_inode` stores dynamic event directory entries, child lists, saved attributes, kref, freed/events flags, and stable directory inode number.

## Persistence, Dependencies, and Integration
The header couples eventfs and tracefs without exposing these internals to external users. It depends on VFS inode, list, kref, `eventfs_entry`, uid/gid types, and dentry declarations.

## Risks and Test Signals
Risks are structural invariants: flags must match remount/drop behavior, `private` must point to the expected owner/eventfs object, and `eventfs_inode` lifetime must match dentry references. Build tests and runtime tracefs/eventfs stress are the key signals.
