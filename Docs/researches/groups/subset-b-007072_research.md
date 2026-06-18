# subset-b-007072 GlusterFS AFR directory, inode, lock, open, and read transaction research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.c

## Purpose
Implements AFR directory open, read, read-plus, and release operations. It keeps directory fds open on all currently usable replica children, selects one readable replica for `readdir`/`readdirp`, and hides AFR-private implementation entries from root listings.

## Important APIs, types, and functions
`afr_opendir()` initializes `afr_local_t`, checks quorum/consistent I/O, gets `afr_fd_ctx_t`, and fans out `opendir` to every up child. `afr_opendir_cbk()` records per-child replies and `fd_ctx->opened_on[]`. `afr_do_readdir()` is shared by `afr_readdir()` and `afr_readdirp()`. `afr_readdir_wind()` stores `fd_ctx->readdir_subvol` and winds the selected child FOP. `afr_readdir_transform_entries()` moves entries into the caller list, skips private dirs, and invalidates entry inodes whose cached readable subvol is not compatible with the parent read child.

## Control flow
First directory read, or any read without a pinned child, enters `afr_read_txn()` with an `AFR_DATA_TRANSACTION`. A failed offset-zero read can call `afr_read_txn_continue()` and fail over. Later reads with nonzero offset bypass read selection and reuse `fd_ctx->readdir_subvol`, preserving directory offset semantics.

## State and persistence behavior
State is transient except for fd context: `opened_on[]` tracks which children have an open fd and `readdir_subvol` pins offset continuation. No on-disk data is changed. Entry inode references from `readdirp` are dropped when validation shows they could represent stale metadata.

## Dependencies and integration points
Depends on `afr-transaction.h`, AFR read-subvolume helpers, inode refresh/readable caches, Gluster list and dict APIs, child xlator directory FOPs, and `afr_cleanup_fd_ctx()` on release.

## Risks and test signals
Risks include incorrect offset failover, stale `readdirp` inodes when healing or consistent metadata is enabled, fd context allocation failures, private directory leakage from root, and quorum edge cases. Tests should cover first-read failover, continued reads staying pinned, private directory filtering, readdirp inode invalidation after generation changes, and all-children-down/quorum failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.h

## Purpose
Declares the AFR directory read-side FOP entry points exported to the AFR translator operation table.

## Important APIs, types, and functions
Exports `afr_opendir()`, `afr_releasedir()`, `afr_readdir()`, and `afr_readdirp()` with Gluster call-frame, xlator, fd, loc, size, offset, and xdata signatures. The header is a narrow contract; implementation details such as `afr_do_readdir()` and callbacks remain private to the `.c` file.

## Control flow
Translator initialization wires these prototypes into the fops table. Runtime calls enter the `.c` implementation, which creates frame-local AFR state and either broadcasts opens or routes reads through read-transaction selection.

## State and persistence behavior
The header declares no state. The implied state is fd context lifecycle: open/read operations maintain AFR fd context and `releasedir` releases it.

## Dependencies and integration points
Requires the broader AFR/Gluster type environment for `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, and `dict_t`. It is included by AFR registration and compile units needing directory read FOP prototypes.

## Risks and test signals
The main risk is signature drift against Gluster fop expectations or implementation definitions. Compile coverage and translator fop-table tests should catch mismatched prototypes; runtime tests should verify all declared entry points are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.c

## Purpose
Implements AFR entry-changing directory FOPs: create, mknod, mkdir, link, symlink, rename, unlink, and rmdir. Each operation is wrapped in AFR transaction machinery so parent entry locks, changelog pre/post operations, quorum, and read-subvolume state stay consistent across replicas.

## Important APIs, types, and functions
`afr_build_parent_loc()` derives parent `loc_t` values for entry locks. `__afr_dir_write_fill()` records child replies and fd open state for create. `__afr_dir_write_finalize()` chooses final errno, authoritative inode/parent stats, and response xdata using current readable subvolumes. `__afr_dir_write_cbk()` is the common child callback. `afr_mark_entry_pending_changelog()` and `afr_mark_new_entry_changelog()` mark partial successful creates/mknods/mkdirs so heal can repair new entries. Public FOPs set `local->transaction.wind`, `unwind`, basename fields, parent locs, and call `afr_transaction()`.

## Control flow
The exported FOP copies the caller frame, initializes `afr_local_t`, copies locs and xdata, sets operation-specific continuation fields, then starts an `AFR_ENTRY_TRANSACTION` or `AFR_ENTRY_RENAME_TRANSACTION`. Transaction code obtains internal locks and winds the per-child operation. Once all child callbacks arrive, the common callback finalizes output, optionally unwinds early if nothing failed, updates pending changelogs for partial new-entry success, and resumes the transaction for post-op/unlock.

## State and persistence behavior
Persistent effects are the requested namespace mutations on child bricks and AFR pending changelog xattrs for inconsistent results. In-memory effects include reply arrays, selected readable parent masks, fd context open marks for create, inode refresh flags after failed child replies, and transaction parent/basename lock state.

## Dependencies and integration points
Integrates with `afr_transaction()`, AFR changelog encoding, read-subvolume interpretation, self-heal through pending xattrs, Gluster child entry FOPs, `AFR_STACK_UNWIND`, dict/xdata helpers, inode refresh marking, and quorum/error-selection helpers.

## Risks and test signals
Risks include parent loc construction errors, rename with two parent locks, partial success without pending xattr marking, `ENOTEMPTY` handling not marking failure, missing `gfid-req` on mkdir, stale stat selection after failures, and fd state divergence after create. Tests should cover every entry FOP with all-success, one-child-fail, quorum-fail, rename across parents, create fd open state, new-entry heal marking, and xdata/error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.h

## Purpose
Declares AFR directory write-side entry points for namespace-mutating FOPs.

## Important APIs, types, and functions
Exports `afr_create()`, `afr_mknod()`, `afr_mkdir()`, `afr_unlink()`, `afr_rmdir()`, `afr_link()`, `afr_rename()`, and `afr_symlink()`. Signatures mirror Gluster fops, including umask, flags, `fd_t`, source/destination locs, linkpath, and xdata.

## Control flow
Callers enter these functions through the AFR fops table. Each implementation creates an AFR transaction frame, records operation parameters in `afr_local_t`, and delegates concurrency, locking, and changelog handling to common transaction code.

## State and persistence behavior
No state is declared here, but these prototypes expose operations that mutate namespace state and AFR pending changelog metadata on child bricks.

## Dependencies and integration points
Depends on Gluster core types and is coupled to `afr-dir-write.c` definitions and the translator fops registration code.

## Risks and test signals
Signature mismatch is the primary header-level risk. Build checks should catch drift, while integration tests should verify each declared operation appears in the AFR fops vector and preserves expected unwind argument order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.c

## Purpose
Implements AFR inode read-side FOPs and special xattr queries. Normal reads select one readable child and retry through `afr_read_txn()`, while management xattrs may query all children, aggregate results, or trigger heal/split-brain workflows.

## Important APIs, types, and functions
Public FOPs include `afr_access()`, `afr_stat()`, `afr_fstat()`, `afr_readlink()`, `afr_readv()`, `afr_seek()`, `afr_getxattr()`, and `afr_fgetxattr()`. `afr_handle_quota_size()` chooses maximum quota metadata across readable children. `afr_filter_xattrs()` removes internal AFR xattrs from user-visible responses. `afr_is_special_xattr()` maps pathinfo, clear-lock, lockinfo, stime, quota-size, and node-UUID requests to all-subvolume callbacks. `afr_handle_heal_xattrs()` dispatches heal-info, split-brain heal, and split-brain status commands.

## Control flow
Simple reads initialize local state, copy loc/fd/xdata, optionally call `afr_fix_open()`, and invoke `afr_read_txn()` with data or metadata transaction type. Per-child callbacks either unwind on success or store errno and call `afr_read_txn_continue()` on failure. `getxattr` first rejects internal AFR keys, handles marker/heal/special keys, node UUID fallback, and only then uses the normal read transaction path.

## State and persistence behavior
Most state is frame-local reply aggregation. Some commands can trigger persistent side effects indirectly: heal xattrs launch self-heal/split-brain synctasks, clear-lock xattrs affect locks in lower layers, and quota-size aggregation rewrites the response dict to the maximum observed value. Internal AFR xattrs are intentionally filtered before unwind.

## Dependencies and integration points
Depends on AFR read transactions, self-heal and split-brain helpers, marker xattr helpers, quota utilities, libxlator stime aggregation, atomic counters, dict serialization, child `getxattr`/`fgetxattr` FOPs, and fd reopen repair.

## Risks and test signals
Risks include leaking internal xattrs, retrying on errors that should be final, wrong aggregation buffer sizing, lockinfo TODO behavior that can ignore per-reply processing failures, special xattr handling diverging between path and fd variants, and heal command authorization assumptions. Tests should cover normal read failover, split-brain read failure, all special xattr aggregations, internal xattr filtering, quota max selection, node UUID fallback, and fd reopen before fd-based reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.h

## Purpose
Declares AFR inode read-side FOP entry points and the quota-size helper used by read response aggregation.

## Important APIs, types, and functions
Exports `afr_access()`, `afr_stat()`, `afr_fstat()`, `afr_readlink()`, `afr_readv()`, `afr_getxattr()`, `afr_fgetxattr()`, `afr_seek()`, and `afr_handle_quota_size()`. The declarations separate path-based and fd-based variants and preserve Gluster fop callback argument shapes.

## Control flow
The translator fops table routes inode read operations through these functions. Implementations initialize AFR frame state and commonly delegate child selection and retry behavior to `afr_read_txn()`.

## State and persistence behavior
The header declares no storage. Its functions mostly expose transient read behavior, except special xattr commands in the implementation can initiate heal-related side effects.

## Dependencies and integration points
Depends on AFR types such as `afr_local_t`, Gluster core types, `gf_seek_what_t`, and dict/xdata APIs. It is coupled to read transaction and self-heal implementation files.

## Risks and test signals
Header risks are prototype drift and missing registration. Compile coverage plus smoke tests for all inode read fops, including `seek` and quota xattr paths, are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.c

## Purpose
Implements AFR inode write-side FOPs, including data writes, truncation, metadata changes, xattr mutation, allocation/discard/zerofill, xattrop/fxattrop, and fsync. It wraps each operation in AFR transaction machinery to coordinate internal locks, changelogs, readable-subvolume updates, delayed post-op behavior, and split-brain controls.

## Important APIs, types, and functions
`__afr_inode_write_fill()` and `__afr_inode_write_finalize()` are the shared reply collection/finalization path. `afr_writev()` duplicates iovecs, requests active-fd and append-write hints, repairs fd opens, and starts a data transaction; `afr_process_post_writev()` handles unstable writes, short writes, and open-fd count updates. Truncate/ftruncate/fallocate/discard/zerofill set byte-range transaction locks. Setattr/fsetattr and xattr operations use metadata transactions. `afr_handle_special_xattr()` handles split-brain choice/resolve, choice timeout, add-brick, and replace-brick commands. `afr_fsync()` clears unstable-write state and can disable delayed post-op on the last fsync.

## Control flow
Most public FOPs copy the frame, initialize `afr_local_t`, copy loc/fd/xdata, set `transaction.wind` and `transaction.unwind`, set range or metadata lock coordinates, and call `afr_transaction()`. Child callbacks feed the common finalizer. If all child operations succeeded, the original FOP can unwind before or alongside transaction resume; writev has special ordering so delayed post-op state is visible to flush before user unwind.

## State and persistence behavior
Persistent effects include child file data/metadata mutations and AFR pending changelog xattrs maintained by transaction code. In-memory state includes reply arrays, selected readable masks, inode ctx lock/open-fd counters, unstable-write flags, split-brain choice, empty-brick pending matrices, and xdata/xattr response refs. Arbiter bricks receive a one-byte write but report logical length.

## Dependencies and integration points
Depends on `afr_transaction()`, internal lock/common transaction code, self-heal helpers, split-brain helpers, fd reopen repair, protocol-common xdata keys, child write/xattr FOPs, dict utilities, syncbarrier/synctask for empty-brick operations, and AFR inode context tracking.

## Risks and test signals
Risks include short writes causing replica divergence, delayed post-op/flush races, append detection mistakes, arbiter write length translation, internal xattr bypass, split-brain command validation, empty-brick lock coverage, and an apparent `afr_zerofill_unwind()` use of `AFR_STACK_UNWIND(discard, ...)` despite the public zerofill path. Tests should cover partial child failures, append and O_SYNC writes, fsync last-fsync, internal xattr rejection, split-brain set/resolve, replace/add brick marking, range locking for writes/truncates, and zerofill unwind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.h

## Purpose
Declares AFR inode write-side FOP entry points for data, metadata, xattr, allocation, and fsync operations.

## Important APIs, types, and functions
Exports `afr_writev()`, `afr_truncate()`, `afr_ftruncate()`, `afr_setattr()`, `afr_fsetattr()`, `afr_setxattr()`, `afr_fsetxattr()`, `afr_removexattr()`, `afr_fremovexattr()`, `afr_discard()`, `afr_fallocate()`, `afr_zerofill()`, `afr_xattrop()`, `afr_fxattrop()`, and `afr_fsync()`.

## Control flow
These declarations are the fops-table contract. Implementations convert each call into an AFR data or metadata transaction with operation-specific wind/unwind callbacks and lock ranges.

## State and persistence behavior
The header has no direct state. The declared operations mutate child brick contents, metadata, xattrs, and AFR changelog state through the implementation.

## Dependencies and integration points
Depends on Gluster types for vectors, iobrefs, inode attributes, xattrop flags, fds, locs, dicts, and call frames. It is tightly coupled to AFR transaction and inode context internals.

## Risks and test signals
Prototype drift and missing fops registration are the header-level risks. Build and ABI checks plus integration tests for every exported write operation are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-lk-common.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-lk-common.c

## Purpose
Provides the shared internal lock engine used by AFR transactions. It manages entry locks and inode locks across replica children, supports nonblocking acquisition with blocking fallback, records which nodes are locked for each lockee, and performs coordinated unlock.

## Important APIs, types, and functions
`afr_add_entry_lockee()` and `afr_add_inode_lockee()` populate transaction lock targets. `afr_entry_lockee_cmp()` gives deterministic entry lock ordering by gfid and basename. `afr_set_lk_owner()` assigns a lock owner from a pointer. `afr_lock_nonblocking()` sends parallel nonblocking locks to up children. `afr_blocking_lock()` retries serial blocking locks. `afr_unlock()` handles eager-lock owner list release and calls `afr_unlock_now()` when actual unlock is needed. `afr_internal_lock_wind()` chooses entrylk/fentrylk or inodelk/finodelk based on transaction type.

## Control flow
Transactions set up lockees, then try nonblocking locks across up children. If every expected lock succeeds, the transaction callback proceeds. If only some locks succeed, AFR unlocks and retries with blocking locks in deterministic child/lockee order. Blocking lock sufficiency requires at least one child where every required lockee succeeded, which matters for multi-lock operations such as mkdir and rename. Unlock callbacks decrement `lk_call_count` and call the transaction continuation once all unlocks finish.

## State and persistence behavior
State is in `afr_internal_lock_t`: lockee array, `locked_nodes[]`, locked counts, attempted counts, expected counts, op errno, lock domain, and callback. For data transactions, successful inode locks increment `inode_ctx->lock_count`; unlock can reset write subvol state. Locks are not durable, but they gate durable child mutations and changelog updates.

## Dependencies and integration points
Depends on AFR transaction types, AFR memory types, child lock FOPs, fd ctx, inode ctx, eager-lock lists, Gluster lock owner helpers, and logging message IDs. It is central to directory and inode write transaction correctness.

## Risks and test signals
Risks include deadlocks from ordering mistakes, lock leaks after partial failures, insufficient multi-lock success checks, ENOSYS behavior when locks xlator is missing, fd ctx failures during lock acquisition, eager-unlock races, and incorrect data lock count accounting. Tests should cover nonblocking success, fallback to blocking, multi-lock rename, unlock after partial child failure, child down filtering, ENOSYS, eager lock release, and fd-based lock paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-lk-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-mem-types.h

## Purpose
Defines AFR-specific memory allocation type IDs used by Gluster's memory accounting and debugging system.

## Important APIs, types, and functions
The `gf_afr_mem_types_` enum starts at `gf_common_mt_end + 1` and assigns IDs for AFR fd context, private state, integer/char helpers, xattr keys, dict/xlator arrays, inode context, self-heal daemon events, replies, healer structures, split-brain choice timeout/status, empty brick handling, lock-heal info, and `gf_lock`.

## Control flow
No runtime control flow exists in this header. Allocation sites pass these enum values to `GF_MALLOC`, `GF_CALLOC`, or related macros, allowing statedump and leak diagnostics to classify AFR allocations.

## State and persistence behavior
No persistent state is stored. The enum values are part of diagnostic ABI within the process; changing or reordering values can make memory accounting harder to interpret.

## Dependencies and integration points
Includes `glusterfs/mem-types.h` for common allocator IDs. Used throughout AFR implementation files wherever typed allocation is performed.

## Risks and test signals
Risks include reusing or reordering IDs, forgetting to add a type for new long-lived structures, or using a misleading allocation type. Test signals are clean builds, memory-accounting statedumps showing expected buckets, and leak tests that can attribute AFR allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-messages.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-messages.h

## Purpose
Defines stable AFR log message IDs and shared message strings for structured Gluster logging.

## Important APIs, types, and functions
The `GLFS_MSGID(AFR, ...)` macro enumerates AFR message identifiers for quorum, child state, locks, split-brain, self-heal, thin arbiter, fsync, xattr, replace/add brick, and many error paths. The following `#define` string constants provide reusable text for common log messages.

## Control flow
No executable control flow is present. The file is included by AFR source files that call `gf_msg()`, `gf_smsg()`, and related logging helpers with stable message IDs.

## State and persistence behavior
Message IDs are a persistent observability contract: comments require appending new IDs and never deleting existing IDs to avoid ID reuse. Strings affect logs and downstream tooling but not filesystem state.

## Dependencies and integration points
Includes `glusterfs/glfs-message-id.h`. Integrated throughout AFR read, write, lock, open, heal, transaction, and thin-arbiter code paths.

## Risks and test signals
Risks include deleting/reordering IDs, typos in user-visible diagnostics, duplicate semantics, and callers using mismatched IDs for a failure mode. Tests are mainly compile-time plus log-oriented tests or static checks that message IDs remain append-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-open.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-open.c

## Purpose
Implements AFR file open and background fd reopen repair. Opens are broadcast to all up children while avoiding direct truncation outside AFR transactions; fd repair reopens fds on children that were down or not opened when the fd was first established.

## Important APIs, types, and functions
`afr_open()` checks quorum and consistency, stores fd flags in `afr_fd_ctx_t`, refreshes split-brain/readability state when needed, then calls `afr_open_continue()`. `afr_open_cbk()` records child open status and optionally issues an AFR-level `ftruncate` when the original open included `O_TRUNC`. `afr_fix_open()` creates an internal frame for fd repair. `afr_fd_ctx_set_need_open()` marks eligible children `AFR_FD_OPENING`; `afr_is_reopen_allowed()` queries locks with `lk(F_GETLK)` and `fd-reopen-status`; `afr_do_fix_open()` winds open/opendir to missing children.

## Control flow
Normal open initializes local/fd context, strips `O_TRUNC` from child `open`, winds open to all up children, handles reply quorum, and unwinds or runs truncation through the translator. Reopen repair first validates the fd is non-anonymous and has a gfid, marks missing children, asks up children whether reopen is safe around locks, and either opens missing children or resets their state to not opened.

## State and persistence behavior
Fd context persists in memory with `flags` and `opened_on[]` states. `O_TRUNC` can cause durable size change through a transaction-safe ftruncate path. Reopen repair only changes fd state and child open handles; it does not directly mutate file contents.

## Dependencies and integration points
Depends on AFR transaction/ftruncate, inode refresh and split-brain helpers, child open/opendir/lk FOPs, fd context helpers, protocol `fd-reopen-status` values, Gluster statedump/logging, and read paths that call `afr_fix_open()` before fd-based operations.

## Risks and test signals
Risks include truncating outside correct transaction ordering, reopening despite conflicting locks, leaving `AFR_FD_OPENING` stuck after failures, fd repair on anonymous/null-gfid fds, and quorum handling for partial opens. Tests should cover open with and without `O_TRUNC`, child-down then child-up fd repair, conflicting locks blocking reopen, directory fd repair, all-open-fail, and xdata propagation from successful child opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-read-txn.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-read-txn.c

## Purpose
Implements AFR read transaction selection and retry logic. It chooses a readable replica for a read-like operation, refreshes inode readability state when cached generations are stale, retries failed reads on alternate readable children, and handles thin-arbiter decision paths.

## Important APIs, types, and functions
`afr_read_txn()` is the exported orchestration function. `afr_read_txn_wind()` updates pending read counters and invokes the caller-provided read wind function. `afr_read_txn_continue()` refreshes once after a failed read, then falls through to `afr_read_txn_next_subvol()`. `afr_read_txn_refresh_done()` picks a new read subvol after refresh or applies split-brain choice. Thin-arbiter helpers `afr_ta_read_txn_synctask()` and `afr_ta_read_txn()` use xattrop and a thin-arbiter lock to determine which data child is safe when a brick is down.

## Control flow
The caller supplies an inode, read wind callback, and transaction type. AFR verifies quorum, consistent I/O, and thin-arbiter quorum. It consults cached inode read-subvolume state, intersects data and metadata readable masks, refreshes stale caches, selects by policy, and winds the chosen child. On child read failure, the caller callback invokes `afr_read_txn_continue()`, which refreshes once and then tries each unread attempted readable child before finally winding `subvol == -1` to force unwind with the stored error.

## State and persistence behavior
State is frame-local (`readable[]`, `read_attempted[]`, `read_subvol`, `refreshed`, transaction type) plus `priv->pending_reads[]` atomics. Thin-arbiter logic performs xattrop reads of pending changelog state and takes a thin-arbiter inodelk but does not change user data.

## Dependencies and integration points
Used by directory reads and inode reads. Depends on inode refresh/readable caches, read-subvolume policy, split-brain choice helpers, quorum helpers, thin-arbiter loc/xattr helpers, syncop xattrop/inodelk, and child up/event generation state.

## Risks and test signals
Risks include off-by-one child-index checks in pending read counters, stale generation handling, retry loops skipping valid children, split-brain choice overriding incorrectly, thin-arbiter lock/xattrop failures returning misleading errno, and pending read counter imbalance. Tests should cover first read on uncached inode, stale generation refresh, failover after read error, no readable subvol, split-brain chosen child, thin-arbiter one-child-down reads, and pending read accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-read-txn.c -->
