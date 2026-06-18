# Group Research: group_723_linux_sources_os_linux_linux_fs_ceph_debugfs_c_sources_os_linux_linu_1679d935182b

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. This grouped report covers the requested CephFS Linux client files only.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/debugfs.c -->
# File Research: sources/os/linux/linux/fs/ceph/debugfs.c

## Role

`debugfs.c` provides CephFS client debugfs files when `CONFIG_DEBUG_FS` is enabled. It is a read-mostly inspection layer over the mounted filesystem client, MDS client, sessions, caps, request tree, and metrics. With debugfs disabled, `ceph_fs_debugfs_init()` and `ceph_fs_debugfs_cleanup()` compile to empty stubs.

## Main Interfaces

- `ceph_fs_debugfs_init(struct ceph_fs_client *fsc)` creates debugfs entries under `fsc->client->debugfs_dir`.
- `ceph_fs_debugfs_cleanup(struct ceph_fs_client *fsc)` removes those entries.
- `DEFINE_SHOW_ATTRIBUTE(...)` exports seq_file show handlers for `mdsmap`, `mdsc`, `caps`, `mds_sessions`, `status`, metric files, `metric_features`, and `subvolumes`.
- `congestion_kb_fops` is a writable simple attribute for `mount_options->congestion_kb`.

## Debugfs Tree

Created entries include:

- `writeback_congestion_kb`: read/write mount writeback congestion threshold.
- `bdi`: symlink to the backing device info debugfs entry.
- `mdsmap`: current MDS map epoch/root/max/session timings/rank address/state.
- `mds_sessions`: client global id, mount name, and active MDS session states.
- `mdsc`: in-flight MDS requests, operation names, unsafe state, and involved paths/inodes.
- `caps`: cap reservation status, per-session inode cap issuance, and cap waiters.
- `status`: client entity instance/address/nonce and blocklisted state.
- `metrics/file`, `metrics/latency`, `metrics/size`, `metrics/caps`, `metrics/metric_features`, `metrics/subvolumes`.

## Data and Control Flow

- `mdsmap_show()` reads `fsc->mdsc->mdsmap` and dumps core map fields plus rank state names from `ceph_mds_state_name()`.
- `mdsc_show()` locks `mdsc->mutex`, walks `mdsc->request_tree`, formats request tids, sessions, ops, unsafe status, and primary/secondary target paths. It uses `ceph_mdsc_build_path()` for dentries and frees path info after printing.
- Metric show functions snapshot counters and per-metric spinlock-protected fields:
  - `metrics_file_show()` reports inode/file/cap counters.
  - `metrics_latency_show()` prints total/average/min/max/stdev for read/write/metadata/copyfrom.
  - `metrics_size_show()` prints size totals for operations that have byte metrics, skipping metadata.
  - `metrics_caps_show()` reports dentry lease and inode cap hit/miss counters.
- `caps_show()` reports global cap reservation counts, then iterates MDS sessions and each session's caps with `ceph_iterate_session_caps()`. It also prints `mdsc->cap_wait_list`.
- `subvolume_metrics_show()` copies the last sent subvolume snapshot under `subvol_metrics_last_mutex`, prints it outside the mutex, then dumps pending metrics through `ceph_subvolume_metrics_dump()`.
- `metric_features_show()` snapshots the metric session feature bitset under `mdsc->mutex`, then explains whether client metrics and subvolume metrics are effectively enabled.

## Concurrency and Lifetime

- `mdsc->mutex` protects request tree and session table walks.
- Session-specific cap iteration is done by dropping `mdsc->mutex`, taking `session->s_mutex`, iterating, then reacquiring `mdsc->mutex`.
- Per-inode cap display takes `ci->i_ceph_lock`.
- Metric arrays use each metric's spinlock for coherent totals.
- Subvolume last-sent snapshots are duplicated with `kmemdup_array()` so formatting does not hold the mutex.
- Cleanup removes individual entries and recursively removes `debugfs_metrics_dir`; removal is tolerant of missing entries.

## Dependencies

This file depends on CephFS internal structures from `super.h`, `mds_client.h`, `metric.h`, and `subvolume_metrics.h`, plus libceph debugfs/auth/mon helpers. It does not implement filesystem behavior; it exposes runtime state maintained by directory, file, MDS, capability, and metric code.

## Error Handling and Edge Cases

- Missing `mdsc` or `mdsmap` yields empty or explanatory output, not errors.
- Failed path construction in request dumps is printed as an empty string.
- Failed subvolume snapshot allocation simply reports no last-sent entries while still printing counters and pending metrics.
- Min latency/size sentinels (`KTIME_MAX`, `U64_MAX`) are rendered as zero.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/debugfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/dir.c -->
# File Research: sources/os/linux/linux/fs/ceph/dir.c

## Role

`dir.c` implements CephFS directory VFS operations and dentry behavior: lookup, readdir, mkdir/mknod/symlink/link/unlink/rename, snapdir handling, directory seek state, dentry lease validation/trimming, dentry cache lifecycle, and directory operation tables.

## Main Interfaces

- File operations: `ceph_dir_fops`, `ceph_snapdir_fops`.
- Inode operations: `ceph_dir_iops`, `ceph_snapdir_iops`.
- Dentry operations: `ceph_dentry_ops`.
- Externally used helpers include `ceph_make_fpos()`, `ceph_handle_snapdir()`, `ceph_finish_lookup()`, `ceph_handle_notrace_create()`, `ceph_trim_dentries()`, `ceph_invalidate_dentry_lease()`, and `ceph_dentry_hash()`.

## Readdir Model

Ceph directory positions encode either fragment/name order or hash order:

- `ceph_make_fpos(high, off, hash_order)` combines fragment/hash and entry offset.
- `HASH_ORDER` marks hash-ordered positions.
- `fpos_frag()`, `fpos_hash()`, `fpos_off()`, and `fpos_cmp()` interpret encoded positions.

`ceph_readdir()` emits `.` and `..`, prepares fscrypt state, touches write fmode for later directory mutations, then tries dcache-backed iteration if:

- the `DCACHE` mount option is enabled,
- `NOASYNCREADDIR` is not set,
- the inode is not a snapdir,
- the directory is complete and ordered,
- and the client holds `CEPH_CAP_FILE_SHARED`.

If dcache iteration fails with `-EAGAIN`, it falls back to MDS `READDIR` or `LSSNAP`.

## Dcache Readdir

- `__dcache_find_get_entry()` locates dentry pointers stored in the directory inode page cache, locking the folio and using RCU plus lockref to safely take a live dentry.
- `__dcache_readdir()` binary-searches the cached dentry pointer array by stored `di->offset`, validates hash/order generation and fscrypt key state, emits entries, touches directory leases, and records the last emitted name.
- Dcache readdir is invalidated when ordered completeness no longer matches release/order counters, entries are missing, negative/unhashed, generation differs, or nokey dentries become decryptable.

## MDS Readdir

When a new chunk is needed, `ceph_readdir()`:

- creates `CEPH_MDS_OP_READDIR` or `CEPH_MDS_OP_LSSNAP`,
- allocates reply buffers,
- sets direct MDS/hash routing for directory fragments,
- encodes the last name for encrypted directories when resuming,
- passes release/order/cache index hints,
- pins the inode and dentry on the request,
- parses reply entries and emits them with `dir_emit()`.

It tracks `dfi->last_readdir`, `dfi->last_name`, `dfi->frag`, `dfi->next_offset`, `dir_release_count`, `dir_ordered_count`, and `readdir_cache_idx`. At the end of all fragments it can mark the directory complete and ordered if no dentries were released and order counters still match.

`ceph_dir_llseek()` supports `SEEK_SET` and `SEEK_CUR`, rejects `SEEK_END`, and resets buffered readdir state when seeking to zero, another fragment, before the current chunk, or across hash/non-hash ordering.

## Lookup and Snapdir Handling

- `ceph_lookup()` handles name length, fscrypt lookup preparation, local negative lookup from complete cached directories, and MDS `LOOKUP`/`LOOKUPSNAP`.
- `ceph_handle_snapdir()` maps the configured hidden snapdir name to `ceph_get_snapdir(parent)` for normal parent directories.
- `ceph_finish_lookup()` normalizes MDS lookup results, including `-ENOENT` without a trace, dentry splicing, and stale positive dentries.
- Root dentries beginning `.ceph` are not concluded locally negative by complete-directory logic.

## Create and Mutation Operations

- `ceph_mknod()` implements mknod and regular create via `ceph_create()`. It rejects non-head snapshots, waits for conflicting async unlink, checks max-files quota, allocates a new inode, sets fscrypt-file flags for encrypted regular files, attaches ACL/security context, and sends `MKNOD`.
- `ceph_symlink()` prepares encrypted symlink targets with fscrypt/base64 when needed, otherwise duplicates the target path, then sends `SYMLINK`.
- `ceph_mkdir()` handles normal `MKDIR` and `.snap/foo` as `MKSNAP`, including snapshot/fscrypt key restrictions and max-files quota.
- `ceph_link()` prepares fscrypt link context, sends `LINK`, drops source link caps, and locally instantiates on traceless success.
- `ceph_unlink()` handles `UNLINK`, `RMDIR`, and `.snap/foo` as `RMSNAP`. It can perform async unlink when `ASYNC_DIROPS` is enabled and the client holds sufficient directory caps.
- `ceph_rename()` supports ordinary rename and snap rename within snapdir, rejects flags, cross-snapshot rename, non-head snapshots, and cross-quota-realm moves.

Mutation requests consistently set dentry cap drop/unless masks so stale shared/auth/xattr/file caps are revoked or preserved according to MDS rules.

## Async Unlink

`get_caps_for_async_unlink()` requires `CEPH_CAP_FILE_EXCL | CEPH_CAP_DIR_UNLINK`, a matching shared generation, and a primary-link dentry. On async submission:

- the dentry is marked `CEPH_DENTRY_ASYNC_UNLINK`,
- added to `fsc->async_unlink_conflict`,
- the target inode is pinned in `req->r_old_inode`,
- and local nlink/dcache state is adjusted on successful submission.

`ceph_async_unlink_cb()` removes conflict tracking, clears the async bit, handles `-EJUKEBOX` specially, and on errors marks parent/target mappings, clears directory completeness, drops the dentry, logs the path, releases the old inode, and releases directory caps.

## Dentry Lease Management

Ceph tracks two lease lists:

- `mdsc->dentry_leases` for direct MDS dentry leases.
- `mdsc->dentry_dir_leases` for directory-wide shared-cap leases.

Important routines:

- `__ceph_dentry_lease_touch()` refreshes direct lease list position.
- `__ceph_dentry_dir_lease_touch()` refreshes directory lease list position while respecting still-valid direct leases.
- `__dentry_lease_is_valid()` validates lease generation and TTL against the session.
- `__dir_lease_try_check()` validates directory lease generation against parent `i_shared_gen` and `CEPH_CAP_FILE_SHARED`.
- `ceph_trim_dentries()` walks both lists, deleting stale leases and optionally expiring dir leases when cap pressure exceeds `caps_use_max`.
- `ceph_invalidate_dentry_lease()` clears lease generation, primary-link state, and unlists the dentry.

The walk logic uses `mdsc->dentry_list_lock`, `dentry->d_lock`, lockref liveness checks, shrink-list staging, and dget/dput to safely dispose unreferenced dentries.

## Dentry Revalidation and Lifecycle

`ceph_d_revalidate()` first delegates fscrypt validation. Snapped dentries and snapdir dentries are trusted. Normal dentries are valid if a direct dentry lease or directory lease is valid and any positive inode still has caps. Otherwise it does an MDS lookup, updates hit/miss metrics, and clears directory completeness if invalid.

`ceph_d_delete()` tells VFS to delete unused positive non-snapped dentries without valid leases. `ceph_d_release()` removes lease list membership, drops lease session references, decrements total-dentry metric, and frees `ceph_dentry_info`. `ceph_d_prune()` clears directory completeness/order when pruning can invalidate dcache readdir assumptions.

## Directory Read Hack and Hashing

`ceph_read_dir()` supports reading directory statistics as text only when mounted with `-o dirstat`; otherwise it returns `-EISDIR`. `ceph_dentry_hash()` returns either the VFS name hash or a Ceph layout-specific string hash for MDS directory partitioning and export support.

## Concurrency and Error Handling

- Directory mutations wait for conflicting async unlink on target dentries.
- Parent `i_rwsem` is assumed for several VFS operations and is marked via `CEPH_MDS_R_PARENT_LOCKED`.
- `i_ceph_lock` protects inode cap/shared-generation/completeness state.
- `dentry->d_lock` protects dentry lease fields, d_parent stability, and dentry-local flags.
- MDS request allocation and reply traces drive VFS dentry instantiation/splicing; traceless create replies are repaired with follow-up lookup where possible.
- Snapshot directories are mostly read-only except explicit snap create/remove/rename operations.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/export.c -->
# File Research: sources/os/linux/linux/fs/ceph/export.c

## Role

`export.c` implements Linux `export_operations` for CephFS, enabling exportfs/NFS-style file handles to encode/decode Ceph inodes, snapped inodes, parents, and names. It bridges VFS export callbacks to Ceph MDS lookup operations and handles Ceph snapshot namespace special cases.

## File Handle Formats

Packed on-wire handle structs:

- `struct ceph_nfs_fh { u64 ino; }`: basic non-snapped inode handle.
- `struct ceph_nfs_confh { u64 ino, parent_ino; }`: non-snapped handle with parent.
- `struct ceph_nfs_snapfh { u64 ino, snapid, parent_ino; u32 hash; }`: snapped inode handle with parent and dentry hash context.

Lengths are expressed in `u32` units for exportfs callbacks.

## Encoding

- `ceph_encode_fh()` chooses normal or snapped encoding based on `ceph_snap(inode)`.
- Normal handles return `FILEID_INO32_GEN` or `FILEID_INO32_GEN_PARENT` even though Ceph stores 64-bit inode fields in the raw payload.
- `ceph_encode_snapfh()` returns `FILEID_BTRFS_WITH_PARENT` for snapped inodes. For non-snapdir snapped inodes, it tries to find a dentry alias, records the parent inode and `ceph_dentry_hash()`, and falls back only for directories where parent can be represented by self.
- If the caller-provided buffer is too small, the functions set the required length and return `FILEID_INVALID`.

## Decoding Inodes and Dentries

- `__lookup_inode()` looks for a head inode in the local cache with `ceph_find_inode()`, otherwise issues MDS `LOOKUPINO`. Reserved vinos are `-ESTALE`.
- `ceph_lookup_inode()` wraps `__lookup_inode()` and rejects unlinked inodes with `i_nlink == 0`.
- `__fh_to_dentry()` obtains an inode, refreshes link caps with `ceph_do_getattr(..., CEPH_CAP_LINK_SHARED)`, rejects unlinked closed files as stale, and returns `d_obtain_alias()`.
- `__snapfh_to_dentry()` decodes snapped and snapdir handles. It can return either target or parent, includes snapid/parent/hash in `LOOKUPINO`, maps head inode to snapdir where needed, and treats unlinked snapped directories with `d_obtain_root()` to avoid further disconnected-parent walks.

## Parent Resolution

- `__get_parent()` issues MDS `LOOKUPPARENT`, either from a child inode or raw ino, then returns `d_obtain_alias()` for the parent inode.
- `ceph_get_parent()` special-cases snapped dentries: non-directory snapped children are rejected, snapped directories resolve through the head inode's snapdir, and unlinked directories use `d_obtain_root()`.
- `ceph_fh_to_parent()` decodes either snapped handles with `__snapfh_to_dentry(..., true)` or connected normal handles. If `LOOKUPPARENT` returns `-ENOENT`, it falls back to the encoded parent ino.

## Name Resolution

- `ceph_get_name()` issues MDS `LOOKUPNAME` to recover a child's name under a parent for non-snapped inodes. It decodes encrypted names via `ceph_fname_to_usr()` using the primary and alternate names from the MDS reply.
- `__get_snap_name()` handles snapped namespace names:
  - snapdir under head inode returns the configured `snapdir_name`,
  - snapped children under a snapdir are found by paging through `LSSNAP` readdir replies until a matching snapid is found.

## Export Operations

`ceph_export_ops` wires:

- `.encode_fh = ceph_encode_fh`
- `.fh_to_dentry = ceph_fh_to_dentry`
- `.fh_to_parent = ceph_fh_to_parent`
- `.get_parent = ceph_get_parent`
- `.get_name = ceph_get_name`

## Dependencies and Semantics

This file depends on `dir.c` for `ceph_dentry_hash()` and snapdir semantics, MDS client request operations for `LOOKUPINO`, `LOOKUPPARENT`, `LOOKUPNAME`, and `LSSNAP`, and crypto helpers for encrypted filename presentation.

Stale detection is conservative: reserved vinos, shutdown inodes, missing MDS targets, unlinked closed files, unsupported snapped lookup, and malformed handle lengths all return stale/error/null results appropriate to exportfs.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/file.c -->
# File Research: sources/os/linux/linux/fs/ceph/file.c

## Role

`file.c` implements CephFS regular-file VFS behavior: open/atomic open/create, release, buffered/direct/synchronous/asynchronous I/O, fscrypt-aware reads and writes, cap acquisition around I/O, fallocate hole punching, copy offload, splice read, llseek, and the regular-file operations table.

## Main Interfaces

- `ceph_open()`, `ceph_atomic_open()`, and `ceph_release()` manage VFS file lifetime and MDS open/create requests.
- `ceph_read_iter()`, `ceph_write_iter()`, and `ceph_splice_read()` dispatch user I/O through page cache or OSD requests depending on caps, flags, encryption, and sync mode.
- `__ceph_sync_read()` is exported within the Ceph client for synchronous OSD reads.
- `ceph_fallocate()` supports keep-size hole punching.
- `ceph_copy_file_range()` uses OSD copy-from offload when safe, otherwise falls back to splice copy.
- `ceph_file_fops` wires the regular-file VFS operations.

## Open and File State

`ceph_flags_sys2wire()` maps Linux open flags to MDS wire flags. `prepare_open_request()` creates `OPEN` or `CREATE` requests, chooses auth MDS for write/create/truncate, sets fmode, flags, and create mode.

`ceph_init_file_info()` allocates either `ceph_dir_file_info` or `ceph_file_info`, sets sync mode for `NOPAGECACHE`, gets fmode refs, initializes per-file read/write context tracking, records the filesystem `filp_gen`, and un-inlines data for writable inline-data files. `ceph_init_file()` selects regular, directory, symlink, or special-file behavior.

`ceph_open()`:

- filters VFS-handled create/excl flags,
- prepares fscrypt regular-file access,
- does a client-side MDS auth check when a path alias is available,
- rejects writes to snapped files,
- trivially opens snapdirs,
- reuses existing caps when sufficient,
- otherwise sends an MDS open request and initializes file-private state from returned fmode.

`ceph_renew_caps()` reopens an inode after session loss when current caps cannot satisfy wanted fmode.

## Atomic Open and Async Create

`ceph_atomic_open()` combines lookup/create/open:

- waits on conflicting async unlink,
- strips `O_TRUNC` because VFS permission/truncate happens later,
- checks max-files quota for create,
- allocates a new inode and ACL/security context,
- prepares fscrypt lookup/create metadata,
- sends a parent-locked MDS open/create request,
- handles snapdir lookup and traceless create replies,
- finishes with `finish_no_open()` for splice/negative/symlink cases or `finish_open()` for opened regular files.

Async create is attempted when `ASYNC_DIROPS` is enabled and `try_prep_async_create()` can obtain:

- auth cap and delegated inode number,
- cached valid file layout,
- `CEPH_CAP_FILE_EXCL | CEPH_CAP_DIR_CREATE`,
- complete directory or matching dentry shared generation.

`ceph_finish_async_create()` locally fills a newly delegated inode with synthetic MDS inode data, initializes ACLs, marks `CEPH_I_ASYNC_CREATE`, splices it into the dentry, marks the file created, and opens it before the MDS reply completes. `ceph_async_create_cb()` later reconciles result errors, inode mismatch, mapping errors, shutdown, and cap flushing. `restore_deleg_ino()` returns unused delegated inode numbers on retryable MDS redirects.

## Release

`ceph_release()` frees per-file state, releases fmode refs, drops fscache cookie use for regular files, releases buffered readdir request/name/dir-info for directories, warns on nonempty read/write contexts, and wakes cap waiters.

## Synchronous Reads

`__ceph_sync_read()` bypasses page cache:

- rejects shutdown inodes,
- waits for dirty page cache in range,
- splits reads by OSD object/request limits,
- expands offsets/lengths for fscrypt block alignment,
- uses sparse reads for encrypted files or `SPARSEREAD`,
- allocates page vectors, submits OSD read, updates read/subvolume metrics,
- decrypts sparse extents for encrypted inodes,
- zero-fills short reads that are holes before EOF,
- copies pages to the destination iterator,
- updates `ki_pos` and returns `CHECK_EOF` retry state when needed.

`ceph_read_iter()` acquires read caps and chooses between direct/sync OSD read and `generic_file_read_iter()` depending on cache/lazy caps, `O_DIRECT`, file sync state, and inline data. It retries after fetching size or inline data when EOF/hole/inline handling requires fresh metadata.

## Direct and AIO I/O

`iter_get_bvecs_alloc()` pins iterator pages into a dynamically allocated `bio_vec` array. `put_bvecs()` releases pages and dirties user-backed read pages when needed.

`ceph_direct_read_write()` handles direct reads/writes using OSD requests and can queue asynchronous completion for non-sync kiocbs when the operation is within `i_size` or satisfied by one OSD request. It invalidates page cache on writes, records metrics, zero-fills read holes, updates size on writes, and returns `-EIOCBQUEUED` for queued AIO.

`ceph_aio_complete_req()` handles individual OSD completions, including `-EOLDSNAPC` write retry via workqueue, sparse read finalization, hole zeroing, metrics, bvec release, request release, and aggregate error propagation. `ceph_aio_complete()` completes the user kiocb when all OSD requests finish, updates size and dirty caps for writes, ends DIO, drops cap refs, frees cap flush state, and releases the aggregate request.

## Synchronous Writes and Encryption

`ceph_sync_write()` writes directly to OSDs from user iterators:

- rejects snapped files,
- waits for page cache in range and invalidates fscache,
- aligns encrypted writes to fscrypt block boundaries,
- performs read-modify-write for partial encrypted blocks,
- uses sparse reads and version assertions or exclusive create to avoid overwriting concurrent changes,
- encrypts pages before write,
- submits OSD write requests,
- updates metrics and subvolume metrics,
- retries RMW if object version changed,
- invalidates written page cache ranges,
- updates inode size and caps.

`ceph_write_iter()` is the high-level write path. It allocates a cap flush, starts direct or write I/O serialization, handles append size refresh, generic write checks, max file size, max-bytes quota, OSD/pool full checks, privilege removal, cap acquisition, timestamp/version updates, and then chooses:

- direct or sync OSD write when buffered/lazy caps are unavailable, `O_DIRECT`, sync mode, or prior write error;
- `generic_perform_write()` when buffered writing is allowed.

It handles `-EOLDSNAPC` by dropping locks/caps and retrying with a newer snap context, marks dirty write caps, flushes when quota is approaching, and forces dsync when OSD map/pool is near full.

## Splice Read and Seek

`ceph_splice_read()` mirrors read cap logic for splice. It falls back to `copy_splice_read()` for inline/sync/no-cache-cap cases and uses `filemap_splice_read()` when cache caps are held.

`ceph_llseek()` refreshes size before `SEEK_END`, `SEEK_DATA`, or `SEEK_HOLE`, then delegates to `generic_file_llseek()`.

## Hole Punching

`ceph_fallocate()` supports only `FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE` on unencrypted regular head inodes. It locks the inode, clamps punching beyond EOF, acquires write/buffer caps, updates file modification state, invalidates fscache and page cache, zeroes partial cached pages, sends OSD zero/delete/truncate operations across Ceph object layout boundaries via `ceph_zero_objects()`, and marks write caps dirty.

`ceph_zero_partial_object()` selects `ZERO`, `DELETE`, or `TRUNCATE` OSD ops, using the current snap context. `ceph_zero_objects()` respects stripe unit/count/object size to zero complete object sets efficiently.

## Copy Offload

`__ceph_copy_file_range()` tries OSD copy-from2 offload when:

- source/destination are in the same Ceph cluster,
- destination is not snapped,
- `NOCOPYFROM` is not set and copy-from2 has not been disabled,
- layouts are compatible non-striped single-object layouts,
- neither inode is encrypted,
- length is at least one object.

It flushes source and destination ranges, obtains source read and destination write caps with deadlock avoidance, validates source size/destination growth/quota, invalidates destination cache, manually copies initial/final partial objects with splice, and uses `ceph_do_objects_copy()` for full-object remote copies. If OSDs return `-EOPNOTSUPP`, it disables copy offload for the filesystem client. Public `ceph_copy_file_range()` falls back to `splice_copy_file_range()` on unsupported/cross-device cases.

## Metrics and Subvolume Accounting

Read, write, and copy-from paths update `ceph_client_metric` latency/size counters. `ceph_record_subvolume_io()` records nonzero read/write byte counts with start/end latency into the MDS subvolume metric collector; EOF reads are intentionally not counted as I/O.

## Concurrency and State

- Cap refs are acquired before reads/writes to prevent mid-I/O release to MDS.
- `ceph_start_io_read/write/direct()` and matching end calls serialize with truncation, direct I/O, and buffered I/O expectations.
- `i_ceph_lock` protects cap, snap, size, and dirty-cap state.
- Snap contexts are selected from pending cap snaps or `i_head_snapc`.
- Page cache invalidation is used whenever direct/sync writes or hole punching bypass cached data.
- Async create/unlink coordination with `dir.c` relies on dentry flags, delegated inode numbers, directory caps, and MDS callbacks.

## Error Handling

Key errors include `-ESTALE` for shutdown inodes on user I/O, `-EROFS` for writes to snapshots, `-EDQUOT` for quota, `-ENOSPC` for full OSD maps/pools, `-EFBIG` for max size, `-EOPNOTSUPP` for unsupported fallocate/copy-offload cases, and `-EIO` for shutdown or impossible encrypted sparse extent states. `-EBLOCKLISTED` during sync reads marks the filesystem client blocklisted. Write errors set Ceph inode write-error state until a later successful write clears it.

## Operation Table

`ceph_file_fops` exports open/release, llseek, read/write iterators, mmap prepare, fsync, POSIX/flock locking, splice read/write, ioctl/compat ioctl, fallocate, and copy_file_range.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/file.c -->