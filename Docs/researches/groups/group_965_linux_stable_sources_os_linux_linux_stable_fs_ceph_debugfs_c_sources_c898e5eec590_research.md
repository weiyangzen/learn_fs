# Group Research: group_965_linux_stable_sources_os_linux_linux_stable_fs_ceph_debugfs_c_sources_c898e5eec590

Scope: `Docs/research_subset_a.md` only. This grouped report covers the listed CephFS Linux stable client files under `sources/os/linux/linux-stable/fs/ceph/`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/debugfs.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/debugfs.c

## Purpose

`debugfs.c` exposes CephFS client state through Linux debugfs when `CONFIG_DEBUG_FS` is enabled. It provides read-only diagnostic views for MDS maps, outstanding MDS requests, capability state, MDS sessions, client status, general metrics, negotiated feature bits, and subvolume metrics, plus a writable debugfs knob for writeback congestion.

## Main Responsibilities

- Creates and removes CephFS debugfs files under the Ceph client debugfs directory.
- Dumps current MDS map information.
- Dumps in-flight MDS client requests and their path/inode context.
- Dumps capability pool status, per-session caps, and cap waiters.
- Dumps MDS session identities and states.
- Dumps client instance and blocklist status.
- Dumps metric counters, latency distributions, size distributions, and cap/dentry cache hit/miss counters.
- Dumps subvolume metric snapshots and pending metric state.
- Shows negotiated MDS session feature bits relevant to metric collection.
- Exposes `writeback_congestion_kb` as a simple writable debugfs attribute.

## Debugfs Entries

Top-level files created by `ceph_fs_debugfs_init()`:
- `writeback_congestion_kb`: read/write mount option for writeback congestion threshold.
- `bdi`: symlink to the backing device info debugfs directory.
- `mdsmap`: MDS map epoch, root, max rank, timeouts, and rank addresses/states.
- `mds_sessions`: client identity and active MDS session states.
- `mdsc`: outstanding MDS requests.
- `caps`: capability pool and per-inode cap table.
- `status`: messenger entity instance and blocklist status.
- `metrics/`: metric subdirectory.

Metric files:
- `metrics/file`: total inodes, opened files, pinned caps, opened inodes.
- `metrics/latency`: read/write/metadata/copyfrom operation latency totals, averages, min/max, and stdev.
- `metrics/size`: read/write/copyfrom size totals, averages, min/max, and summed bytes.
- `metrics/caps`: dentry lease and inode cap hit/miss counters.
- `metrics/metric_features`: session feature-bit report and metrics enablement decision.
- `metrics/subvolumes`: last sent and pending subvolume I/O metrics.

## Locking and Data Access

- MDS request and session trees are walked under `mdsc->mutex`.
- Per-session capability iteration takes `session->s_mutex`.
- Individual inode cap state is read under `ci->i_ceph_lock`.
- Cap waiters are read under `mdsc->caps_list_lock`.
- Metric latency and size structures use per-metric spinlocks.
- Subvolume metric snapshots are copied under `subvol_metrics_last_mutex` before formatting, avoiding long seq_file output while holding the mutex.

## Notable Formatting Helpers

- `CEPH_LAT_METRIC_SHOW` converts ktime values to microseconds and derives a standard deviation-like display value from the stored squared latency sum.
- `CEPH_SZ_METRIC_SHOW` normalizes an unset `U64_MAX` minimum to zero for display.
- `ceph_session_feature_table` maps CephFS feature bits to stable debugfs names for `metric_features_show()`.

## Disabled Build Behavior

When `CONFIG_DEBUG_FS` is not enabled:
- `ceph_fs_debugfs_init()` is an empty function.
- `ceph_fs_debugfs_cleanup()` is an empty function.
- None of the seq_file/debugfs helpers are compiled.

## Important Dependencies

- `mds_client.h`: request trees, sessions, caps, feature bits, request path helpers.
- `metric.h`: client metric counters and latency/size state.
- `subvolume_metrics.h`: pending and last-sent subvolume metrics.
- Ceph common debugfs support from `linux/ceph/debugfs.h`.
- Linux `seq_file`, debugfs, atomics, percpu counters, and ktime helpers.

## Edge Cases and Risks

- `mdsc_show()` builds paths for dentries while holding request iteration state; it carefully releases path metadata with `ceph_mdsc_free_path_info()`.
- `metric_features_show()` reports disabled metrics if there is no current metric session or if the MDS session lacks `METRIC_COLLECT`.
- Subvolume metric snapshot allocation can fail; the output then reports no last-sent entries but still prints aggregate send counters and pending metrics.
- Cleanup uses individual `debugfs_remove()` calls plus `debugfs_remove_recursive()` for the metrics directory; debugfs tolerates missing entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/debugfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/dir.c

## Purpose

`dir.c` implements CephFS directory and dentry VFS behavior: readdir, lookup, create-like operations, link/unlink/rename, snapdir handling, dentry lease validation, dcache readdir acceleration, async unlink, and directory operation tables.

## Main Responsibilities

- Implements `ceph_dir_fops`, `ceph_snapdir_fops`, `ceph_dir_iops`, `ceph_snapdir_iops`, and `ceph_dentry_ops`.
- Maintains Ceph-specific dentry state through `ceph_d_init()` and `ceph_d_release()`.
- Encodes and compares readdir positions for fragmented directories and hash-ordered replies.
- Serves readdir from dcache when a directory is complete and protected by shared file caps.
- Falls back to MDS `READDIR`/`LSSNAP` requests when cached directory state is incomplete or invalid.
- Handles lookup, snapdir aliasing, and negative dentry completion.
- Implements metadata mutations: mknod/create, symlink, mkdir/snapshot creation, hard link, unlink/rmdir/snapshot removal, and rename/snapshot rename.
- Manages dentry and directory-wide leases, including renewal, trimming, invalidation, revalidation, and pruning.
- Provides optional `-o dirstat` directory read output.
- Computes directory-entry hashes according to Ceph directory layout.

## Readdir Model

Readdir positions pack directory fragment/hash state into `loff_t`:
- `ceph_make_fpos()` combines a high value and per-fragment offset.
- `HASH_ORDER` marks hash-ordered positions.
- `fpos_frag()`, `fpos_hash()`, and `fpos_off()` decode positions.
- `fpos_cmp()` orders positions using `ceph_frag_compare()` and the low offset.

`ceph_readdir()` always emits `.` and `..` first, then:
- Prepares fscrypt readdir state, clearing complete directory state if unlocking changes visible names.
- Tries `__dcache_readdir()` when mount options and caps prove the directory cache is complete and ordered.
- Sends MDS `READDIR` or `LSSNAP` requests by fragment when cache use is not possible.
- Tracks the last emitted name and next offset so readdir can resume robustly across directory changes.
- Updates `dfi->last_readdir`, `frag`, `next_offset`, `readdir_cache_idx`, release counts, and ordered counts.
- Marks a directory complete/ordered when the full traversal completes without dentry releases or ordering changes.

## Dcache Readdir

`__dcache_readdir()` reads cached dentry pointers from the directory inode mapping:
- Uses `__dcache_find_get_entry()` to locate cached dentries by index.
- Binary-searches to the requested position when possible.
- Rejects unhashed, negative, stale-generation, or now-decryptable nokey dentries.
- Touches directory leases before emitting entries.
- Falls back with `-EAGAIN` if cached content is missing or inconsistent.

The directory inode `i_size` is used as the number of cached dentry pointer entries when the directory is complete and ordered.

## Lookup and Snapdir Handling

`ceph_lookup()`:
- Rejects overlong names.
- Prepares encrypted partial lookup when needed.
- Can answer local `-ENOENT` from a complete cached directory, excluding snapdir and root `.ceph*` special cases.
- Otherwise sends `LOOKUP` or `LOOKUPSNAP` to an MDS.
- Requests inode/auth/xattr caps needed for VFS/security behavior.

`ceph_handle_snapdir()` splices the synthetic `.snap` directory when an MDS returns `-ENOENT` for the configured snapdir name under a head directory.

`ceph_finish_lookup()` handles traceless `-ENOENT`, spliced dentries, and VFS return conventions.

## Create, Link, Unlink, and Rename

Mutation operations are translated into MDS requests:
- `ceph_mknod()` and `ceph_create()` send `MKNOD`; regular files under encrypted directories set the fscrypt file request bit.
- `ceph_symlink()` encrypts symlink targets when the new symlink inode is encrypted, then sends `SYMLINK`.
- `ceph_mkdir()` sends `MKDIR` or `MKSNAP` for `.snap/name`.
- `ceph_link()` sends `LINK` and may instantiate the new dentry locally if the reply has no trace.
- `ceph_unlink()` sends `UNLINK`, `RMDIR`, or `RMSNAP`.
- `ceph_rename()` sends `RENAME` or `RENAMESNAP`, disallowing unsupported flags, cross-snapshot renames, and cross-quota renames.

Common behavior:
- Snapshot trees are read-only except snapdir snapshot creation/removal/rename operations.
- Quota checks reject max-files violations before create/mkdir/symlink.
- `ceph_wait_on_conflict_unlink()` serializes against conflicting async unlink.
- fscrypt helpers validate link/rename compatibility.
- Dentry cap drops and “unless” masks tell the MDS what cached state can be revoked.
- `ceph_handle_notrace_create()` follows old-MDS traceless create replies with a lookup.

## Async Unlink

When `ASYNC_DIROPS` is enabled, `ceph_unlink()` can submit async unlink for regular unlink:
- `get_caps_for_async_unlink()` requires directory `FILE_EXCL | DIR_UNLINK` caps, matching shared generation, and primary linkage.
- The dentry is marked `CEPH_DENTRY_ASYNC_UNLINK` and inserted into `async_unlink_conflict`.
- On successful submission, local link count and dcache state are updated optimistically.
- `ceph_async_unlink_cb()` removes conflict tracking, wakes waiters, handles `-EJUKEBOX` retry fallback, and marks parent/target mappings on real failure.

## Dentry Lease System

Two lease concepts are maintained:
- Per-dentry MDS leases, tracked by `lease_gen`, `lease_session`, `lease_seq`, expiry time, and renewal time.
- Directory-wide leases backed by `CEPH_CAP_FILE_SHARED` and `lease_shared_gen`.

Important helpers:
- `__ceph_dentry_lease_touch()` keeps valid dentry leases in LRU-like order.
- `__ceph_dentry_dir_lease_touch()` tracks directory-wide lease use.
- `dentry_lease_is_valid()` validates and optionally renews MDS leases.
- `dir_lease_is_valid()` validates directory-wide leases and touches file mode wanted state.
- `ceph_trim_dentries()` scans lease lists to drop stale dentries under cap pressure.
- `ceph_invalidate_dentry_lease()` invalidates a dentry lease and clears primary-link state.

## Dentry Revalidation and Pruning

`ceph_d_revalidate()`:
- Delegates fscrypt name revalidation first.
- Trusts snapped dentries and snapdir dentries.
- Uses valid per-dentry or directory-wide leases when available.
- Falls back to MDS lookup outside RCU-walk mode.
- Updates lease hit/miss metrics.
- Clears directory complete state when validation fails.

`ceph_d_delete()` permits VFS deletion of unused positive head dentries lacking valid lease coverage.

`ceph_d_prune()` clears complete or ordered directory cache state when the VFS prunes relevant dentries.

## Directory Stat Read

`ceph_read_dir()` implements the nonstandard `read()` on directories only when mounted with `DIRSTAT`. It formats local recursive and direct directory counts/bytes/ctime into a small text buffer.

## Important Dependencies

- `mds_client.h`: MDS request creation, request execution, request flags, path building, release counts, and session state.
- `crypto.h`: encrypted dentries, lookup/readdir preparation, encrypted symlink targets, encrypted request names.
- `super.h`: Ceph inode/dentry structures, caps, quotas, mount options, snapdir helpers.
- `ceph_frag.c`: fragment comparison used in readdir position ordering.
- `file.c`: `ceph_open()`, `ceph_release()`, `ceph_atomic_open()`, `ceph_fsync()`, locking/ioctl hooks.
- Linux VFS dentry, inode, namei, fscrypt, and directory iteration APIs.

## Edge Cases and Risks

- Readdir correctness depends on preserving `last_name`, fragment, hash-order, and offset semantics across MDS replies and seeks.
- Dcache readdir is only valid while directory shared-cap generation and ordered cache state remain intact.
- Unlocking an encrypted directory invalidates complete directory state because previously raw nokey names may become decryptable.
- Async unlink deliberately mutates local dcache/link state before server completion and must mark mapping errors if the server later fails the operation.
- Dentry lease trimming uses trylocks and RCU/list handoff to avoid blocking heavily while still dropping stale dentries.
- `ceph_d_prune()` defensively disables ordered dcache readdir if dentries disappear without an MDS revocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/export.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/export.c

## Purpose

`export.c` implements CephFS `export_operations` for NFS/exportfs support. It encodes Ceph inodes into file handles and resolves file handles, parents, and names back through cached inodes or MDS lookup operations, including special handling for snapped inodes and the synthetic snapdir.

## File Handle Formats

The file defines packed handle structures:
- `ceph_nfs_fh`: basic handle containing inode number.
- `ceph_nfs_confh`: connected handle containing inode and parent inode numbers.
- `ceph_nfs_snapfh`: snapped inode handle containing inode number, snapid, parent inode number, and dentry hash.

Handle sizes are expressed in `u32` units for exportfs.

## Encoding

`ceph_encode_fh()`:
- Delegates non-head inodes to `ceph_encode_snapfh()`.
- Encodes head inodes as `FILEID_INO32_GEN` with just inode number.
- Encodes connected head handles as `FILEID_INO32_GEN_PARENT` with inode and parent inode numbers.
- Returns `FILEID_INVALID` with the required size when the caller-provided buffer is too small.

`ceph_encode_snapfh()`:
- Encodes snapped inode identity and enough parent/hash data to help the MDS resolve non-directory snapped inodes.
- For snapped non-snapdir inodes, finds an alias dentry and records parent inode/hash unless parent is snapdir.
- For snapdir or no-parent cases, only directories are accepted; parent ino is set to the inode itself and hash to zero.
- Uses `FILEID_BTRFS_WITH_PARENT` as the fileid type for this Ceph-specific snapped format.

## Inode and Dentry Resolution

`__lookup_inode()`:
- Rejects reserved Ceph vino values as stale.
- Checks the local inode cache first.
- Falls back to MDS `LOOKUPINO` with inode/xattr mask.
- Rejects shutdown cached inodes.

`ceph_lookup_inode()` wraps `__lookup_inode()` and rejects unlinked inodes with `i_nlink == 0`.

`__fh_to_dentry()`:
- Looks up a head inode.
- Fetches `LINK_SHARED` caps through `ceph_do_getattr()` so link count is reliable.
- Returns `-ESTALE` if the inode has no links and is not currently opened.
- Returns `d_obtain_alias(inode)` for exportfs.

`__snapfh_to_dentry()`:
- Reconstructs a `ceph_vino` for either the snapped child or its parent.
- Checks local inode cache first.
- Falls back to MDS `LOOKUPINO`, passing snapid and parent/hash hints for snapped non-directory children.
- Converts returned head inode to a snapdir inode when resolving `CEPH_SNAPDIR`.
- Returns `-EOPNOTSUPP` if the MDS cannot resolve the requested snapped inode form.

## Parent Resolution

`__get_parent()` sends `LOOKUPPARENT`, either for a child dentry/inode or for an inode number from a connected handle.

`ceph_get_parent()` handles snapped dentries specially:
- Non-directory snapped children are rejected.
- For snapped directories, the head inode or snapdir of the head inode is used as parent.
- If the head directory has been unlinked, `d_obtain_root()` is used to avoid exportfs repeatedly walking disconnected parents.
- Head inodes use `LOOKUPPARENT`.

`ceph_fh_to_parent()`:
- Resolves snapped handles through `__snapfh_to_dentry(..., want_parent=true)`.
- Resolves connected head handles through `__get_parent()`.
- Falls back to parent inode from the handle if `LOOKUPPARENT` returns `-ENOENT`.

## Name Resolution

`ceph_get_name()` implements exportfs `.get_name()`:
- Snapped inodes delegate to `__get_snap_name()`.
- Head inodes use MDS `LOOKUPNAME` with parent locked.
- Plain directories copy the MDS-provided dentry name.
- Encrypted directories convert MDS name/alternate-name data back to a user-facing name through `ceph_fname_to_usr()`.

`__get_snap_name()`:
- Returns the configured snapdir name when child is the snapdir under its head directory.
- For snapshots under snapdir, iterates `LSSNAP` replies until the child snapid is found.
- Tracks `last_name` and `next_offset` to continue multi-request snapshot directory scans.

## Export Operations

`ceph_export_ops` wires:
- `.encode_fh = ceph_encode_fh`
- `.fh_to_dentry = ceph_fh_to_dentry`
- `.fh_to_parent = ceph_fh_to_parent`
- `.get_parent = ceph_get_parent`
- `.get_name = ceph_get_name`

## Important Dependencies

- `linux/exportfs.h`: file handle and export operation API.
- `mds_client.h`: `LOOKUPINO`, `LOOKUPPARENT`, `LOOKUPNAME`, `LSSNAP`, request execution, and readdir reply buffers.
- `crypto.h`: encrypted name decoding for exportfs name recovery.
- `dir.c`: `ceph_dentry_hash()` used when encoding snapped handles.
- `super.h`: Ceph inode/vino/snap helpers and snapdir helpers.

## Edge Cases and Risks

- File handles for snapped non-directory inodes require parent/hash hints because an inode number and snapid alone may not be enough for all MDS lookup paths.
- Exported head inodes with zero link count can still be valid if open; `__fh_to_dentry()` checks `__ceph_is_file_opened()`.
- Snapdir parent recovery intentionally uses `d_obtain_root()` for unlinked directories to prevent exportfs from walking further up a disconnected path.
- Encrypted `.get_name()` depends on the MDS alternate-name field when available and can fail if fscrypt conversion fails.
- `__get_snap_name()` may need multiple `LSSNAP` requests and must keep the last seen snapshot name for continuation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/file.c

## Purpose

`file.c` implements CephFS regular-file open, close, read, write, direct I/O, async direct I/O completion, atomic open/create, fallocate hole punching, llseek, splice read, and copy_file_range offload. It is the main bridge between Linux file operations, Ceph capabilities, page cache policy, fscrypt constraints, FS-Cache invalidation, MDS metadata operations, and OSD object I/O.

## Main Responsibilities

- Defines `ceph_file_fops`.
- Converts Linux open flags to Ceph MDS wire flags.
- Initializes and releases per-file and per-directory private state.
- Opens files locally when existing caps are sufficient or through MDS `OPEN`/`CREATE` requests otherwise.
- Supports async create using delegated inode numbers and directory create caps.
- Implements atomic open with lookup/create/open in one MDS request.
- Implements synchronous OSD reads and writes.
- Implements direct read/write with bvec-backed OSD requests and optional AIO completion.
- Routes buffered reads/writes through generic VFS helpers when cache/buffer caps permit.
- Handles inline-data reads by forcing getattr of inline data.
- Records global and subvolume I/O metrics.
- Performs hole punching with object zero/delete/truncate operations.
- Offloads eligible `copy_file_range()` calls to OSD copy-from operations.
- Integrates cap dirtying, cap flush preallocation, quota checks, and writeback sync behavior.

## Open and File State

`prepare_open_request()` creates MDS `OPEN` or `CREATE` requests and chooses auth MDS when flags imply writing, creation, or truncation.

`ceph_init_file_info()`:
- Allocates `ceph_file_info` or `ceph_dir_file_info`.
- Initializes fmode refs with `ceph_get_fmode()`.
- Sets synchronous I/O mode for `NOPAGECACHE`.
- Initializes per-file rw context tracking.
- Uninlines data before opening inline regular files for write.

`ceph_open()`:
- Validates fscrypt opens for regular files.
- Rejects write opens on snapshots.
- Opens snapdir locally.
- Uses existing caps locally when possible, touching wanted file mode and optionally checking caps asynchronously.
- Otherwise sends an MDS open request and initializes file state from the returned fmode.
- Performs an MDS-side access check when a path alias is available, returning local `-EACCES` only for definite denial.

`ceph_release()` drops fmode refs, FS-Cache cookie use, pending readdir request references, dirstat buffers, and private file caches, then wakes cap waiters.

## Atomic Open and Async Create

`ceph_atomic_open()` combines lookup/create/open behavior:
- Strips `O_TRUNC`; VFS handles truncation after permission checks.
- Waits for conflicting async unlink.
- Performs local MDS access check when possible.
- Allocates a new inode and ACL/security context for create.
- Prepares encrypted lookup/create state when the parent is encrypted.
- Sends MDS `OPEN`/`CREATE`, handles snapdir lookup, traceless create replies, spliced dentries, symlinks, and no-open retry paths.

Async create is attempted when `ASYNC_DIROPS` is enabled and prerequisites hold:
- Parent has auth cap and `FILE_EXCL | DIR_CREATE`.
- Parent has a valid cached file layout.
- Session has delegated inode numbers.
- Dentry has a valid lease or parent directory is complete.
- Security xattrs fit in a single pagelist page.

`ceph_finish_async_create()` fabricates enough inode reply state to instantiate the delegated inode locally, fills the inode, splices it into the dentry, marks `CEPH_I_ASYNC_CREATE`, and finishes open while the MDS request completes asynchronously.

`ceph_async_create_cb()` handles server completion, waking waiters, marking mapping errors, shutting down locally created inodes on failure, and detecting delegated inode mismatches.

## Read Paths

`ceph_read_iter()`:
- Starts read or direct-I/O exclusion.
- Acquires read caps and desired cache/lazy caps.
- Uses direct/sync OSD reads when cache caps are absent, `O_DIRECT` is set, sync mode is forced, or inline data must be fetched.
- Uses `generic_file_read_iter()` with a recorded rw context when cache/lazy caps allow page-cache reads.
- Handles EOF/hole retry by refreshing size.
- Handles inline-data retry by fetching `CEPH_STAT_CAP_INLINE_DATA` and copying inline bytes plus zero-fill.

`__ceph_sync_read()`:
- Flushes dirty page-cache pages in the requested range.
- Splits reads along object and mount boundaries through `ceph_osdc_new_request()`.
- Uses sparse reads for encrypted files or `SPARSEREAD`.
- Adjusts encrypted reads to crypto-block boundaries.
- Treats OSD `-ENOENT` as holes.
- Decrypts sparse encrypted extents.
- Zero-fills short reads before EOF.
- Copies pages into the destination iterator and updates file position.

`ceph_splice_read()` uses `filemap_splice_read()` only when cache/lazy caps allow it; otherwise it falls back to `copy_splice_read()`.

## Write Paths

`ceph_write_iter()`:
- Rejects shutdown and snapshot writes.
- Allocates a cap flush record before taking locks/caps.
- Starts write or direct-I/O exclusion.
- Handles append by refreshing size.
- Runs generic write checks, max file size checks, quota checks, OSD full/nearfull checks, and privilege stripping.
- Acquires write caps plus buffer/lazy caps when useful.
- Updates file time and i_version.
- Chooses sync/direct OSD writes when buffer/lazy caps are absent, direct I/O is requested, sync mode is forced, or previous writes have errored.
- Uses `generic_perform_write()` for buffered writes when file buffer caps permit.
- Marks `FILE_WR` caps dirty after successful writes.
- Retries `-EOLDSNAPC` after dropping cap refs so pending snapshot state can complete.
- Forces dsync behavior when the OSD map or pool is near-full.

`ceph_sync_write()`:
- Flushes page-cache pages in range and invalidates FS-Cache.
- Splits writes by object mapping.
- Adjusts encrypted writes to fscrypt block boundaries.
- Performs read/modify/write for encrypted partial crypto blocks.
- Uses assert-version or exclusive create to protect RMW from concurrent object changes.
- Encrypts page vectors before OSD write.
- Invalidates written page-cache range after successful OSD writes.
- Updates inode size and cap state when extending.

## Direct and Async I/O

`ceph_direct_read_write()`:
- Pins iterator pages into bvec arrays.
- Builds OSD read/write requests with `CEPH_OSD_DATA_TYPE_BVECS`.
- Invalidates page cache and FS-Cache for direct writes.
- Uses sparse read support when requested.
- Allows AIO only when the I/O is within current size or can be satisfied by one OSD request.
- For synchronous direct reads, zero-fills short reads before EOF.
- Returns `-EIOCBQUEUED` after starting queued async OSD requests.

`ceph_aio_complete_req()`:
- Handles per-OSD request completion.
- Retries writes on `-EOLDSNAPC` through workqueue redrive.
- Converts sparse read results, `-ENOENT`, and short reads into user-visible bytes/zero-fill.
- Updates read/write/subvolume metrics.
- Releases pinned bvec pages and completes the aggregate AIO request.

`ceph_aio_complete()`:
- Ends DIO, updates file size for writes, marks write caps dirty, drops cap refs, completes the kiocb, and frees request state when all OSD requests finish.

## Hole Punching and Zeroing

`ceph_fallocate()` supports only `FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE`:
- Regular files only.
- Snapshots and encrypted files are rejected.
- Acquires write/buffer caps.
- Invalidates FS-Cache and page cache.
- Zeroes partial page-cache pages and truncates whole cached pages.
- Calls `ceph_zero_objects()` to zero/delete/truncate OSD objects.
- Marks file write caps dirty on success.

`ceph_zero_objects()` maps ranges to object-set boundaries:
- Uses `CEPH_OSD_OP_ZERO` for partial object ranges.
- Uses delete/truncate operations for full object-set coverage.
- Preserves snapshot context by taking the current head or pending capsnap snap context.

## Copy File Range

`ceph_copy_file_range()` first tries `__ceph_copy_file_range()` and falls back to `splice_copy_file_range()` for unsupported or cross-cluster cases.

The OSD copy offload path requires:
- Same Ceph cluster FSID.
- Destination is not a snapshot.
- `NOCOPYFROM` is not set.
- OSDs support copy-from2.
- Non-striped compatible layouts: same stripe unit, stripe count 1, same object size.
- Neither file is encrypted.
- Length is at least one object.
- Source and destination object offsets match.
- Source read caps and destination write/buffer caps are held.
- Source and destination dirty data are written back first.

It handles unaligned leading/trailing partial object regions with `splice_file_range()` and full objects with OSD copy-from requests. Destination page cache and FS-Cache are invalidated, destination size and dirty caps are updated, and OSD `-EOPNOTSUPP` disables future copy-from2 attempts for the mount.

## Metrics and Subvolume Accounting

- Read, write, and copy-from OSD request latencies/sizes update `ceph_client_metric`.
- `ceph_record_subvolume_io()` records nonzero read/write byte counts into subvolume metrics.
- EOF reads are intentionally not counted as subvolume I/O.
- Write metrics count submitted write lengths on successful OSD writes.

## Important Dependencies

- `caps.c`: cap acquisition/release, wanted fmode state, dirty cap marking, cap flush records, snapshot context selection.
- `addr.c`: buffered writeback, inline-data uninlining, mmap preparation, page-cache behavior.
- `cache.c`/`cache.h`: FS-Cache use/unuse and invalidation.
- `crypto.c`/`crypto.h`: encrypted open checks, read/write alignment, encrypted RMW, page encryption/decryption.
- `dir.c`: atomic-open snapdir/notrace helpers and dentry async state.
- OSD client APIs: request allocation, extent setup, sparse reads, copy-from, request wait/callback.
- Linux VFS: generic read/write, direct I/O exclusion, splice, fallocate, llseek, fscrypt, quota/newsize checks.

## Edge Cases and Risks

- Async create depends on delegated inode numbers and local fabricated inode state matching the later MDS reply.
- Direct AIO keeps cap refs until all OSD requests complete; completion paths must release bvec pages and cap refs exactly once.
- Encrypted partial-block sync writes use RMW with object version assertions; version changes force retry.
- Sync/direct reads must distinguish short object reads, holes, EOF, encrypted sparse extents, and copy-to-user faults.
- `-EOLDSNAPC` write retries deliberately drop caps and reacquire snapshot context to preserve snapshot ordering.
- OSD copy offload is conservative; many valid VFS copy cases intentionally fall back to splice to avoid stale size/layout/cap hazards.
- Hole punching encrypted files is disabled because object zeroing would not preserve fscrypt block semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/file.c -->