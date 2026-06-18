# sources/distributed-fs/ceph/src/mds/events/EOpen.h

Purpose: Declares a journal event that records clean/open inodes needed for recovery.

Important APIs/types: `EOpen` stores an `EMetaBlob`, base inode vector `inos`, and snap inode vector `snap_inos`. `add_clean_inode` adds parent dentry context and records either base or snap vino; `add_ino` records a raw inode number.

Control flow: Open-file state is journaled so replay can reopen/recover clean inodes and keep cache state for active clients. `update_segment()` accounts for opened inodes.

State and persistence behavior: Persistent payload is metablob context plus inode ids. It does not itself represent a mutation but preserves open-file recovery information.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `CInode`, and MDLog replay.

Risks: Omitting parent dentry context for non-base inodes can make replay unable to locate them. Snap inodes must use `vinodeno_t` to distinguish snapshots.

Test signals: Replay clean base and snap inodes, segment update accounting, and encode/decode with metablob context.
