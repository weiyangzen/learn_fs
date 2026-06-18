# sources/distributed-fs/ceph-client/fs/lockd/svcsubs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcsubs.c` provides support routines for the NLM server file table and resource cleanup. It maps NLM file handles to opened VFS files, tracks file references, traverses locks/blocked locks/shares, and exports cleanup helpers used by NFSD failover and network events. The source was read as a complete 521-line file for this report.

## Important APIs, Types, and Functions

Important state includes `nlm_files[FILE_NRHASH]` and `nlm_file_mutex`. Public/common functions include `lock_to_openmode`, `nlm_lookup_file`, `nlm_release_file`, `nlmsvc_mark_resources`, `nlmsvc_free_host_resources`, `nlmsvc_invalidate_all`, `nlmsvc_unlock_all_by_sb`, and `nlmsvc_unlock_all_by_ip`. Core helpers include `nlm_do_fopen`, `nlm_delete_file`, `nlm_unlock_files`, `nlm_traverse_locks`, `nlm_inspect_file`, `nlm_file_inuse`, `nlm_close_files`, and `nlm_traverse_files`.

## Control Flow

`nlm_lookup_file` hashes the NFS file handle, serializes the table with `nlm_file_mutex`, opens the needed read or write VFS file through `nlmsvc_ops->fopen`, creates a new `nlm_file` if required, links it into the hash table, and increments `f_count`. `nlm_release_file` decrements `f_count` and deletes the record if no file references, blocked locks, shares, or NLM-managed VFS locks remain. Cleanup APIs traverse every hash bucket, temporarily pin each file, call `nlmsvc_traverse_blocks`, `nlmsvc_traverse_shares`, and `nlm_traverse_locks`, then remove idle files. Superblock and IP cleanup pass match predicates to this traversal.

## State and Persistence Behavior

The file table is in-memory and global to lockd. Each `nlm_file` keeps a file handle, optional read/write `struct file` pointers, a reference count, a block list, share list, and cached lock count. VFS file opens are closed through `nlmsvc_ops->fclose` when the `nlm_file` is deleted or traversal finds it idle. There is no on-disk state here.

## Dependencies and Integration Points

It depends on NFSD-provided lockd bindings (`nlmsvc_ops->fopen`/`fclose`), VFS lock contexts from `locks_inode_context`, `vfs_lock_file`, lock manager identity `nlmsvc_lock_operations`, host matching helpers, SUNRPC address comparison, and share/block traversal functions from companion lockd files. It exports cleanup hooks for filesystems and network address handling.

## Risks and Edge Cases

File-handle hashing uses only the NFSv2-size bytes, so collisions are expected and handled by full handle comparison. Opening reexported files can block the lockd thread. `-EWOULDBLOCK` maps to an internal drop-reply status. Cleanup cannot rely on exact refcounts because VFS locks can be split/merged without lockd notification, so it scans inode lock lists. Traversal temporarily drops the file-table mutex, requiring careful `f_count` pinning. Failure to unlock all resources triggers warnings and in one path `BUG()`.

## Test Signals

Test lookup of existing and new file handles for read/write modes, stale handle and deferred open mapping, file release after lock/share/block cleanup, host resource free after client reboot/FREE_ALL, server shutdown invalidation, `nlmsvc_unlock_all_by_sb`, `nlmsvc_unlock_all_by_ip`, and leak warnings when VFS locks remain on file removal.
