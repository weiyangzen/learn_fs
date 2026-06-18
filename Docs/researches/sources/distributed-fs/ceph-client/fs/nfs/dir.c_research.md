# sources/distributed-fs/ceph-client/fs/nfs/dir.c

## Purpose
`dir.c` implements the Linux NFS client directory and path-name side of VFS integration. It provides directory file operations, READDIR/READDIRPLUS caching, dentry revalidation, lookup and atomic-open plumbing, directory mutation operations, silly-rename coordination for active unlinks, rename/link/symlink handling, and the per-credential ACCESS cache used by permission checks.

## Important APIs, types, and functions
The exported surfaces include `nfs_dir_operations`, `nfs_dir_aops`, `nfs_dentry_operations`, `nfs4_dentry_operations`, `nfs_lookup`, `nfs_atomic_open`, `nfs_atomic_open_v23`, `nfs_add_or_obtain`, `nfs_instantiate`, `nfs_create`, `nfs_mknod`, `nfs_mkdir`, `nfs_rmdir`, `nfs_unlink`, `nfs_symlink`, `nfs_link`, `nfs_rename`, `nfs_access_get_cached`, `nfs_access_add_cache`, `nfs_access_set_mask`, `nfs_may_open`, and `nfs_permission`.

`struct nfs_open_dir_context` is allocated per opened directory and tracks directory cookie position, verifier bytes, adaptive directory transfer size, EOF state, and READDIRPLUS cache-hit/miss hints. `struct nfs_cache_array` is stored in page-cache folios and contains decoded directory entries, a starting/last cookie, change attribute, EOF/full flags, and a monotonic-cookie hint. `struct nfs_readdir_descriptor` is the transient state machine for a single `iterate_shared` call.

## Control flow
Directory open allocates an open-dir context, records current inode generation and cookie verifier, and links the context onto the NFS inode open-file list. `nfs_readdir` revalidates the mapping, copies the persistent cursor from the open context, decides whether to request READDIRPLUS from cache-hit/miss heuristics, and then searches/fills folio-backed cache arrays until either the caller buffer is full, EOF is reached, or an error stops iteration.

READDIR cache misses flow through `find_and_lock_cache_page`. It hashes the last cookie to a page-cache index, validates the folio against the directory change attribute and starting cookie, and fills it by issuing `NFS_PROTO(inode)->readdir`. XDR pages are decoded into cache arrays by `nfs_readdir_folio_filler`; READDIRPLUS entries also call `nfs_prime_dcache` to refresh or instantiate matching dentries. Bad cookies or verifier changes invalidate page-cache ranges and rewind the search. When a cookie cannot be found in page cache, `uncached_readdir` reads into anonymous folios and emits entries without installing them into the mapping.

Dentry validation starts with `nfs_lookup_revalidate` or `nfs4_lookup_revalidate`. The common path checks a blocked unlink/rename marker in `d_fsdata`, verifies parent directory change attributes saved in `d_time`, handles delegation-tagged dentries, and either trusts the cached inode or sends a fresh LOOKUP. Negative dentries are revalidated according to lookup-cache mount flags, create/rename intent, case-insensitive server capability, and parent change attributes. Atomic open for NFSv4 uses `open_context`, then `finish_open`; NFSv2/v3 emulate lookup-open with a create fast path.

Mutation operations call protocol methods through `NFS_PROTO(dir)`, then carefully update dcache and inode state. Failed create/mknod drops the dentry because the server may have completed the operation despite a reply error. Remove and rename block dentry revalidation while an unlink or target replacement is in flight, use silly rename when an active target cannot be removed, force writeback before unsafe file rename/link cases, and invalidate or update link count/change attributes after success.

Permission checks first consult a per-inode rb-tree keyed by fsuid, fsgid, and supplementary groups. If no usable cache entry exists, `nfs_do_access` sends ACCESS RPCs, stores the returned NFS access bits, converts them to VFS MAY bits, and applies local execute-bit checks.

## State and persistence behavior
No durable on-disk state is owned here; persistence is remote server state accessed through NFS protocol operations. Runtime state includes directory page-cache folios that store decoded names, per-open readdir cursors, NFS inode cookie verifiers, dentry verifiers in `d_time`, unlink/rename revalidation blocks in `d_fsdata`, access-cache rb-trees and LRUs, and NFS inode cache-validity bits.

Directory cache coherency depends on the parent directory change attribute and cookie verifier. When either changes, folios are reinitialized or invalidated so future `getdents` calls cannot reuse stale cookies. Dentry coherency relies on saved parent verifiers and delegation tags; delegation revocation clears the tag so later pathwalks perform real validation.

## Dependencies and integration points
The file integrates with VFS directory, dentry, inode, permission, and file-locking interfaces; SUNRPC/NFS protocol operation vectors; NFS inode cache invalidation; NFSv4 delegations and atomic OPEN; pNFS-independent writeback through `nfs_sync_inode`; fscache open context setup; idmapped VFS create hooks; Linux shrinker infrastructure for access-cache reclaim; and tracepoints in `nfstrace.h`.

Cross-file contracts include inode construction via `nfs_fhget`, protocol-specific lookup/create/remove/rename/access callbacks, silly-rename helpers, NFS open contexts from the regular file path, and NFSv4 directory delegation helpers.

## Risks
The highest-risk area is cache coherency. Incorrect verifier updates, failure to invalidate directory folios on cookie verifier changes, or trusting negative dentries on case-insensitive servers can produce stale lookups or missing entries. READDIR cookie hashing intentionally admits collisions, so validation by starting cookie and change attribute is essential.

Concurrency risks include races between unlink/rename and open/pathwalk, RCU pathwalk returning `-ECHILD` at the right points, dentry alias invalidation during READDIRPLUS priming, and access-cache rb-tree/LRU updates under inode and global locks. Silly rename paths must not leave `d_fsdata` blocked or leak renamed dentries. Access-cache timestamps also depend on login ancestry and must not grant permissions after a credential transition.

## Test signals
Useful signals include READDIR over changing directories, bad-cookie server replies, verifier changes between page-cache fills, 32-bit getdents position mode, READDIRPLUS fallback on `-ENOTSUPP`, dcache priming with stale aliases, case-insensitive negative lookups, lookup-cache mount flags, NFSv4 delegated pathwalks and delegation revocation, atomic open create/truncate/error cases, unlink of open files, rename over busy targets, cross-directory rename with unstable filehandles, ACCESS cache hits/misses/reclaim, and RCU pathwalk fallbacks.
