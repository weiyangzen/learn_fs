# sources/distributed-fs/ceph-client/fs/autofs/autofs_i.h

Purpose: Internal autofs header defining shared structures, flags, helpers, and prototypes for the autofs filesystem implementation.

Important APIs and types: `struct autofs_info` stores per-dentry state, flags, expiry completion, active/expiring lists, owner ids, timeout, and dentry reference. `struct autofs_sb_info` stores superblock-wide daemon pipe, owning process group, mount namespace id, protocol versions, flags, default timeout, type, locks, wait queues, and active/expiring lists. Helper APIs include `autofs_sbi()`, `autofs_dentry_ino()`, `autofs_oz_mode()`, pipe validation/preparation helpers, managed-dentry flag helpers, expiring-list helpers, and prototypes for wait, expire, inode, root, and ioctl code.

Control flow: Other autofs files include this header to coordinate mount setup, wait queue messaging, dentry management, expiry selection, and misc-device ioctl control. Inline helpers centralize common lock and flag manipulation.

State and persistence: Defines the core runtime state persisted for each mounted autofs superblock and each autofs dentry/inode. Flags such as `AUTOFS_INF_PENDING`, `AUTOFS_INF_WANT_EXPIRE`, and `AUTOFS_INF_EXPIRING` coordinate lookup and expiry. Superblock flags include catatonic, strict expire, and ignore modes.

Dependencies and integration points: Depends on VFS dentries/inodes/superblocks, mount APIs, fs_context, uapi autofs ioctl definitions, pid namespaces, pipes, wait queues, RCU, spinlocks, and mutexes.

Risks: This header sets locking expectations for all autofs code. Misusing `lookup_lock`, `fs_lock`, or expiring flags can cause RCU-walk hazards, missed expiry completion, or stale daemon communication state.

Test signals: Mount setup, daemon pipe validation, oz-mode permission checks, managed dentry flag transitions, per-dentry expiry list add/remove, catatonic behavior, and lookup behavior while entries are pending or expiring.
