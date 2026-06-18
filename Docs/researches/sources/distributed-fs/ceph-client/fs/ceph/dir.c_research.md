# Research: sources/distributed-fs/ceph-client/fs/ceph/dir.c

## Purpose

`dir.c` implements CephFS directory and dentry behavior for the Linux VFS. It covers directory reads, lookup, create-like operations, hard links, unlink/rmdir, rename, dentry lease validation, complete-directory cache management, snapdir handling, and directory-specific file/inode/dentry operation tables.

The file is the main bridge between VFS pathname operations and Ceph MDS metadata requests. It also owns much of the client-side directory coherency model: per-dentry leases, directory-wide `CEPH_CAP_FILE_SHARED` completeness, ordered readdir cache state, dentry lease trimming, and invalidation when dentries are pruned or leases expire.

## Important APIs, Types, and Functions

- `ceph_d_init()` allocates `struct ceph_dentry_info`, initializes lease list state, attaches it to `dentry->d_fsdata`, and increments the total-dentry metric.
- Readdir position helpers (`ceph_make_fpos()`, `is_hash_order()`, `fpos_frag()`, `fpos_hash()`, `fpos_off()`, `fpos_cmp()`) encode Ceph directory fragment/hash position state into VFS `loff_t` offsets.
- `note_last_dentry()` stores the last emitted name and next offset in `struct ceph_dir_file_info` so later MDS READDIR requests can resume robustly after directory changes.
- `__dcache_find_get_entry()` and `__dcache_readdir()` implement dcache-backed readdir for complete ordered directories.
- `ceph_readdir()` is the primary `iterate_shared` implementation. It emits `.` and `..`, chooses dcache vs MDS READDIR/LSSNAP, manages fragments, tracks cache completeness, and emits directory entries.
- `reset_readdir()`, `need_reset_readdir()`, and `ceph_dir_llseek()` keep buffered readdir state coherent across seekdir/llseek.
- `ceph_handle_snapdir()` synthesizes the hidden `.snap` directory when lookup receives ENOENT on the configured snapdir name.
- `ceph_finish_lookup()` normalizes MDS lookup/open results for VFS dentry expectations, including no-trace ENOENT and spliced dentries.
- `ceph_lookup()` handles ordinary and snapdir lookups, fscrypt partial lookup preparation, local negative lookup from complete directory cache, and MDS LOOKUP/LOOKUPSNAP fallback.
- Mutation operations `ceph_mknod()`, `ceph_create()`, `ceph_symlink()`, `ceph_mkdir()`, `ceph_link()`, `ceph_unlink()`, and `ceph_rename()` translate VFS operations into MDS requests with cap-drop hints, parent locking flags, quota checks, fscrypt handling, ACL/security context propagation, and snap semantics.
- Async unlink helpers `get_caps_for_async_unlink()` and `ceph_async_unlink_cb()` allow local unlink completion when the client holds sufficient directory caps, with conflict tracking through `fsc->async_unlink_conflict`.
- Lease functions `__ceph_dentry_lease_touch()`, `__ceph_dentry_dir_lease_touch()`, `__dentry_leases_walk()`, `ceph_trim_dentries()`, `ceph_invalidate_dentry_lease()`, `dentry_lease_is_valid()`, `dir_lease_is_valid()`, and `ceph_d_revalidate()` manage dentry lease lists, expiration, renewal, and VFS d_revalidate behavior.
- Dentry lifecycle callbacks `ceph_d_delete()`, `ceph_d_release()`, and `ceph_d_prune()` decide whether unused dentries are retained, free Ceph-private dentry state, and clear complete/ordered directory flags when VFS pruning invalidates cache assumptions.
- `ceph_read_dir()` implements the optional `-o dirstat` directory read interface.
- `ceph_dentry_hash()` computes the MDS-compatible name hash for export/snapshot lookup users.
- Operation tables `ceph_dir_fops`, `ceph_snapdir_fops`, `ceph_dir_iops`, `ceph_snapdir_iops`, and `ceph_dentry_ops` register this file's behavior with VFS.

## Control Flow

### Readdir

`ceph_readdir()` starts by emitting `.` and `..` for positions 0 and 1. It then prepares fscrypt state and touches write fmode on the directory so later create/unlink paths do not have to drop shared caps unnecessarily. If the `DCACHE` mount option is enabled, async readdir is not disabled, the inode is not a snapdir, the directory is complete and ordered, and the client holds `CEPH_CAP_FILE_SHARED`, it attempts `__dcache_readdir()`.

`__dcache_readdir()` uses the directory page cache as an array of dentry pointers. It binary-searches cached offsets for the starting `ctx->pos`, validates each dentry under lock, checks shared generation, skips no-key encrypted names once the key is available, emits entries with `dir_emit()`, updates `ctx->pos`, and records the last emitted dentry name. Any stale/missing cache state returns `-EAGAIN`, causing `ceph_readdir()` to fall back to MDS READDIR.

The MDS path creates `CEPH_MDS_OP_READDIR` or `CEPH_MDS_OP_LSSNAP`, allocates a reply buffer, selects a fragment/hash position, includes last-name or hash-offset resume information, sends the request, and emits entries from `req->r_reply_info`. It tracks whether the MDS prepopulated dentries into dcache. At the end of all fragments, if no dentries were released and the ordered count still matches, it marks the directory complete and possibly ordered, using `i_size` as the count of cached dentry pointers.

### Lookup and Create

`ceph_lookup()` first handles fscrypt preparation and can answer local ENOENT when a negative dentry is in a complete directory with a valid shared cap and is not the snapdir/root special name. Otherwise it sends LOOKUP/LOOKUPSNAP with inode/auth/xattr caps requested. ENOENT on the snapdir name is converted to a snapdir inode by `ceph_handle_snapdir()`, and `ceph_finish_lookup()` converts no-trace replies into VFS-compatible dentry results.

`ceph_mknod()`, `ceph_symlink()`, and `ceph_mkdir()` allocate a new inode with `ceph_new_inode()`, attach security/ACL context to the request, set parent-locked state, request two caps, and provide cap drop/unless hints so the MDS can invalidate cached directory state. Symlink creation encrypts and base64-encodes the target when needed. `ceph_mkdir()` also maps `mkdir .snap/name` to `CEPH_MDS_OP_MKSNAP`.

`ceph_handle_notrace_create()` handles old/no-trace create replies by issuing a lookup. If lookup splices another dentry, it drops that result and returns `-ESTALE` to avoid confusing VFS.

### Link, Unlink, Rename

`ceph_link()` prepares fscrypt link semantics, submits `CEPH_MDS_OP_LINK`, drops source link caps, and instantiates the new dentry manually when the MDS returns no trace.

`ceph_unlink()` maps snapdir rmdir to RMSNAP, ordinary directory removal to RMDIR, and ordinary file removal to UNLINK. It checks local MDS auth access when possible. With `ASYNC_DIROPS`, ordinary unlink can be submitted asynchronously if the client holds `CEPH_CAP_FILE_EXCL | CEPH_CAP_DIR_UNLINK` and the dentry is a primary linkage with the current shared generation. The async path sets `CEPH_DENTRY_ASYNC_UNLINK`, inserts the dentry into the conflict hash, submits the request, decrements local link count, and deletes the dentry. Completion removes the conflict hash entry, wakes waiters, and on failure marks parent/target mappings with errors, clears directory completeness, and drops uncertain dentries. `-EJUKEBOX` falls back to synchronous retry.

`ceph_rename()` rejects unsupported flags, cross-snapshot rename, non-snap writable violations, and cross-quota-realm moves. It maps snapdir same-directory rename to RENAMESNAP, otherwise sends RENAME with old/new dentries, parent state, and cap drop hints; no-trace success is repaired with `d_move()`.

### Lease and Dentry Validation

VFS `d_revalidate` calls `ceph_d_revalidate()`. It delegates fscrypt validity first, trusts snapped dentries and snapdir dentries, then checks a per-dentry lease with possible renewal. If the dentry lease is missing, it checks the directory-wide lease by verifying `CEPH_CAP_FILE_SHARED` and matching shared generation. If neither validates, it sends LOOKUP/LOOKUPSNAP outside RCU walk and marks hit/miss metrics. Invalid revalidation clears the directory complete flag.

`ceph_trim_dentries()` periodically walks the dentry lease lists to remove invalid leases and optionally expire directory leases when cap pressure exceeds `caps_use_max`. The walker uses `spin_trylock()` to avoid blocking on dentry locks, handles live/refcounted dentries differently from zero-ref dentries, and uses a dispose list with `dput()` to let `ceph_d_delete()` reclaim stale dentries.

## State and Persistence Behavior

Directory state is mostly volatile cache/coherency state:

- `struct ceph_dentry_info` stores lease session, lease generation/sequence, expiration/renewal times, directory shared generation, readdir offset, flags, and membership in MDS client lease lists.
- `struct ceph_dir_file_info` stores per-open readdir state: last MDS readdir request, last emitted name, fragment, next offset, ordered/release counts, readdir cache index, and optional dirstat text.
- Directory completeness and ordered readdir state live in `struct ceph_inode_info` flags/counters and can be cleared by dentry pruning, lookup misses, async operation failure, or explicit invalidation.
- MDS mutation requests persist metadata changes in the Ceph cluster. Local dcache/inode updates are optimistic in async cases and authoritative only once MDS replies are integrated by the MDS client.
- Snapdir operations map VFS names under the configured snapdir to Ceph snapshot metadata operations.

No on-disk local state is written here. Persistence is achieved through MDS requests and OSD-backed CephFS metadata/data semantics outside this file.

## Dependencies and Integration Points

- VFS directory, inode, dentry, and file operation tables call into this file.
- `mds_client.h` supplies request allocation/submission, MDS op codes, reply parsing, cap handling, path building, access checks, and session/lease primitives.
- `super.h` supplies mount options, Ceph inode/dentry/file structures, inode helpers, quota helpers, and cap helpers.
- `crypto.h` supplies fscrypt name lookup, encrypted dname encoding, encrypted symlink target handling, and user-name conversion hooks.
- Linux dcache, RCU, lockref, inode locking, page cache, and seq/hash primitives are used for local cache management.
- Metrics are updated through `mdsc->metric` counters for total dentries, dentry lease hits/misses, and cap metrics.
- `ceph_atomic_open()` is declared in `file.c` but registered here in `ceph_dir_iops`, tying directory lookup/create behavior to file open behavior.

## Risks and Edge Cases

- Readdir offset encoding is Ceph-specific and must preserve ordering across fragmented/hash-ordered directories. Bugs in offset comparison or resume name handling can skip or duplicate entries.
- Dcache readdir is safe only when directory completeness, ordered count, release count, and shared generation remain valid. Dentry pruning explicitly clears complete/ordered flags because stale cached dentries would otherwise be visible.
- Lease renewal cannot be performed in RCU walk; `dentry_lease_is_valid()` returns `-ECHILD` in that case so VFS retries in ref-walk mode.
- Async unlink is optimistic. Failure must propagate mapping errors and clear uncertain cache state; conflict tracking is required so later operations wait for in-flight async unlink on the same name.
- Fscrypt no-key names and later key availability can invalidate complete-directory assumptions; lookup clears completeness when a directory transitions from locked to unlocked.
- Snapdir has special semantics: `.snap` is hidden, snapshots are read-only except for MKSNAP/RMSNAP/RENAMESNAP through snapdir operations, and normal mutation in snapshots returns `-EROFS`.
- Several paths intentionally fall back to MDS authority rather than relying on local access/path checks when path construction or access check returns non-EACCES errors.
- Quota checks are local preflights but the MDS remains authoritative for races with other clients.

## Test Signals

Validation should cover:

- Readdir across fragmented directories, hash-ordered replies, seekdir/llseek, small buffers that stop `dir_emit()`, and transition from MDS readdir to complete ordered dcache readdir.
- Negative lookup from complete directory cache and invalidation after dentry prune/drop.
- Fscrypt directories before and after key availability, including encrypted symlink creation and no-key dentry revalidation.
- Snapdir lookup, `mkdir .snap/name`, `rmdir .snap/name`, and snap rename behavior.
- Create/mknod/mkdir/symlink/link/rename/unlink with cap drop hints and no-trace MDS replies.
- Async unlink success, `-EJUKEBOX` fallback, failure error propagation, conflict wait behavior, and local link count correction.
- Lease hit/miss counters, lease renewal, RCU walk fallback, and trimming under cap pressure.
- Optional `-o dirstat` directory reads.
