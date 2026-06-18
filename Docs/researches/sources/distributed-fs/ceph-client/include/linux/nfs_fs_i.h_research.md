# sources/distributed-fs/ceph-client/include/linux/nfs_fs_i.h

Purpose: Defines lock-owner metadata embedded in NFS file/inode state for NFS lock manager and NFSv4 locks.

Important APIs, types, and functions: Exports `struct nfs_lock_info` and `struct nfs4_lock_info`. Detected source surface: 21 lines; includes none; macros `_NFS_FS_I`; structs `list_head`, `nfs4_lock_info`, `nfs4_lock_state`, `nfs_lock_info`, `nlm_lockowner`; enums none; typedefs none; function-like declarations/helpers none.

Control flow: Locking code associates VFS file locks with NLM lock owners or NFSv4 lock state so lock/unlock RPCs can be matched to owner identity.

State and persistence behavior: The fields persist with the relevant file/inode lock context while locks are active.

Dependencies and integration points: Integrates with NLM lock owners and NFSv4 lock state definitions.

Risks and test signals: Risks are lock-owner aliasing and stale lock state after recovery. Test POSIX byte-range locks, reclaim, unlock, and mixed local/remote owners.
