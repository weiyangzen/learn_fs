# Research: subset-b-007094

Grouped research for the GlusterFS locks and marker quota files assigned to `subset-b-007094`. Each section preserves the original source path so the reconciliation lane can split this document into source-tree-aligned per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/posix.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/posix.c

## Purpose
`posix.c` is the main entry point for the GlusterFS `features/locks` translator. It implements the translator lifecycle, fop/cbk tables, POSIX byte-range locks, mandatory-lock enforcement for I/O paths, lock migration support, lock-count xdata responses, meta-locks used by rebalance, lock state dumps, and cleanup on fd, inode, and client lifetime events.

## Important APIs, Types, And Functions
The file is built around `pl_inode_t`, `posix_lock_t`, `pl_local_t`, `pl_fdctx_t`, `pl_ctx_t`, `pl_meta_lock_t`, and `posix_locks_private_t` from the locks headers. Exported translator operations are installed in `struct xlator_fops fops`, `struct xlator_cbks cbks`, `struct xlator_dumpops dumpops`, and `xlator_api`.

Important lock APIs include `pl_lk`, `pl_is_fop_allowed`, `__rw_allowable`, `do_blocked_rw`, `pl_flush`, `pl_release`, `pl_forget`, `pl_getactivelk`, and `pl_setactivelk`. Xdata/count handling is centralized in `PL_LOCAL_GET_REQUESTS`, `pl_has_xdata_requests`, `pl_get_xdata_requests`, `pl_set_xdata_response`, and count fillers for entry, inode, and POSIX locks. Mandatory-lock control uses `PL_CHECK_LOCK_ENFORCE_KEY`, `pl_track_io_fop_count`, and the set/removexattr callbacks. Lock migration and rebalance coordination use `GF_META_LOCK_KEY`, `GF_META_UNLOCK_KEY`, `pl_metalk`, `pl_metaunlock`, `pl_fill_active_locks`, `gf_lkmig_info_to_posix_lock`, and `pl_write_active_locks`.

## Control Flow
Normal FOPs either pass through while adding xdata bookkeeping, or first validate lock state. `readv`, `writev`, `truncate`, `ftruncate`, `discard`, and `zerofill` build a `posix_lock_t` region and call `pl_is_fop_allowed` when mandatory locking is active. If the operation can proceed, it winds to the child translator; if it conflicts and the fd permits blocking, a call stub is queued on `pl_inode->rw_list`; otherwise it unwinds with `EAGAIN` or `EBUSY`. `do_blocked_rw` later scans queued read/write requests after lock release and resumes stubs whose regions are now allowable.

`pl_lk` validates flock ranges, normalizes negative `l_len`, creates a `posix_lock_t`, handles reserve-lock commands, fd lock enumeration, `F_GETLK`, `F_SETLK`, and `F_SETLKW`, and integrates with reserve locks before calling `pl_setlk`. Blocking locks remain queued by lower helper logic; nonblocking conflicts return `EAGAIN`. Unlocks can alter the returned flock type so NLM can detect whether an fd still has locks.

Most metadata FOPs use the `PL_STACK_UNWIND` family so requested lock-count xdata can be attached on unwind. The compatibility macro suppresses extra xdata for clients older than op-version 3.10. Inode removal paths use `PL_INODE_REMOVE` to coordinate pending remove state with lock cleanup before rename, unlink, or rmdir proceeds.

## State And Persistence Behavior
Primary runtime state is in inode and fd contexts, not in this file's own globals. `pl_inode_t` stores active POSIX locks (`ext_list`), blocked read/write stubs (`rw_list`), reserve locks, inode/entry lock domains, meta-locks, mandatory-lock flags, migration state, and counters. `pl_fdctx_t` stores copied locks for `F_GETLK_FD` iteration. `pl_ctx_t` is per-client state used to clean inode, entry, and meta locks on disconnect or destroy.

Persistent or cross-translator state is represented through xattrs and dictionaries. The file reads pathinfo and lockinfo xattrs, serializes lockinfo dictionaries for lock migration across fd reopen, handles `GF_XATTR_CLRLK_CMD`/`GF_XATTR_INTRLK_CMD`, and sets or removes `GF_ENFORCE_MANDATORY_LOCK`. Meta-lock and active-lock migration state is passed through FOPs rather than stored on disk here.

## Dependencies And Integration Points
The file depends on GlusterFS translator infrastructure (`STACK_WIND`, unwind macros, `xlator_api_t`), inode/fd/client context APIs, dict/xdata helpers, syncops, statedump, lock helpers from `common.c`, `clear.c`, `inodelk.c`, `entrylk.c`, and reserve-lock helpers from `reservelk.c`. It must sit over exactly one child and eventually over a `storage/` translator. Its options expose mandatory locking, tracing, revocation, contention notification, and enforced mandatory lock behavior.

## Risks And Edge Cases
Risk concentrates around lock lifetime and concurrency: mutex ordering between client ctx and inode ctx, waking blocked stubs after deletion or migration, stale frame/local ownership on forced cleanup, and keeping fd/inode refs balanced. Mandatory-lock enforcement has subtle behavior differences between `forced`, `file`, and `optimal` modes; wrong flag handling can either reject valid I/O or let fenced writes through. Lock migration has explicit TODOs around partial failure and meta-lock cleanup. Compatibility code for older clients can hide xdata responses, so changes to xdata behavior need op-version awareness.

## Test Signals
Direct unit coverage in this subset is only for entry lock name semantics, not `posix.c`. Strong test signals would include mandatory-lock read/write/truncate blocking, nonblocking fd `EAGAIN`, lock-count xdata requests on lookup/stat/readdirp, clear-lock xattrs, client disconnect cleanup, fd lock migration using `GF_XATTR_LOCKINFO_KEY`, meta-lock migration, and statedump lock lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/reservelk.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/src/reservelk.c

## Purpose
`reservelk.c` implements reserve locks for the locks translator. Reserve locks are exact-range reservations that can block later POSIX lock calls until the matching reservation is unlocked. `posix.c` calls this file from `pl_lk` for `F_RESLK_*` commands and before ordinary `F_SETLK/F_SETLKW` requests.

## Important APIs, Types, And Functions
The public functions are `reservelks_equal`, `pl_verify_reservelk`, `grant_blocked_reserve_locks`, `grant_blocked_lock_calls`, `pl_reserve_unlock`, and `pl_reserve_setlk`. Internal helpers include `__reservelk_grantable`, `__same_owner_reservelk`, `__matching_reservelk`, `__reservelk_conflict`, `_pl_verify_reservelk`, `__lock_reservelk`, `find_matching_reservelk`, and `__reserve_unlock_lock`.

## Control Flow
Reservation equality is exact: start and end offsets must match. Setting a reserve lock checks `pl_inode->reservelk_list`; if an equal reservation exists, nonblocking callers get `-EAGAIN`, while blocking callers are linked to `pl_inode->blocked_reservelks`. Otherwise the lock is inserted into `reservelk_list`.

Ordinary POSIX locks call `pl_verify_reservelk`. If a matching reservation exists with the same owner, the reserve lock is consumed and destroyed so the POSIX lock can continue. If the owner differs, the POSIX lock is added to `pl_inode->blocked_calls` and the caller is held. Unlocking a reserve lock removes the exact matching reservation, grants newly possible reserve locks, then retries blocked ordinary lock calls through `pl_setlk`.

## State And Persistence Behavior
All state is in `pl_inode_t` lists protected by `pl_inode->mutex`: active reservations, blocked reservations, and blocked lock calls. There is no disk persistence. Waiting callers hold their original `posix_lock_t` and frame until grant or failure.

## Dependencies And Integration Points
This file depends on list primitives, `posix_lock_t`, lock owner comparison, `__delete_lock`, `__destroy_lock`, `pl_setlk`, tracing, fd-number conversion, refkeeper updates, and GlusterFS unwind macros. It is tightly integrated with `pl_lk` in `posix.c`.

## Risks And Edge Cases
The exact-boundary matching model is narrow; overlapping but non-identical reservations do not conflict. `__matching_reservelk` returns the list iterator after traversal, so callers rely on list macros producing `NULL`-like behavior only through loop control assumptions. The helper `__grant_blocked_lock_calls` splices from `blocked_reservelks` even though it is named for blocked ordinary calls; if this is not intentional, blocked POSIX calls may not drain as expected. Frame lifetime is delicate because blocked locks are unwound outside the inode mutex.

## Test Signals
Useful tests should exercise exact same-range reserve locks, same-owner conversion into POSIX locks, different-owner blocking, nonblocking `EAGAIN`, unlock granting order, and interaction with later `pl_setlk` conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/src/reservelk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/tests/unit-test.c -->
# sources/distributed-fs/glusterfs/xlators/features/locks/tests/unit-test.c

## Purpose
This is a small standalone unit test for entry lock name conflict behavior. It constructs a `pl_inode_t` with directory lock state and calls `lock_name`/`unlock_name` directly.

## Important APIs, Types, And Functions
The file imports GlusterFS base headers plus `locks.h` and `common.h`. It declares external `lock_name(pl_inode_t *, const char *, entrylk_type)` and `unlock_name(pl_inode_t *, const char *, entrylk_type)`. The `expect` macro jumps to `out` on failure, and `main` returns 0 only if all expectations pass.

## Control Flow
The test initializes `pinode->dir_lock_mutex` and `pinode->gf_dir_locks`, then checks these scenarios: a whole-directory write lock blocks a named write lock; unlocking the whole-directory lock succeeds; repeated read locks on the same basename are compatible; a write lock conflicts with those reads; write lock/unlock on one basename succeeds; and a write lock blocks a read lock on the same different basename.

## State And Persistence Behavior
State is entirely in heap memory allocated by `CALLOC`. The test does not persist anything and does not free or destroy all initialized state before exit, which is acceptable for a short process but not a reusable harness pattern.

## Dependencies And Integration Points
It depends on the entry lock implementation exposing non-static `lock_name` and `unlock_name`. It is a lower-level signal than translator FOP tests because it bypasses frames, xdata, client identity, and inode context setup.

## Risks And Test Signals
The test covers core reader/writer compatibility for basename entry locks, including the special `NULL` basename. It does not test blocked queues, owners, domains, fd paths, or cleanup. A failure returns `1` without describing which expectation failed, so diagnostic value is limited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/locks/tests/unit-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/marker/Makefile.am

## Purpose
This top-level automake file for the marker feature translator delegates all build work to the `src` subdirectory.

## Important APIs, Types, And Functions
There are no C APIs. The only meaningful variables are `SUBDIRS = src` and `CLEANFILES =`.

## Control Flow
Automake descends into `src`, where the actual `marker.la` translator target is declared. Cleanup has no extra files at this level.

## State, Dependencies, And Integration Points
The file participates in the GlusterFS autotools build. Its integration point is directory recursion; missing `src` would make the marker translator unavailable to the build.

## Risks And Test Signals
Risk is low. Build-system tests should confirm `make` enters `xlators/features/marker/src` and that dist/clean targets still work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/Makefile.am

## Purpose
This automake file builds the `marker.la` translator module when server-side translators are enabled. It defines the marker source files, headers, include paths, linker flags, and compiler flags.

## Important APIs, Types, And Functions
The target is `marker.la`, installed under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. `marker_la_SOURCES` includes `marker.c`, `marker-quota.c`, `marker-quota-helper.c`, and `marker-common.c`. `noinst_HEADERS` includes marker and quota headers plus `libxlator.h`. `marker_la_LIBADD` links against `libglusterfs.la`.

## Control Flow
`if WITH_SERVER` gates whether the xlator library is built. The build compiles with `GF_CPPFLAGS`, `GF_CFLAGS`, include paths for libglusterfs, rpc xdr generated headers, and xlator lib sources.

## State And Persistence Behavior
There is no runtime state. Build outputs are the libtool module and standard automake artifacts.

## Dependencies And Integration Points
The file integrates marker with GlusterFS' translator installation layout and with libglusterfs. Changes here affect whether marker quota code is compiled, packaged, and loadable.

## Risks And Test Signals
Source/header list drift is the main risk: adding a new marker file without updating this file can break builds or omit functionality. Test signals are autotools configure/build success under `WITH_SERVER` and package install path verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.c -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.c

## Purpose
`marker-common.c` provides shared inode-context allocation for the marker translator. It creates `marker_inode_ctx_t` objects and guarantees an inode has a marker context attached.

## Important APIs, Types, And Functions
`marker_inode_ctx_new` allocates a zeroed `marker_inode_ctx_t` with `quota_ctx` initially `NULL`. `marker_force_inode_ctx_get` retrieves the marker inode context from `inode_ctx`; if absent, it allocates one and stores it under the translator key.

## Control Flow
`marker_force_inode_ctx_get` locks `inode->lock`, attempts `__inode_ctx_get`, and either returns the existing context or allocates and installs a new one via `__inode_ctx_put`. On install failure it frees the new context before unlocking.

## State And Persistence Behavior
State is per-inode in-memory translator context. The marker context owns the pointer to quota-specific context but this file does not allocate that nested quota context. There is no disk persistence.

## Dependencies And Integration Points
It depends on `marker.h` for `marker_inode_ctx_t`, GlusterFS memory accounting through `gf_marker_mt_marker_inode_ctx_t`, and inode context APIs. `marker-quota-helper.c` uses it before creating quota inode contexts.

## Risks And Test Signals
Correct locking is critical because multiple operations may race to create marker contexts. Tests should exercise repeated context creation on the same inode and allocation failure paths. Consumers must free nested quota state during forget paths; this helper only manages the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.h -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.h

## Purpose
This header exposes the common marker inode-context helper to marker source files.

## Important APIs, Types, And Functions
It includes `marker.h` and declares `marker_force_inode_ctx_get(inode_t *, xlator_t *, marker_inode_ctx_t **)`.

## Control Flow, State, And Dependencies
The header contains no runtime logic or state. Its only integration point is sharing the inode context retrieval/creation contract implemented in `marker-common.c`.

## Risks And Test Signals
The declaration must stay synchronized with the implementation. Since it exposes only one helper, build success across marker quota files is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-mem-types.h

## Purpose
This header defines marker-specific memory accounting IDs used by GlusterFS allocation macros.

## Important APIs, Types, And Functions
The enum `gf_marker_mem_types_` starts at `gf_common_mt_end + 1` and defines accounting buckets for marker config, locs, volume marks, int64 allocations, quota inode contexts, marker inode contexts, contribution nodes, quota metadata, quota synctask args, and `gf_marker_mt_end`.

## Control Flow And State
There is no executable control flow. The enum values are consumed by `GF_CALLOC`, `GF_MALLOC`, and related macros in marker and quota code to attribute allocations.

## Dependencies And Integration Points
The file depends on `<glusterfs/mem-types.h>` and is included by marker quota headers and sources. It must remain consistent with `xlator_mem_acct_init` usage in the broader marker translator.

## Risks And Test Signals
Adding new marker allocation classes should happen before `gf_marker_mt_end`. Duplicating or reordering values can confuse memory accounting. Test signals are successful compilation and memory-accounting initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.c -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.c

## Purpose
`marker-quota-helper.c` owns helper routines for quota inode contexts, contribution nodes, and loc reconstruction. These utilities support the quota transaction engine in `marker-quota.c`.

## Important APIs, Types, And Functions
Key APIs are `mq_loc_fill`, `mq_inode_loc_fill`, `mq_alloc_inode_ctx`, `mq_contri_init`, `mq_get_contribution_node`, `mq_add_new_contribution_node`, `mq_dict_set_contribution`, `mq_inode_ctx_get`, and `mq_inode_ctx_new`. Internals include `mq_contri_fini` and `__mq_add_new_contribution_node`.

## Control Flow
`mq_inode_loc_fill` resolves an inode's parent and path, fills a `loc_t`, and ensures a quota context exists. Root inodes are handled without a parent. `mq_alloc_inode_ctx` initializes quota totals, dirty/update flags, a lock, and an empty contribution list. `mq_contri_init` creates refcounted contribution nodes keyed by a parent inode gfid. `mq_add_new_contribution_node` skips root paths, locks the quota context, finds or creates a contribution node for the current parent, and returns a ref. `mq_dict_set_contribution` builds the correct trusted quota contribution xattr key, including volume-version suffixes through `GET_CONTRI_KEY`.

## State And Persistence Behavior
In-memory state lives in `quota_inode_ctx_t` under `marker_inode_ctx_t->quota_ctx`; it tracks size, file count, directory count, dirty status, update/create status, and a list of `inode_contribution_t` entries. Persistent state is addressed by trusted xattr keys built here, but actual reads/writes are performed in `marker-quota.c`.

## Dependencies And Integration Points
This file depends on inode tables, path resolution, marker common context helpers, quota key macros from `marker-quota.h`, GlusterFS refcounts, and memory accounting. `marker-quota.c` relies on these helpers before every quota xattr transaction.

## Risks And Test Signals
Parent resolution is a fragile area for hard links, root entries, and stale inodes. Contribution nodes are refcounted and also list-linked, so missing `GF_REF_PUT` or failing to delete from lists can leak or use freed nodes. Tests should cover root, nameless lookups, hard-link parents, repeated contribution insertion, context racing, and long key generation near `QUOTA_KEY_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.h -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.h

## Purpose
This header declares quota helper APIs and macros used by the marker quota implementation.

## Important APIs, Types, And Functions
Macros include `QUOTA_FREE_CONTRIBUTION_NODE`, `QUOTA_SAFE_INCREMENT`, and `QUOTA_SAFE_DECREMENT`. Declared functions cover contribution creation, contribution xattr key insertion, quota inode context creation/retrieval, contribution deletion, inode-to-loc filling, contribution initialization, and contribution lookup.

## Control Flow And State
The header itself has no executable state. The macros mutate shared quota state under locks: contribution deletion removes the list node and drops a ref; increment/decrement macros update counters with a supplied lock.

## Dependencies And Integration Points
It includes `marker.h` and exposes helper contracts to `marker-quota.c`. It depends on `quota_inode_ctx_t` and `inode_contribution_t` definitions being available through included marker quota headers in compilation units.

## Risks And Test Signals
Macro callers must pass valid locks and initialized contribution nodes. `QUOTA_FREE_CONTRIBUTION_NODE` combines list mutation with refcount release, so double-free or double-delete bugs are possible if callers also manipulate the list. Build coverage plus quota forget/rename/unlink tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.c -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.c

## Purpose
`marker-quota.c` implements quota xattr maintenance for the marker translator. It keeps directory size/file/dir-count xattrs and per-parent contribution xattrs consistent after creates, writes, renames, deletes, and lookup-driven self-heal.

## Important APIs, Types, And Functions
The central exported APIs are `mq_req_xattr`, `mq_xattr_state`, `mq_initiate_quota_txn`, `mq_initiate_quota_blocking_txn`, `mq_create_xattrs_txn`, `mq_reduce_parent_size_txn`, and `mq_forget`. Supporting operations include context status setters, `mq_build_ancestry`, `quota_dict_set_size_meta`, metadata math (`mq_compute_delta`, `mq_add_meta`, `mq_sub_meta`), xattr checks and creation (`mq_are_xattrs_set`, `mq_create_size_xattrs`), locking (`mq_lock`), dirty flag operations, metadata reads, contribution/size updates, synctask wrappers, transaction prevalidation, dirty-directory rebuild, and xattr inspection for files and directories.

## Control Flow
Quota updates are usually asynchronous synctasks. `mq_prevalidate_txn` rejects unsupported inode types, DHT linkfiles, missing gfids, and missing contexts, then copies a `loc_t` and resolves parent state. `mq_create_xattrs_txn` serializes create-xattr work using `create_status`, possibly creates a contribution node, and runs `mq_create_xattrs_task`; that task locks directories, checks existing xattrs, creates missing size xattrs, and starts a blocking quota transaction if needed.

`mq_initiate_quota_task` walks from a changed child up to root. At each level it resolves/validates the parent, locks the parent with an inode lock, gets or creates the child contribution node, computes delta between current size and contribution, marks the parent dirty with get-and-set xattrop, updates the child contribution xattr, updates the parent size xattr, clears dirty when safe, unlocks, then repeats upward. `mq_reduce_parent_size_task` handles unlink/rename removal by subtracting a child contribution from its old parent and optionally removing the contribution xattr. `mq_update_dirty_inode_task` heals a dirty directory by scanning children with `readdirp`, summing their contribution xattrs, comparing with the directory size xattr, and applying the delta.

Lookup inspection flows through `mq_xattr_state`. It ensures contribution nodes exist, inspects directory or file xattrs, seeds in-memory quota context from trusted xattrs, creates missing xattrs, triggers dirty healing, or starts quota updates when contribution and size diverge.

## State And Persistence Behavior
In-memory quota state is stored in `quota_inode_ctx_t` and `inode_contribution_t`. Persistent state is in trusted xattrs: size metadata under `QUOTA_SIZE_KEY` with optional version suffix, contribution metadata under `trusted.glusterfs.quota.<parent-gfid>.contri`, and dirty state under `trusted.glusterfs.quota.dirty`. Size and contribution metadata use endian-converted `quota_meta_t` arrays with xattrop add semantics. Dirty flags allow lookup-time repair after partial failures.

## Dependencies And Integration Points
The file depends on GlusterFS dict, syncop lookup/xattrop/setxattr/removexattr/inodelk/readdirp/opendir APIs, quota common utilities, marker private config (`marker_conf_t`), inode/path helpers, synctasks, call stubs, and helper APIs from `marker-quota-helper.c`. It integrates with `marker.c`, which calls these transaction functions from FOP callbacks.

## Risks And Edge Cases
The hardest risks are concurrency and partial updates across ancestor chains. Parent changes during rename are explicitly revalidated after locking, but races with parallel removes can still abort and rely on later healing. Dirty flag cleanup is subtle: failures clear in-memory dirty status so future lookup can retry. Rollback after parent size update failure only rolls back contribution xattrs, so error handling depends on dirty repair. Hard-link behavior is acknowledged as needing revisit. Long key generation, missing parent locs, stale inodes, and versioned quota keys are additional edge cases.

## Test Signals
High-value tests include create-xattr bootstrapping for files and directories, write delta propagation to root, unlink and rename parent reduction, hard-link contributions, dirty directory rebuild via readdirp, upgrade cases without inode-quota xattrs, DHT linkfile skips, parent-change races, and failure injection around xattrop/removexattr/lock acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.h -->
# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.h

## Purpose
`marker-quota.h` defines the marker quota data model, xattr key macros, allocation helpers, and public transaction APIs used by the marker translator.

## Important APIs, Types, And Functions
Key constants are `QUOTA_XATTR_PREFIX`, `QUOTA_DIRTY_KEY`, `CONTRIBUTION`, `QUOTA_KEY_MAX`, and `READDIR_BUF`. Key-building macros include `GET_QUOTA_KEY`, `GET_CONTRI_KEY`, and `GET_SIZE_KEY`, which add version suffixes from `marker_conf_t`. Allocation macros include `QUOTA_ALLOC` and `QUOTA_ALLOC_OR_GOTO`.

Core types are `quota_inode_ctx_t`, `quota_synctask_t`, and `inode_contribution_t`. Public prototypes expose xattr request/inspection, quota update transactions, xattr creation, parent size reduction, and quota forget cleanup.

## Control Flow And State
The header defines state containers but no executable control flow. `quota_inode_ctx_t` stores current size, file count, directory count, dirty flag, transaction status flags, a lock, and contribution list. `quota_synctask_t` packages a translator, loc, contribution delta, nlink, and optional call stub for async work. `inode_contribution_t` tracks a parent gfid's contribution and is refcounted.

## Persistence Behavior
The macros define persistent trusted xattr names for quota metadata. Version-aware key construction means the same logic can address different quota schema generations.

## Dependencies And Integration Points
It depends on xlator types, marker memory types, GlusterFS refcounting, quota common utilities, and call stubs. It is included by marker quota source and helper files and forms their shared contract.

## Risks And Test Signals
Macro safety is important because key buffers are fixed at `QUOTA_KEY_MAX`. The `QUOTA_ALLOC` macro appears to pass `sizeof(type)` as the count and `1` as the size, which is equivalent in total bytes but unusual. Tests should cover key construction for versioned and unversioned volumes, root contribution keys, and memory-accounted allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.h -->
