# Research Report: subset-b-005633

Work item: `subset-b-005633`

Scope:
- `sources/distributed-fs/ceph-client/fs/ceph/debugfs.c`
- `sources/distributed-fs/ceph-client/fs/ceph/dir.c`
- `sources/distributed-fs/ceph-client/fs/ceph/export.c`
- `sources/distributed-fs/ceph-client/fs/ceph/file.c`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/debugfs.c -->
# Research: sources/distributed-fs/ceph-client/fs/ceph/debugfs.c

## Purpose

`debugfs.c` exposes runtime CephFS client state through Linux debugfs when `CONFIG_DEBUG_FS` is enabled. It is an observability and tuning file, not part of the data path. It publishes MDS map details, outstanding MDS requests, cap ownership and waiters, MDS sessions, mount status, client metrics, session feature negotiation, and subvolume metric snapshots. It also exposes a writable `writeback_congestion_kb` debugfs attribute backed by the mount option.

When debugfs is disabled, the file compiles to empty `ceph_fs_debugfs_init()` and `ceph_fs_debugfs_cleanup()` stubs, preserving callers without adding runtime artifacts.

## Important APIs, Types, and Functions

- `struct ceph_session_feature_desc` and `ceph_session_feature_table[]` map CephFS session feature bit numbers to stable human-readable names. `metric_features_show()` uses this table to explain which negotiated MDS features are active.
- `mdsmap_show()` prints `ceph_mdsmap` epoch, root, max MDS count, session timeout/autoclose settings, and per-rank address/state.
- `mdsc_show()` walks `mdsc->request_tree` under `mdsc->mutex` and prints each in-flight `ceph_mds_request`, including tid, target session, op name, unsafe status, and inode/dentry/path context.
- `metrics_file_show()`, `metrics_latency_show()`, `metrics_size_show()`, and `metrics_caps_show()` expose counters from `struct ceph_client_metric`, including inode/open-file/cap counts, latency distributions, byte distributions, dentry lease hits/misses, and cap hits/misses.
- `caps_show()` reports global cap reservation status via `ceph_reservation_status()`, iterates per-session inode caps with `ceph_iterate_session_caps()`, and dumps `mdsc->cap_wait_list`.
- `mds_sessions_show()` prints auth global id, mount auth name, and each MDS session state.
- `status_show()` prints the client entity instance, client address/nonce, and blocklist state.
- `subvolume_metrics_show()` snapshots `mdsc->subvol_metrics_last` under `subvol_metrics_last_mutex`, then dumps pending metrics through `ceph_subvolume_metrics_dump()`.
- `metric_features_show()` evaluates whether client metric sending and subvolume metrics are enabled from module state, active metric session state, and negotiated feature bits.
- `congestion_kb_get()` and `congestion_kb_set()` back a debugfs simple attribute that reads/writes `fsc->mount_options->congestion_kb`.
- `ceph_fs_debugfs_init()` creates the debugfs files/directories and stores dentries in `struct ceph_fs_client`; `ceph_fs_debugfs_cleanup()` removes them.

## Control Flow

Initialization starts in `ceph_fs_debugfs_init()`. It creates `writeback_congestion_kb`, a `bdi` symlink, top-level files (`mdsmap`, `mds_sessions`, `mdsc`, `caps`, `status`), a `metrics` directory, and metric files under it (`file`, `latency`, `size`, `caps`, `metric_features`, `subvolumes`). Each read-only debugfs file is wired through `DEFINE_SHOW_ATTRIBUTE`, so opening the file invokes the matching `*_show()` seq_file callback with `fsc` in `s->private`.

Most show paths follow a snapshot pattern: take the narrow lock needed for the state being displayed, copy or read scalar values, drop the lock, and format the result into `seq_file`. `mdsc_show()` holds `mdsc->mutex` while walking the MDS request tree, but temporarily calls path-building helpers for dentries and uses dentry locks when printing names. `caps_show()` avoids holding `mdsc->mutex` while iterating one session's caps by taking a session reference, dropping the MDS client mutex, locking `session->s_mutex`, iterating caps, then reacquiring the MDS client mutex. `subvolume_metrics_show()` explicitly duplicates the last-sent metric array before formatting it so the output path does not hold the snapshot mutex during seq output.

Cleanup is direct and idempotent from the caller perspective: `ceph_fs_debugfs_cleanup()` removes individual files and recursively removes the `metrics` directory. The debugfs API tolerates missing dentries, so partial creation failures during init do not require complicated rollback here.

## State and Persistence Behavior

This file does not persist data to disk or to the Ceph cluster. It exposes volatile kernel-client state:

- MDS map and session state come from `fsc->mdsc`.
- Metrics come from counters, atomics, and spinlock-protected `struct ceph_metric` fields.
- Subvolume metrics come from `mdsc->subvol_metrics_last`, send counters, and pending aggregation state.
- Cap reporting reads live cap structures and cap waiter lists.
- `writeback_congestion_kb` mutates the in-memory mount option and affects writeback congestion behavior for the mounted client.

The output is best-effort diagnostic data. It can race with ongoing MDS transitions, cap changes, request completion, and metrics updates, but the show paths use the same mutexes/spinlocks expected by the owning subsystems to avoid torn list traversal and unsafe dereferences.

## Dependencies and Integration Points

- Linux debugfs and seq_file APIs provide file creation and read formatting.
- Ceph MDS client internals provide request trees, session lookup, cap iteration, cap waiter lists, MDS maps, and metric state.
- Ceph auth and mon client state supply `global_id`, auth mount name, and client entity identity.
- `metric.h` supplies metric counters, latency/size state, and `disable_send_metrics`.
- `subvolume_metrics.h` supplies pending and last-sent subvolume metric dumps.
- `super.h` supplies `struct ceph_fs_client`, mount options, debugfs dentries, and client accessors.

The exported integration surface is only `ceph_fs_debugfs_init()` and `ceph_fs_debugfs_cleanup()`, which are called from mount/client setup and teardown code. The rest of the functions are static show helpers bound to debugfs file operations.

## Risks and Edge Cases

- Debugfs output depends on live mutable state. A reader can see a consistent-enough snapshot but not a transactionally consistent view across MDS map, sessions, caps, and metrics.
- `mdsc_show()` path rendering may fail; it degrades to an empty path string rather than failing the debugfs read.
- `metric_features_show()` reports no active metrics if there is no active `mdsc->metric.session`; this can be a transient state during mount, reconnect, or teardown.
- `subvolume_metrics_show()` can fail to allocate the snapshot copy; it reports no last-sent entries but still prints aggregate send counters and pending metrics.
- The writable congestion attribute accepts any `u64` and casts it to `int`; validation is minimal because this is a debugfs control.
- Feature names must be kept in sync with feature bit definitions in `mds_client.h`; missing names do not break negotiation but reduce diagnosability.

## Test Signals

Useful validation signals include:

- With `CONFIG_DEBUG_FS=y`, mounting CephFS should create the expected files under the client's debugfs directory and remove them cleanly on unmount.
- Reading `mdsmap`, `mdsc`, `caps`, and `mds_sessions` during active metadata operations should not warn, deadlock, or dereference freed sessions/requests.
- `metrics/latency`, `metrics/size`, and `metrics/caps` should reflect read/write/metadata/copy activity after workloads.
- `metrics/metric_features` should change with negotiated session features and `disable_send_metrics`.
- `metrics/subvolumes` should show last-sent and pending subvolume metrics after subvolume I/O when the feature is negotiated.
- Writing and rereading `writeback_congestion_kb` should update `fsc->mount_options->congestion_kb`.
- A debugfs-disabled kernel should still link callers through the empty init/cleanup stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/dir.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/export.c -->
# Research: sources/distributed-fs/ceph-client/fs/ceph/export.c

## Purpose

`export.c` implements CephFS `export_operations` so CephFS can be exported through Linux exportfs/NFS. It encodes inodes into stable file handles, reconstructs dentries and parents from those handles, and resolves child names for exportfs. It handles ordinary head inodes, connected handles with parent inode numbers, snapshot inodes, snapdir dentries, disconnected aliases, encrypted directory names, and stale/unlinked inode cases.

## Important APIs, Types, and Functions

- `struct ceph_nfs_fh` is the basic handle containing only `ino`.
- `struct ceph_nfs_confh` contains `ino` and `parent_ino` for connected handles.
- `struct ceph_nfs_snapfh` contains `ino`, `snapid`, `parent_ino`, and name `hash` for snapped inodes.
- `ceph_encode_fh()` is the exportfs encode hook. It emits ordinary basic/connected handles or delegates snapped inodes to `ceph_encode_snapfh()`.
- `ceph_encode_snapfh()` encodes snapshot file handles, deriving parent inode and dentry hash from an alias when possible and falling back to self-parent for directory/snapdir handles.
- `__lookup_inode()` finds a head inode in the local inode cache or sends `CEPH_MDS_OP_LOOKUPINO`; it rejects reserved vinos and shutdown inodes.
- `ceph_lookup_inode()` wraps `__lookup_inode()` and returns `-ESTALE` for unlinked head inodes.
- `__fh_to_dentry()` reconstructs an ordinary dentry by inode number, refreshes LINK caps with `ceph_do_getattr()`, and rejects stale unlinked unopened files.
- `__snapfh_to_dentry()` reconstructs snapped or snapdir dentries from `ceph_nfs_snapfh`, optionally reconstructing the parent side of the handle.
- `ceph_fh_to_dentry()` dispatches ordinary and snapped file-handle decoding.
- `__get_parent()` sends `CEPH_MDS_OP_LOOKUPPARENT` for ordinary parent lookup.
- `ceph_get_parent()` is the exportfs parent hook and includes special handling for snapped directories and snapdir parents.
- `ceph_fh_to_parent()` decodes connected handles to parents, including snapshot handles.
- `__get_snap_name()` resolves names in snapdir contexts by returning the configured snapdir name or enumerating snapshots with `CEPH_MDS_OP_LSSNAP`.
- `ceph_get_name()` sends `CEPH_MDS_OP_LOOKUPNAME` for ordinary names and decrypts/decodes encrypted names when needed.
- `ceph_export_ops` registers encode/decode/parent/name hooks with exportfs.

## Control Flow

Encoding starts in `ceph_encode_fh()`. For ordinary inodes, it verifies the caller-provided raw handle has enough `u32` slots, stores the inode number, optionally stores the parent inode number, and returns `FILEID_INO32_GEN` or `FILEID_INO32_GEN_PARENT`. For snapped inodes, `ceph_encode_snapfh()` requires the larger snapshot handle and stores the snap id, parent inode, and directory hash. For non-snapdir snapped entries it tries to find an alias and parent outside the snapdir; if no parent can be derived, only directories can be encoded using self-parent semantics.

Decoding ordinary handles goes through `ceph_fh_to_dentry()` and `__fh_to_dentry()`. The latter performs inode lookup, forces a LINK-cap getattr to make `i_nlink` reliable, returns `-ESTALE` for unlinked unopened files, and returns `d_obtain_alias(inode)` so exportfs can work with connected or disconnected aliases.

Snapshot decoding goes through `__snapfh_to_dentry()`. It builds the target `ceph_vino` differently depending on whether exportfs wants the object or parent. If the inode is not cached, it sends LOOKUPINO with snap id, and for non-parent snapped child lookup it also supplies the saved parent inode and name hash. Snapdir replies are converted with `ceph_get_snapdir()`. If a snapped directory's head has been unlinked, it uses `d_obtain_root()` to avoid marking the snapdir dentry disconnected and causing exportfs to continue walking parents that cannot be resolved.

Parent reconstruction for ordinary entries uses `CEPH_MDS_OP_LOOKUPPARENT`; `ceph_fh_to_parent()` can fall back to the encoded `parent_ino` if LOOKUPPARENT returns `-ENOENT`. `ceph_get_parent()` has separate logic for snapped directories: non-directory snapped children are unsupported, non-snapdir snapped directories use the snapdir of the head inode as the simplified parent, and deleted heads again use `d_obtain_root()` to terminate exportfs traversal cleanly.

Name lookup uses `ceph_get_name()`. For head inodes, it sends `CEPH_MDS_OP_LOOKUPNAME` with child inode and parent vino, then copies the returned name. If the parent is encrypted, it converts the Ceph returned dname/alternate ciphertext through `ceph_fname_to_usr()`. Snapshot names use `__get_snap_name()`: the snapdir itself is named with the mount's snapdir name, while entries inside snapdir are found by repeated LSSNAP requests until the child snapid matches a returned snapshot entry.

## State and Persistence Behavior

File handles are packed binary snapshots of Ceph inode identity and, when needed, parent/snapshot context. They are not persisted by this file; NFS/exportfs consumers store and return them. The authoritative state remains in the Ceph MDS cluster.

The reconstruction paths use local inode cache when possible, but they refresh through MDS requests when cache misses or parent/name resolution require authoritative metadata. Stale handling depends on current inode/link state:

- Reserved vinos are immediately stale.
- Shutdown inodes are stale.
- Unlinked unopened ordinary files are stale after LINK-cap refresh.
- Deleted snapped directory heads use root-style dentries to prevent impossible parent walks.

## Dependencies and Integration Points

- Linux exportfs calls `ceph_export_ops`.
- MDS request operations used here are LOOKUPINO, LOOKUPPARENT, LOOKUPNAME, and LSSNAP.
- `super.h` supplies Ceph inode/vino helpers, snapshot constants, mount snapdir name, and inode cache helpers.
- `mds_client.h` supplies request creation/submission and reply parsing.
- `crypto.h` supplies encrypted name conversion through `ceph_fname_to_usr()`.
- `ceph_dentry_hash()` is implemented in `dir.c` and is required to encode snapshot handles that the MDS can later resolve.
- VFS helpers `d_obtain_alias()` and `d_obtain_root()` are central to disconnected exportfs reconstruction.

## Risks and Edge Cases

- Snapshot handles depend on parent inode and hash context for non-directory snapped entries. If the alias is unavailable at encode time, non-directory snapshot handle encoding fails.
- `FILEID_BTRFS_WITH_PARENT` is reused for snapshot handles because it fits the packed data shape; consumers must dispatch by fileid type exactly as this file does.
- Local inode cache hits may avoid an MDS round trip, but shutdown inode detection is required to avoid returning stale objects.
- Ordinary file handle decode must refresh LINK caps before trusting `i_nlink`; otherwise a concurrently unlinked file could be exported incorrectly.
- Encrypted parent names require alternate-name data from the MDS. Missing or inconsistent fscrypt context can make `get_name` fail.
- Snapshot name lookup may require paging through all snapshots with LSSNAP; large snapshot directories can make exportfs name resolution expensive.
- Parent fallback in `ceph_fh_to_parent()` handles older or racey MDS behavior but can return stale if both LOOKUPPARENT and encoded parent lookup fail.

## Test Signals

Useful tests include:

- Export ordinary CephFS files and directories over NFS, then reopen by file handle after dropping local dentries/inodes.
- Decode connected file handles after parent rename/unlink races and verify stale behavior.
- Export snapped directories and snapdir entries, including deleted head directories, and verify parent traversal terminates correctly.
- Resolve names for encrypted directories and no-encryption directories through exportfs `get_name`.
- Confirm unlinked unopened files return `-ESTALE` while still-open unlinked files can be represented as aliases when intended.
- Exercise `fh_to_parent` fallback by forcing LOOKUPPARENT misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/file.c -->
# Research: sources/distributed-fs/ceph-client/fs/ceph/file.c

## Purpose

`file.c` implements CephFS regular file operations and the file-open side of directory operations. It translates Linux VFS open/read/write/splice/llseek/fallocate/copy_file_range calls into Ceph MDS capability management and Ceph OSD object I/O. It chooses between page-cache buffered I/O, synchronous OSD I/O, direct I/O, async OSD requests, inline-data reads, encrypted read/write adjustment, async create, and remote object copy offload.

The file is central to CephFS consistency: it acquires and releases file capabilities, coordinates read/write/direct I/O locks, updates inode size and dirty caps, handles snapshot contexts, invalidates page cache/fscache around direct or remote changes, records client/subvolume metrics, and falls back to VFS helpers when Ceph-specific fast paths are not safe.

## Important APIs, Types, and Functions

- `ceph_record_subvolume_io()` records per-subvolume read/write operation metrics for successful non-zero I/O.
- `ceph_flags_sys2wire()` maps Linux open flags to Ceph wire flags.
- `iter_get_bvecs_alloc()`, `__iter_get_bvecs()`, and `put_bvecs()` pin iterator pages into `bio_vec` arrays for direct/asynchronous OSD I/O and release/dirty them afterward.
- `prepare_open_request()` allocates and initializes MDS OPEN/CREATE requests, including requested fmode and wire flags.
- `ceph_init_file_info()` and `ceph_init_file()` allocate per-open `ceph_file_info` or `ceph_dir_file_info`, acquire fmode refs, initialize read/write context tracking, handle no-page-cache sync mode, and uninline data before write opens.
- `ceph_renew_caps()` reacquires caps after session loss by sending an open request if local caps cannot satisfy wanted state.
- `ceph_open()` is the VFS open implementation. It handles fscrypt, access checks, snap read-only enforcement, fast open from existing caps, snapdir opens, and MDS OPEN fallback.
- Async create helpers `try_prep_async_create()`, `restore_deleg_ino()`, `wake_async_create_waiters()`, `ceph_async_create_cb()`, and `ceph_finish_async_create()` implement local create completion using delegated inode numbers, cached layouts, and directory create caps.
- `ceph_atomic_open()` combines lookup/create/open through MDS and optionally performs async create. It is registered from `dir.c`.
- `ceph_release()` frees per-file/per-directory private state, releases fmode refs, releases fscache cookies, and wakes cap waiters.
- `__ceph_sync_read()` and `ceph_sync_read()` perform blocking OSD reads, including sparse reads, encrypted extent decryption, EOF/hole zeroing, page-vector copyout, and retry signaling.
- `struct ceph_aio_request`, `struct ceph_aio_work`, `ceph_aio_complete_req()`, `ceph_aio_retry_work()`, and `ceph_aio_complete()` track asynchronous direct OSD requests and complete kiocbs.
- `ceph_direct_read_write()` handles direct read/write by building OSD requests from iterator-backed bvecs, with optional AIO and EOLDSNAPC retry.
- `ceph_sync_write()` performs blocking OSD writes, including fscrypt read-modify-write for partial crypto blocks and object-boundary splitting.
- `ceph_read_iter()`, `ceph_splice_read()`, and `ceph_write_iter()` are the main VFS read/write/splice entry points and perform cap acquisition, I/O mode selection, retries, and dirty-cap updates.
- `ceph_llseek()` refreshes size for SEEK_END/SEEK_DATA/SEEK_HOLE before delegating to generic llseek.
- `ceph_fallocate()`, `ceph_zero_pagecache_range()`, `ceph_zero_objects()`, and `ceph_zero_partial_object()` implement punch-hole support through page-cache invalidation/zeroing and OSD ZERO/TRUNCATE/DELETE operations.
- Copy offload helpers `get_rd_wr_caps()`, `is_file_size_ok()`, `ceph_alloc_copyfrom_request()`, `ceph_do_objects_copy()`, `__ceph_copy_file_range()`, and `ceph_copy_file_range()` implement object-aligned OSD copy-from2 and VFS fallback.
- `ceph_file_fops` registers regular file operations.

## Control Flow

### Open and Atomic Create

`ceph_open()` rejects duplicate opens, normalizes flags, runs fscrypt open checks for regular files, does a local MDS auth access check when it can build a path, rejects write opens on snapshots, and trivially initializes snapdir opens. If the inode already has usable caps, it touches fmode and initializes file private state without sending a synchronous open, possibly scheduling `ceph_check_caps()` to expand wanted caps. Otherwise it sends an MDS OPEN request and initializes private state from the returned fmode.

`ceph_atomic_open()` handles lookup/open/create from VFS. It strips `O_TRUNC` because VFS does truncation after permission checks, waits for conflicting async unlink, performs quota and fscrypt setup, allocates a new inode for create, builds an OPEN/CREATE request, and either:

- uses async create when `ASYNC_DIROPS`, directory create caps, cached layout, delegated inode number, and dentry lease/complete-dir conditions are satisfied; or
- sends a synchronous MDS request, finishes lookup/open/no-open depending on reply, caches the file layout after create, initializes ACLs, and calls `finish_open()`.

The async create path submits the MDS request but locally fills the new inode from synthesized MDS reply data, attaches it to the dentry, marks `FMODE_CREATED`, and opens the file. Completion later validates the MDS result, propagates errors, shuts down locally-created inodes on failure, releases directory caps, and wakes waiters.

### Read

`ceph_read_iter()` starts read/direct I/O exclusion, decides wanted cache/lazy caps, and calls `ceph_get_caps()` for `CEPH_CAP_FILE_RD`. If cache/lazy caps are unavailable, the file is direct, or the file is forced sync, it reads through OSD paths: direct unencrypted reads use `ceph_direct_read_write()`, otherwise `ceph_sync_read()`. Inline data triggers a getattr for inline data and copies from a temporary page. Buffered reads add a read/write context to the file and call `generic_file_read_iter()`.

`__ceph_sync_read()` flushes dirty page-cache data in range, splits reads by object mapping, adjusts encrypted reads to crypto block boundaries, uses sparse reads when needed, waits for OSD completion, updates metrics, decrypts encrypted extents, zero-fills short holes before EOF, copies pages to the iterator, updates `ki_pos`, and signals EOF/hole retry through `retry_op`.

`ceph_splice_read()` follows similar cap logic for pipe splicing. If page-cache caps are unavailable or inline/sync mode applies, it falls back to `copy_splice_read()`; otherwise it uses `filemap_splice_read()` under cap references and a read/write context.

### Write

`ceph_write_iter()` rejects shutdown and snapshot writes, preallocates a cap flush, starts direct or buffered write exclusion, handles append size refresh, runs generic write checks and size/quota/full-pool checks, removes file privileges, acquires `CEPH_CAP_FILE_WR` plus buffer/lazy caps where possible, updates file time and i_version, then chooses an I/O path.

If buffer/lazy caps are unavailable, direct I/O is requested, sync mode is set, or the inode is in write-error mode, it gets the current snap context and performs direct or synchronous OSD writes. Otherwise it uses `generic_perform_write()` into page cache. Successful writes mark FILE_WR caps dirty, may flush caps near quota limits, release cap refs, retry on `-EOLDSNAPC`, and call `generic_write_sync()` when required or near full.

`ceph_sync_write()` flushes overlapping page cache, invalidates fscache, loops by object boundary, adjusts encrypted writes to crypto block boundaries, performs read-modify-write for partial encrypted blocks with version assertion or exclusive create, encrypts pages, writes to OSD, retries RMW on version conflicts, invalidates local page cache range after successful OSD writes, and updates inode size/caps.

`ceph_direct_read_write()` builds bvec-backed OSD requests directly from the iterator. For writes it invalidates cache pages first and sets OSD write flags/mtime. It may queue multiple async OSD requests for non-sync kiocbs when the I/O is inside i_size or fits in one OSD request; completion updates size and dirty caps. Reads zero-fill holes and dirty user-backed pages when needed.

### Fallocate and Copy Offload

`ceph_fallocate()` supports only `FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE` on unencrypted regular head files. It acquires write caps, marks the file modified, locks page-cache invalidation, invalidates fscache, zeroes/truncates page-cache coverage, sends OSD ZERO/TRUNCATE/DELETE operations across affected objects, and marks FILE_WR caps dirty.

`ceph_copy_file_range()` first attempts `__ceph_copy_file_range()`. The offload path requires same cluster, writable head destination, copy-from enabled and supported, compatible non-striped layouts, unencrypted files, length at least one object, successful writeback of both ranges, source read caps and destination write caps, valid file sizes/quotas, matching object offsets, and page-cache invalidation on the destination. It manually splices initial/final partial-object ranges and uses OSD copy-from2 for full objects. Unsupported or cross-device cases fall back to `splice_copy_file_range()`.

## State and Persistence Behavior

This file coordinates multiple state layers:

- Per-open state in `ceph_file_info` / `ceph_dir_file_info`: fmode refs, sync flags, read/write contexts, generation, and directory readdir state.
- Per-inode cap state in `ceph_inode_info`: file modes, issued/wanted caps, dirty caps, snap contexts, layout, inline-data state, size, write-error state, async-create flags, and cached layout.
- Page cache and fscache state: flushed before sync reads/writes, invalidated before/after direct writes, punch-hole, and remote copy.
- Ceph cluster persistence: metadata/open/create state goes through MDS requests; file data, zeroing, and copy offload go through OSD requests.
- Metrics: latency/size counters and subvolume metrics are updated for OSD reads, writes, and copy-from operations.

Write persistence is split: data writes complete through OSD requests or page-cache writeback; metadata such as size/mtime is represented by dirty caps and later flushed to the MDS. Snap contexts are captured for writes so OSD writes land in the correct snapshot epoch, and `-EOLDSNAPC` causes retry after dropping caps and allowing pending capsnap state to settle.

## Dependencies and Integration Points

- VFS file operations call `ceph_file_fops`; directory operation tables in `dir.c` call `ceph_open()`, `ceph_release()`, and `ceph_atomic_open()`.
- MDS client integration covers OPEN, CREATE, cap renewal, access checks, async create callbacks, cap flush allocation, and cap dirtying.
- OSD client integration covers read/write/sparse-read/zero/delete/truncate/copy-from requests, request allocation, callbacks, object layout mapping, snap contexts, object versions, and OSD map full/nearfull flags.
- Netfs/fscache integration uses `ceph_fscache_use_cookie()`, `ceph_fscache_unuse_cookie()`, and `ceph_fscache_invalidate()`.
- Fscrypt integration adjusts offsets/lengths, decrypts sparse extents, encrypts write pages, and requires RMW for partial crypto blocks.
- Linux generic helpers provide buffered read/write, splice, direct I/O accounting, page-cache invalidation, write checks, file time updates, llseek, and copy fallback.
- Quota helpers reject max-file/max-byte violations before sending work likely to fail.
- `metric.h` and `subvolume_metrics.h` collect client and subvolume I/O statistics.

## Risks and Edge Cases

- Capability selection determines consistency. Taking the buffered path without cache/buffer caps would violate coherency, while unnecessary sync/direct fallback hurts performance.
- Async create relies on delegated inode numbers, cached layouts, and directory caps. Failures must shut down speculative inodes and wake waiters; `-EJUKEBOX` must restore delegated inode numbers and retry synchronously.
- Encrypted writes that do not align to crypto blocks require RMW with object version assertions. Races can force retry, and sparse extent validation failures return `-EIO`.
- Short OSD reads may represent holes rather than EOF; both sync and direct paths zero-fill holes and sometimes getattr/retry to distinguish EOF from stale size.
- Direct/AIO requests pin user pages; completion must dirty read pages when appropriate, put all pages, drop cap refs, call `inode_dio_end()`, and complete the kiocb exactly once.
- `ceph_write_iter()` returns `written ? written : err`, so partial success masks later errors in the standard Linux style.
- Hole punching is unsupported for encrypted files and only supports one fallocate mode.
- Remote copy offload is safe only for compatible object-aligned layouts and unencrypted files. It intentionally falls back to splice copy for unsupported conditions, stale source size, cross-cluster copies, disabled copy-from, or OSD lack of copy-from2.
- Full and nearfull OSD map/pool flags alter write behavior: full returns `-ENOSPC`; nearfull pushes writes toward synchronous durability.

## Test Signals

Important test coverage includes:

- Fast open from existing caps, synchronous MDS open, cap renewal after session reconnect, snapdir open, and write-open rejection on snapshots.
- Atomic open for existing files, negative dentries, symlink/no-open cases, synchronous create, async create success, async create `-EJUKEBOX`, and async create failure cleanup.
- Buffered reads/writes under cache/buffer caps and sync/direct fallback when caps are absent or mount options force sync.
- Direct read/write AIO completion, page pin release, dirtying of user-backed read pages, and `-EOLDSNAPC` retry.
- Sparse reads, holes before EOF, short reads at EOF, inline-data reads, and encrypted read decrypt/zero behavior.
- Encrypted partial-block writes with RMW, version assertion conflict retry, and object creation race retry.
- Quota exceeded, max file size, full/nearfull pool handling, append size refresh, dirty cap marking, and generic write sync.
- Punch-hole fallocate over partial and full object-set ranges, including page-cache/fscache invalidation.
- Copy_file_range offload for object-aligned compatible files and fallback for encrypted, striped, short, cross-cluster, unsupported, and partial-object cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/file.c -->
