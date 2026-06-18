# Research: subset-b-007074

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.c

## Purpose
`afr-transaction.c` implements the write-side AFR transaction engine for GlusterFS replicate volumes. It coordinates internal locks, pre-op changelog marking, dispatch of the real file operation to eligible replica children, quorum validation, post-op changelog repair/cleanup, eager-lock batching, delayed post-op optimization, durability fsyncs, arbiter safeguards, and thin-arbiter post-op decision logic. It is the core state machine that keeps replicated data, metadata, and directory-entry operations from silently diverging when children fail or partitions occur.

## Important APIs, Types, And Functions
The public entry point is `afr_transaction(frame, this, type)`, which validates quorum and consistency constraints, initializes transaction-local arrays, builds lockees, refreshes metadata readability when needed, and starts the lock/pre-op/FOP/post-op sequence. Other exported helpers include `afr_transaction_fop_failed()`, `afr_transaction_resume()`, `afr_lock()`, `afr_has_quorum()`, `afr_txn_nothing_failed()`, `afr_needs_changelog_update()`, `afr_set_pending_dict()`, `afr_pick_error_xdata()`, `afr_zero_fill_stat()`, `afr_transaction_detach_fop_frame()`, `afr_fd_report_unstable_write()`, and `afr_fd_has_witnessed_unstable_write()`.

Key internal phases are `afr_changelog_pre_op()`, `afr_transaction_perform_fop()`, `afr_transaction_fop()`, `afr_changelog_post_op()`, `afr_changelog_post_op_safe()`, `afr_changelog_post_op_do()`, and `afr_transaction_done()`. Eager-lock control is concentrated in `__afr_eager_lock_handle()`, `afr_has_lock_conflict()`, `__afr_transaction_wake_shared()`, `afr_lock_resume_shared()`, and `afr_delayed_changelog_wake_up_cbk()`. Thin-arbiter handling uses `afr_ta_decide_post_op_state()`, `afr_ta_post_op_do()`, `afr_ta_process_onwireq()`, `afr_ta_process_waitq()`, and `afr_release_notify_lock_for_ta()`.

## Control Flow
A caller prepares `afr_local_t` with the FOP-specific wind/unwind callbacks and calls `afr_transaction()`. The function first checks client quorum, consistent-IO policy, and thin-arbiter quorum, then allocates transaction state via `afr_transaction_local_init()` and lock targets via `afr_transaction_lockee_init()`. Metadata transactions may trigger `afr_inode_refresh()` before starting if cached event-generation data is stale.

`afr_transaction_start()` either takes a new lock or joins an existing eager-lock owner batch. Locks are attempted non-blocking first through `afr_lock_nonblocking()` and fall back to `afr_blocking_lock()` in `afr_post_nonblocking_lock_cbk()`. Once locks are done, `afr_changelog_pre_op()` chooses locked children as `pre_op` participants, marks unlocked children failed, enforces FOP quorum, optionally writes dirty/pending xattrs, and can piggyback pre-op xdata when `pre-op-compat` is disabled.

`afr_transaction_perform_fop()` sets write-subvolume state for data writes, updates inherited pre-op state, transfers eager locks to compatible waiting transactions, temporarily adopts the original FOP frame lock owner, and calls `afr_transaction_fop()`. The FOP phase winds only to children with successful pre-op and no recorded failure. Arbiter volumes first compute pre-op sources and reject operations where the arbiter is the only source.

Callbacks mark failed children with `afr_transaction_fop_failed()` and eventually call `afr_transaction_resume()`. Resume restores the caller lock owner, treats symmetric errors as all-success when applicable, updates pre-op accounting, and enters post-op. Post-op handles quorum loss, dirty/pending xattr updates, delayed eager-lock post-op, optional fsync-before-undirty for unstable writes, thin-arbiter decision paths, unlock, final unwind, and stack destruction.

## State And Persistence
The file mutates `afr_local_t::transaction` arrays (`pre_op`, `failed_subvols`, `pre_op_sources`, `changelog_xdata`), `pending` matrices, `dirty` changelog counters, transaction lock list nodes, and `op_ret/op_errno`. It updates `afr_inode_ctx_t` state for eager-lock ownership, pre-op inheritance (`pre_op_done`, `inherited`, `on_disk`), delayed post-op timers, open/inodelk conflict avoidance, write-subvolume selection, and witnessed unstable writes.

Persistent replica state is stored as extended attributes. Per-child pending changelogs are written under `priv->pending_key[i]` with data/metadata/entry counters; dirty state is written under `AFR_DIRTY`. For entry self-heal granularity, pre/post xattrops may pass `GF_XATTROP_ENTRY_IN_KEY` or `GF_XATTROP_ENTRY_OUT_KEY`. Thin arbiter state is persisted in the thin-arbiter ID file using `syncop_xattrop()` and protected by `AFR_TA_DOM_NOTIFY` / `AFR_TA_DOM_MODIFY` inodelk domains.

## Dependencies And Integration Points
This file depends on the GlusterFS stack-wind callback model, dict/xattr APIs, timer APIs, syncop calls, inode/fd/loc lifetimes, AFR self-heal matrix helpers, lock helpers from `afr-lk-common.c`, read/write subvolume helpers, and message IDs from `afr-messages.h`. It is called by inode-write, dir-write, metadata, xattrop, fsync, and other AFR FOP implementations that populate the transaction callbacks in `afr_local_t`.

## Risks
The main risk is ordering: clearing dirty/pending xattrs before data is stable can make an inconsistent replica look trustworthy, which is why `ensure-durability` may force fsync before hard post-op. Quorum checks happen at several points; missing one can create split-brain during a network partition. Eager-lock batching is list/timer heavy and can reorder overlapping writes unless conflict detection is correct. Thin-arbiter queues rely on shared `priv` counters and event-generation validation; stale TA decisions can fail good FOPs or accept unsafe ones. Error propagation is subtle because post-op failure can overwrite the original FOP result only in specific cases.

## Test Signals
Useful tests include writes/truncates/setattrs/renames/unlinks with one or more children down, quorum-type `auto` and `fixed`, arbiter and thin-arbiter replica sets, overlapping writes under eager-lock, delayed post-op timer cancellation, pre-op compatibility on/off, optimistic changelog on/off, fsync failure after unstable writes, entry granular heal xattr behavior, metadata refresh races after child up/down events, and symmetric-error paths. Runtime signals include correct pending/dirty xattr deltas, no lock-list assertions, no leaked timers, expected quorum error codes, and self-heal discovering exactly the children marked by the transaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.h

## Purpose
`afr-transaction.h` is the public interface for AFR transaction and read-transaction support. It exposes the write transaction state machine in `afr-transaction.c`, the read transaction helpers implemented with the same transaction vocabulary, quorum helpers, delayed changelog callbacks, thin-arbiter lock-release callbacks, and small utility functions used by the rest of the AFR translator.

## Important APIs, Types, And Functions
The central declaration is `afr_transaction(call_frame_t *frame, xlator_t *this, afr_transaction_type type)`, paired with `afr_transaction_resume()` and `afr_transaction_detach_fop_frame()`. FOP implementations report child failure with `afr_transaction_fop_failed()` and may trigger locking directly through `afr_lock()`. Changelog and quorum helpers include `afr_set_pending_dict()`, `afr_txn_nothing_failed()`, `afr_has_quorum()`, `afr_needs_changelog_update()`, `afr_zero_fill_stat()`, and `afr_pick_error_xdata()`.

Read-side declarations include `afr_read_txn()`, `afr_read_txn_continue()`, `afr_pending_read_increment()`, and `afr_pending_read_decrement()`, which integrate read selection and outstanding-read load tracking with the shared AFR private state. Thin-arbiter exported callbacks are `afr_release_notify_lock_for_ta()` and `afr_ta_lock_release_done()`. `__mark_all_success()` is intentionally exposed for shared symmetric-error handling.

## Control Flow
The header is included by FOP implementation files that initialize `afr_local_t`, set transaction wind/unwind callbacks, and call the transaction engine. Write FOP callbacks use `afr_transaction_fop_failed()` before unwinding to `afr_transaction_resume()`. Read FOP paths use `afr_read_txn()` to select a readable child, wind the caller-provided read function, and continue to other candidates through `afr_read_txn_continue()` when a read fails.

## State And Persistence
This header does not define storage by itself, but every declaration operates on `afr_private_t`, `afr_local_t`, `call_frame_t`, and inode/fd state declared in `afr.h`. The APIs coordinate persistent on-disk xattrs through `dict_t` objects and expose quorum decisions based on caller-provided child-bit arrays. Pending read counters are held in `afr_private_t::pending_reads`, while delayed changelog wakeups and transaction frame detachment operate on `afr_inode_ctx_t` and `afr_local_t` lock/timer state.

## Dependencies And Integration Points
The header depends on `afr.h`, which provides transaction types, local/private structures, callback typedefs, and GlusterFS core types. It is part of the AFR internal module boundary: inode-write, dir-write, open/fsync/xattrop paths, self-heal, and read transaction code all depend on these declarations rather than duplicating transaction internals.

## Risks
Because this header exposes low-level state-machine hooks, misuse can corrupt transaction accounting. Calling `afr_transaction_resume()` without restoring proper `op_ret`, `op_errno`, and child failure bits can produce wrong post-op xattrs. Incorrect child arrays passed to `afr_has_quorum()` can grant unsafe writes. Direct use of `__mark_all_success()` must remain limited to verified symmetric-error cases, otherwise real failures would be hidden. Thin-arbiter callback signatures also rely on frame ownership conventions: destroying or reusing frames too early can break wait queue processing.

## Test Signals
Compilation across all AFR FOP modules is the first signal because this file is a shared internal ABI. Behavioral tests should cover all transaction types, read retry/load counters, explicit child failure reporting, quorum helper outcomes for even/odd replica counts, delayed changelog wakeup, and thin-arbiter notify-lock release. Header changes should trigger broad AFR regression tests because seemingly small signature or semantic changes affect most read/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.c

## Purpose
`afr.c` is the translator entry point for GlusterFS AFR/replicate. It initializes and reconfigures `afr_private_t`, parses volume options, allocates child arrays and inode tables, initializes self-heal-daemon state, exports the AFR FOP/callback/dump operation tables, and registers the translator API as `"replicate"`.

## Important APIs, Types, And Functions
Top-level translator hooks are `init()`, `fini()`, `reconfigure()`, `notify()`, and `mem_acct_init()`, all referenced from `xlator_api`. The `fops` table binds lookup, locks, statfs, inode reads, inode writes, open/opendir, directory reads, and directory writes to AFR implementations in included/adjacent modules. `cbks` supplies release, releasedir, and forget callbacks; `dumpops` exposes `afr_priv_dump()`.

Important initialization helpers are `xlator_subvolume_index()`, `fix_quorum_options()`, `afr_set_favorite_child_policy()`, `set_data_self_heal_algorithm()`, `afr_handle_anon_inode_options()`, `afr_pending_xattrs_init()`, and `afr_ta_init()`. Self-heal cleanup uses `afr_selfheal_daemon_fini()` and `afr_destroy_healer_object()`.

## Control Flow
`init()` validates that the translator has children, allocates `afr_private_t`, initializes locks and lists, counts subvolumes, parses arbiter/thin-arbiter settings, initializes read-selection and self-heal options, configures quorum, eager-lock, pre-op, durability, HALO, favorite-child, consistent-metadata/IO, anonymous inode, and changelog xattr options, and allocates arrays for children, up/down state, local flags, anonymous-inode flags, child latency, pending reads, pending keys, and last events. It then stores child pointers, creates a self-heal domain string, creates an inode table with different sizing when running as SHD, initializes the self-heal daemon if requested, and creates the local frame pool.

`reconfigure()` updates the same runtime-tunable fields from a new options dict. It resolves read-subvolume by object or index, recalculates quorum behavior, resets read-child discovery when `choose-local` changes, disables `consistent_io` if quorum is enabled, updates anonymous-inode naming, and wakes self-heal when SHD enablement or timeout changes. `fini()` tears down SHD healer threads, cancels pending parent-up timers, destroys the local mempool, frees private state via `afr_priv_destroy()`, and destroys the inode table.

## State And Persistence
The file owns allocation and option population of `afr_private_t`. Persistent translator configuration includes child count, child pointers, arbiter/thin-arbiter mode, pending xattr names, dirty xattr name, self-heal parameters, quorum mode/count, read selection policy, eager-lock/post-op delay/pre-op compatibility, HALO latency limits, consistency flags, and anonymous-inode names derived from `volume-id`. Runtime state initialized here includes child-up/halo-up arrays, latency arrays, local flags, pending-read counters, heal queues, saved locks, thin-arbiter wait/on-wire queues, event generation fields, and SHD structures.

The file itself does not write disk data. Its persistent effects are the option-selected xattr names and translator runtime structures that later transaction and self-heal code use to write trusted AFR xattrs and maintain replica consistency.

## Dependencies And Integration Points
`afr.c` includes `afr-common.c` directly, making many common helper definitions part of the same compilation unit. It depends on GlusterFS xlator APIs, option parsing macros (`GF_OPTION_INIT`/`GF_OPTION_RECONF`), memory accounting, inode-table creation, timers, thread cleanup, self-heal-daemon helpers, and all AFR FOP implementations named in the operation table. The automake build for AFR must compile this as the module entry source that exports `xlator_api`.

## Risks
Initialization has many partially allocated resources and a single `out` path; failures depend on later private cleanup to avoid leaks. Thin-arbiter setup deliberately decrements `child_count` while pending-key allocation may account for the thin-arbiter file name, so off-by-one mistakes can corrupt child arrays or pending xattr names. Quorum options override each other, and enabling quorum disables consistent-IO, so reconfiguration tests must check the final effective policy rather than raw option values. Direct inclusion of `afr-common.c` can hide symbol-boundary issues and makes compile order important.

## Test Signals
Signals include successful volume graph load with normal replica, arbiter, and thin-arbiter configurations; invalid `read-subvolume` and `read-subvolume-index` rejection; live reconfigure of quorum, eager-lock, self-heal, HALO, favorite-child, and read policies; clean translator unload without leaked timers or healer threads; correct `distribute.so`-style operation exposure through xlator API; and option table validation through Gluster volume set/get tests. SHD-specific tests should verify inode table sizing and healer object cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.h

## Purpose
`afr.h` is the primary internal header for the AFR replicate translator. It defines the global private state, per-call local state, inode and fd contexts, transaction types, lock state, reply storage, read/self-heal policy enums, thin-arbiter state enums, stack cleanup macros, utility macros, and cross-file prototypes used by AFR read, write, lock, self-heal, open, lookup, and translator lifecycle code.

## Important APIs, Types, And Functions
Key enums include `afr_read_hash_mode_t`, `afr_favorite_child_policy`, `afr_data_self_heal_type_t`, `afr_child_index`, `afr_ta_fop_state_t`, `afr_transaction_type`, `afr_fd_open_status_t`, and `afr_fop_lock_state_t`. Core structures are `afr_private_t`, `afr_local_t`, `afr_inode_ctx_t`, `afr_lock_t`, `afr_internal_lock_t`, `afr_lockee_t`, `afr_reply`, `afr_fd_ctx_t`, `afr_lk_heal_info_t`, and small split-brain/read helper argument structs.

Important macros include `AFR_COUNT`, `AFR_INTERSECT`, `AFR_CMP`, `AFR_IS_ARBITER_BRICK`, `AFR_SET_ERROR_AND_CHECK_SPLIT_BRAIN`, `AFR_ERROR_OUT_IF_FDCTX_INVALID`, `AFR_STACK_UNWIND`, `AFR_STACK_DESTROY`, `AFR_FRAME_INIT`, `AFR_STACK_RESET`, `AFR_BASENAME`, `AFR_QUORUM_AUTO`, and changelog constants such as `AFR_NUM_CHANGE_LOGS`, `AFR_DIRTY`, `AFR_TA_DOM_NOTIFY`, and `AFR_TA_DOM_MODIFY`. Inline helpers map transaction or inode type to changelog index with `afr_index_for_transaction_type()` and `afr_index_from_ia_type()`.

## Control Flow
Most AFR FOPs allocate an `afr_local_t` through `AFR_FRAME_INIT`, populate the `cont` union fields and transaction callbacks, call read/transaction/self-heal helpers, then unwind with `AFR_STACK_UNWIND` or destroy private frames with `AFR_STACK_DESTROY`. Lock paths fill `afr_internal_lock_t` and `afr_lockee_t`; transaction paths mutate the nested `transaction` member; read paths use `readable`, `read_attempted`, `read_subvol`, and `readfn`; reply interpretation uses `replies` and `afr_reply` arrays.

The private translator state (`afr_private_t`) is initialized in `afr.c`, updated by notifications/reconfigure, consulted by transaction/read/self-heal paths, and cleaned up at translator shutdown. Inode and fd contexts cache state across individual FOP frames, while `afr_local_t` represents one outstanding operation or transaction frame.

## State And Persistence
`afr_private_t` stores long-lived translator state: child count and pointers, child-up/HALO-up/local/anonymous-inode arrays, latency, pending xattr keys, self-heal queues and limits, thin-arbiter identity and queues, quorum/read/eager-lock/durability/metadata consistency options, event generation, volume UUID, SHD state, saved lock-heal queues, and anonymous-inode names. `afr_inode_ctx_t` persists per-inode read/write subvolume choices, split-brain choice, pre-op inheritance counters, eager-lock lists and timers, open fd count, refresh need, and unstable-write witness state. `afr_fd_ctx_t` persists per-fd open status by child, flags, readdir subvolume, and lock-heal information.

`afr_local_t` is per-frame but large: it stores operation identity, event-generation snapshot, child-up snapshot, readable arrays, xattr request/response dicts, pending changelog matrix, dirty counters, replies, continuation arguments for nearly every FOP, transaction fields, thin-arbiter fields, barriers, and lock-owner snapshots. Persistent on-disk representation is not defined here directly, but the constants and structures describe the trusted AFR xattr format `[data, metadata, entry]`.

## Dependencies And Integration Points
The header depends on GlusterFS core types and APIs (`call_frame_t`, `xlator_t`, `inode_t`, `fd_t`, `loc_t`, dicts, locks, timers, syncop, iatt, flock, list heads, mempools) and AFR sibling headers (`afr-mem-types.h`, `afr-self-heald.h`, `afr-messages.h`). Its prototypes connect all AFR implementation files: read subvolume selection, inode refresh, locking, fd cleanup, reply interpretation, matrix allocation, self-heal, split-brain handling, quorum, consistent IO, thin arbiter, domain locks, and private directory handling.

## Risks
This header is a dense shared contract. Layout changes in `afr_local_t`, `afr_private_t`, or inode/fd contexts can affect many asynchronous callbacks and cleanup paths. The stack macros combine unwind/destroy with local cleanup, read-counter decrement, and domain-lock release; misuse can leak locals or double-free frames. Many arrays are sized by `priv->child_count`, but thin-arbiter mode has special indexing at `THIN_ARBITER_BRICK_INDEX`; callers must not blindly iterate into thin-arbiter-only slots. The `cont` union-style struct relies on each FOP reading only its populated fields.

## Test Signals
Any change requires full AFR build coverage and broad runtime tests for read, write, metadata, entry, lock, self-heal, thin-arbiter, arbiter, split-brain, and SHD paths. Memory diagnostics should watch frame cleanup, dict refs, reply wiping, inode/fd context lifetime, and list membership assertions. ABI-like signals include every AFR source compiling without duplicate/missing prototypes and no operation table regression from signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/Makefile.am

## Purpose
This top-level DHT automake file delegates the DHT cluster translator build to the `src` subdirectory. Its complete contents are `SUBDIRS = src`, with no trailing newline in the checked file.

## Important APIs, Types, And Functions
There are no C APIs, types, functions, or build targets defined here. The only automake variable is `SUBDIRS`, which tells automake recursion to descend into `xlators/cluster/dht/src`.

## Control Flow
During an autotools build, automake processes this directory and recurses into `src` for actual target definitions. Installation, library target creation, headers, compiler flags, and unit-test conditionals are all owned by `src/Makefile.am`, not by this file.

## State And Persistence
The file has no runtime state and no generated persistent artifacts by itself. Its build-system effect is persistent only through the generated `Makefile.in`/`Makefile` recursion graph: excluding `src` here would prevent DHT translator modules from being built under this directory.

## Dependencies And Integration Points
It depends on the repository's autotools recursion model. The integration point is the child `sources/distributed-fs/glusterfs/xlators/cluster/dht/src/Makefile.am`, which defines `dht.la`, `nufa.la`, and `switch.la`.

## Risks
The main risk is accidental deletion or change of the `SUBDIRS` assignment, which would silently remove DHT translator build coverage from recursive builds. The lack of a trailing newline may trigger style or packaging warnings in some tooling, though automake can still parse the assignment.

## Test Signals
Run autoreconf/configure or the project's normal autotools build and verify that `xlators/cluster/dht/src` is entered and the DHT modules are produced. Static checks can simply assert this file contains exactly the intended `SUBDIRS = src` delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/Makefile.am

## Purpose
This automake file defines the build for GlusterFS DHT-family cluster translators: `dht.la`, `nufa.la`, and `switch.la`. It collects the common DHT source set, adds the translator-specific entry source for each module, sets compiler and include flags, links against `libglusterfs.la`, installs modules into the GlusterFS cluster xlator directory, and creates a compatibility symlink from `distribute.so` to `dht.so`.

## Important APIs, Types, And Functions
Important automake variables include `xlator_LTLIBRARIES`, `xlatordir`, `dht_common_source`, `dht_la_SOURCES`, `nufa_la_SOURCES`, `switch_la_SOURCES`, per-library `*_LDFLAGS` and `*_LIBADD`, `noinst_HEADERS`, `AM_CFLAGS`, `AM_CPPFLAGS`, `CLEANFILES`, `uninstall-local`, `install-data-hook`, and the `if UNITTEST` conditional block.

The common source list includes layout, helper, linkfile, rebalance, self-heal, rename, hash, disk-usage, common, inode read/write, shared, lock, and `libxlator.c` sources. Module-specific sources are `dht.c`, `nufa.c`, and `switch.c`. Headers include `dht-common.h`, `dht-mem-types.h`, `dht-messages.h`, `dht-lock.h`, and `libxlator.h`.

## Control Flow
Automake builds all three libtool modules from the shared source list plus one entry source. The modules use `-module` and `$(GF_XLATOR_DEFAULT_LDFLAGS)`, link to the built `libglusterfs.la`, and install into `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/cluster`. `install-data-hook` creates `distribute.so` as a symlink to `dht.so`; `uninstall-local` removes that symlink. If `UNITTEST` is enabled, coverage and xunit artifacts are added to `CLEANFILES`, while `noinst_PROGRAMS` and `TESTS` are initialized empty for this makefile.

## State And Persistence
This file has no runtime state. Build-time state consists of generated `.la`, `.so`, object, coverage, and optional test result files. Installation persists the DHT/Nufa/Switch translator modules and the legacy `distribute.so` symlink in the target xlator directory. The `DATADIR` and `LIBDIR` preprocessor defines embed configured paths into compiled code.

## Dependencies And Integration Points
It depends on GlusterFS build variables (`GF_CFLAGS`, `GF_CPPFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, `PACKAGE_VERSION`), the top-level build directory for `libglusterfs.la` and `libxlator.c`, source-tree include directories for libglusterfs, RPC XDR, RPC library, and xlator lib, and automake/libtool conventions for `xlator_LTLIBRARIES`. The source list integrates DHT code with the shared xlator support library and exposes three translator variants from the same implementation base.

## Risks
Because `dht_common_source` is shared by all three modules, adding a source or header needed by only one variant can accidentally affect all variants or fail another module's build. The compatibility symlink assumes `dht.so` exists at install time and `ln -sf` is acceptable for the target filesystem/package manager. Paths reference both top source and top build trees; generated headers or out-of-tree builds can fail if include ordering is wrong. The unit-test conditional currently declares empty test lists, so enabling `UNITTEST` here alone may not execute DHT tests.

## Test Signals
Build signals include successful out-of-tree and in-tree autotools builds of `dht.la`, `nufa.la`, and `switch.la`, correct linkage to `libglusterfs.la`, and successful install/uninstall of the `distribute.so` symlink. Packaging checks should inspect module placement under `xlator/cluster`. Developer tests should verify that changing the common source list rebuilds all three modules and that `make clean` removes coverage artifacts when `UNITTEST` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/Makefile.am -->
