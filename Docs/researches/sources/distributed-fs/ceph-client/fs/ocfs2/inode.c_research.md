# sources/distributed-fs/ceph-client/fs/ocfs2/inode.c

## Purpose
`inode.c` implements the OCFS2 VFS inode lifecycle: translating on-disk `struct ocfs2_dinode` records into VFS inodes, validating and repairing dinode blocks, keeping inode metadata coherent with the journal, and coordinating clustered deletion through orphan directories and open locks. It is one of the main integration points between Linux inode operations and OCFS2 cluster locking, metadata caching, quotas, truncate logs, xattrs, refcount trees, and filecheck.

## Important APIs, types, and functions
- `struct ocfs2_find_inode_args` packages block number, VFS inode number, iget flags, and system file type for `iget5_locked()`.
- `ocfs2_ilookup()` and `ocfs2_iget()` are the public lookup/load entry points. `ocfs2_iget()` validates block zero, calls `iget5_locked()`, runs `ocfs2_read_locked_inode()` for new inodes, and seeds fsync transaction ids from JBD2.
- `ocfs2_populate_inode()` maps disk dinode fields into `struct inode` and `struct ocfs2_inode_info`, sets inode/file/address-space operations, system and bitmap flags, lock resources, and directory allocation reservation type.
- `ocfs2_read_locked_inode()` optionally takes OCFS2 open/meta locks, reads and validates the dinode, populates the inode, and writes out dirty non-JBD buffers after checksum repair paths.
- `ocfs2_evict_inode()`, `ocfs2_delete_inode()`, `ocfs2_wipe_inode()`, and `ocfs2_remove_inode()` implement clustered deletion and inode allocator release.
- `ocfs2_mark_inode_dirty()` and `ocfs2_refresh_inode()` synchronize mutable inode fields between VFS memory and disk dinodes.
- `ocfs2_validate_inode_block()`, `ocfs2_filecheck_validate_inode_block()`, and `ocfs2_filecheck_repair_inode_block()` validate signatures, generation, flags, slot bounds, inline data, chain-list geometry, refcount location, and metadata ECC.
- `ocfs2_inode_caching_ops` exposes owner, superblock, cache lock, and I/O lock callbacks for the OCFS2 metadata cache.

## Control flow
Inode acquisition starts in `ocfs2_iget()`, which fills `ocfs2_find_inode_args`, invokes `iget5_locked()` with `ocfs2_find_actor()` and `ocfs2_init_locked_inode()`, then calls `ocfs2_read_locked_inode()` while the inode is new. The read path decides whether cluster locking is safe: ordinary inodes can take open and metadata locks, while system files, orphan recovery loads, and local mounts avoid that path. It then reads the block through either the cached OCFS2 metadata path or synchronous raw block I/O, optionally using filecheck validation or repair, and calls `ocfs2_populate_inode()`.

Deletion is deliberately staged. `ocfs2_evict_inode()` writes the inode and either truncates pages or enters `ocfs2_delete_inode()` when link count is zero or the inode may be remotely orphaned. `ocfs2_delete_inode()` blocks signals, takes the NFS sync lock, takes the inode metadata lock, rejects DIO-orphaned entries, and asks `ocfs2_query_inode_wipe()` whether an exclusive open lock can be obtained cluster-wide. If so, `ocfs2_wipe_inode()` locks the owning orphan directory, truncates file data, removes directory indexes, xattrs, and refcount trees, then `ocfs2_remove_inode()` clears `OCFS2_VALID_FL`/`OCFS2_ORPHANED_FL`, timestamps deletion, drops quotas, and frees the dinode from the inode allocator.

Metadata update flow is the standard OCFS2 journal dance: call `ocfs2_journal_access_di()`, mutate the dinode fields, call `ocfs2_journal_dirty()`, and update inode fsync transaction ids. `ocfs2_clear_inode()` waits for checkpointing before destroying locks unless the inode was fully deleted.

## State and persistence behavior
Persistent state is primarily in dinode fields: block number, mode, link count, size, cluster count, timestamps, attributes, dynamic features, generation, slot ownership, orphan flags, deletion time, inline data, chain lists, and metadata ECC. In-memory state lives in `ocfs2_inode_info`: cluster locks, allocation/xattr semaphores, metadata cache, extent map, open count, orphan recovery link, direct-I/O markers, reservation state, and fsync transaction ids. The code treats cluster locks as the validity boundary for trusting cached inode contents. Deletes persist by journaling the dinode changes and inode allocator updates; checkpointing protects lock teardown from unflushed metadata.

## Dependencies and integration points
This file depends on OCFS2 DLM glue for metadata/open/rw locks, JBD2 through `journal.h`, metadata cache and buffer-head I/O, suballocator code, directory/orphan helpers, xattr removal, refcount-tree removal, truncate handling, quota accounting, filecheck error codes, and tracepoints. VFS integration happens through inode operation and file operation assignment in `ocfs2_populate_inode()` plus eviction/revalidation hooks.

## Risks and edge cases
- Clustered delete correctness relies on lock ordering among NFS sync, inode meta lock, orphan dir lock, and open lock. The code contains explicit deadlock avoidance for downconvert and orphan recovery contexts.
- Repair paths intentionally avoid repairing JBD-owned buffers and emergency/read-only states.
- Dinode validation differentiates local checksum failures from fatal structural errors; test expectations should reflect which failures abort the filesystem.
- `ocfs2_delete_inode()` blocks signals because `-ERESTARTSYS` during deletion could leave permanent orphan entries.
- Filecheck repair changes only a limited set of fields, such as `i_blkno`, generation, `l_next_free_rec`, and ECC; it does not blindly restore validity flags.

## Test signals
Useful tests include cold-cache `stat`/iget on normal and system files, filecheck check/fix injections for bad ECC, block number, generation, and extent-list counters, clustered unlink while another node holds an open lock, orphan recovery racing with local eviction, DIO orphan cleanup, quota-enabled delete, reflink/refcount delete, and eviction after uncheckpointed inode metadata.
