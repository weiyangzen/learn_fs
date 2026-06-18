# sources/distributed-fs/ceph-client/fs/ocfs2/sysfile.h

Purpose: declares the system-file lookup interface for OCFS2 subsystems.

Important APIs and types: exposes `ocfs2_get_system_file_inode(struct ocfs2_super *osb, int type, u32 slot)`.

Control flow: callers pass a system inode type and slot, receiving a referenced inode or NULL. Global system inode types ignore slot semantics; local types are resolved per slot.

State and persistence behavior: the function declared here uses runtime inode caches in `struct ocfs2_super` and persistent system directory entries on disk, but the header stores no state.

Dependencies and integration points: included by mount, allocator, quota, statfs, journal, and recovery code needing system inodes.

Risks: callers must `iput` successful returns and must pass valid slot values for local system inodes. Treating NULL as a recoverable condition where a system inode is mandatory can hide filesystem corruption.

Test signals: compile coverage for all system inode consumers, reference leak checks around repeated get/iput cycles, and error paths where mandatory system files are absent.
