# sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.h

Purpose: declares the OCFS2 cluster-locking interface and LVB wire layouts used by `dlmglue.c` and the rest of the filesystem. It is the public contract for metadata, data/RW, open, dentry, flock, quota, refcount, NFS-sync, trim, orphan-scan, and superblock locking helpers.

Important APIs and types: defines `OCFS2_LVB_VERSION`, `struct ocfs2_meta_lvb`, `struct ocfs2_qinfo_lvb`, `struct ocfs2_orphan_scan_lvb`, `struct ocfs2_trim_fs_lvb`, `struct ocfs2_trim_fs_info`, and `struct ocfs2_lock_holder`. It declares all lock lifecycle and acquisition functions, including `ocfs2_dlm_init`, `ocfs2_dlm_shutdown`, `ocfs2_create_new_inode_locks`, `ocfs2_rw_lock`, `ocfs2_open_lock`, `ocfs2_inode_lock_full_nested`, `ocfs2_inode_lock_with_folio`, `ocfs2_inode_lock_tracker`, `ocfs2_super_lock`, `ocfs2_nfs_sync_lock`, `ocfs2_trim_fs_lock`, `ocfs2_file_lock`, `ocfs2_qinfo_lock`, and `ocfs2_refcount_lock`.

Control flow: the header has no active control flow, but its wrappers shape call sites. `ocfs2_inode_lock`, `ocfs2_try_inode_lock`, `ocfs2_inode_lock_full`, and `ocfs2_inode_lock_nested` standardize normal, noqueue, flagged, and lockdep-subclassed metadata locking. `OCFS2_META_LOCK_RECOVERY`, `OCFS2_META_LOCK_NOQUEUE`, `OCFS2_LOCK_NONBLOCK`, and `OCFS2_META_LOCK_GETBH` alter waiting, DLM queueing, folio-lock avoidance, and disk-buffer retrieval.

State and persistence behavior: the LVB structs are DLM lock value block formats shared between nodes. They store inode metadata, quota grace/free counts, orphan scan sequence numbers, and trimfs result metadata in big-endian fields. `ocfs2_lock_holder` is transient stack-associated state used to detect and suppress recursive cluster locking inside one task.

Dependencies and integration points: includes `dcache.h` for dentry-lock data and forwards OCFS2-specific types from inode, quota, refcount, and file layers. Callers across file, inode, dir, quota, refcount, export, xattr, and recovery code rely on these declarations to coordinate cluster coherence before reading or mutating shared disk structures.

Risks: LVB layout changes require matching protocol/version handling in clustered deployments. Misusing `OCFS2_META_LOCK_GETBH` or the tracker API can bypass expected lock acquisition or mask recursive locking bugs. The noqueue/nonblock flags are used to avoid deadlocks with folio locks and nowait I/O, so callers must propagate `-EAGAIN` or `AOP_TRUNCATED_PAGE` correctly.

Test signals: compile coverage for all OCFS2 configs, mixed-node lock protocol tests, metadata LVB version compatibility, noqueue inode-lock users, recursive ACL/setattr and permission paths, trim/orphan LVB read/write, and callers using `ocfs2_inode_lock_with_folio` from address-space operations.
