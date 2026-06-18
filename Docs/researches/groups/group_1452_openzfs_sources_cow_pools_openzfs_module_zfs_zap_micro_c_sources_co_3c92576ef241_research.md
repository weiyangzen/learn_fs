# Group Research: group_1452_openzfs_sources_cow_pools_openzfs_module_zfs_zap_micro_c_sources_co_3c92576ef241

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_micro.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zap_micro.c

## Summary
Implements micro-ZAP handling: compact single-block ZAP objects, their in-memory B-tree index, conversion to fat-ZAP, byte swapping, entry insertion, and normalization-conflict checks.

## Main Responsibilities
- Computes the effective maximum micro-ZAP block size, including `large_microzap` gating.
- Byteswaps on-disk micro-ZAP blocks.
- Builds and maintains an in-memory B-tree of micro-ZAP entries keyed by hash and collision differentiator.
- Opens ZAP dmu buffers as either micro-ZAP or fat-ZAP objects.
- Creates micro-ZAP blocks and upgrades them to fat-ZAP when needed.
- Adds entries and detects Unicode normalization conflicts.

## Key APIs
- `zap_get_micro_max_size()`
- `mzap_byteswap()`
- `mzap_open()`
- `mzap_upgrade()`
- `mzap_create_impl()`
- `mze_find()`, `mze_destroy()`
- `mze_canfit_fzap_leaf()`
- `mzap_normalization_conflict()`
- `mzap_addent()`

## Important Behavior
Micro-ZAP entries are indexed in memory using only the upper 32 bits of the ZAP hash plus the on-disk `mze_cd` collision differentiator. `mze_find()` walks all same-hash entries and calls `zap_match()` to handle exact or normalized matching.

`mzap_upgrade()` copies the old micro-ZAP block, optionally changes object block size, destroys the micro index, initializes fat-ZAP state, and reinserts every micro-ZAP entry with its original collision differentiator.

`mzap_create_impl()` creates a micro-ZAP header by default, but immediately upgrades when fat-ZAP-only flags are requested.

## State and Synchronization
Most mutating operations assert the ZAP rwlock is held as writer. `mzap_open()` installs `zap_t` as the DMU buffer user and handles races by freeing the loser object if another opener already installed one.

## Risks
The upgrade path assumes reinsertion cannot fail; failure would lose entries, so it uses `VERIFY0()`. Hash/collision ordering depends on `mze_cd` matching physical storage. Large micro-ZAP support must stay aligned with block-size limits, send/receive expectations, and the `uint16_t` chunk id limit.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zap_micro.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zcp.c

## Summary
Implements the ZFS Channel Program runtime: a bounded Lua 5.2 environment that executes scripts either in syncing context or open context, converts between Lua values and nvlists, exposes ZFS modules, and enforces argument, memory, and instruction limits.

## Main Responsibilities
- Creates and configures the Lua interpreter for channel programs.
- Converts input nvlists to Lua tables and Lua return values back to nvlists.
- Installs ZFS Lua libraries under `zfs.list`, `zfs.check`, `zfs.sync`, and `zfs.get_prop`.
- Tracks current run state in the Lua registry.
- Enforces instruction and memory limits.
- Handles cleanup callbacks when Lua longjmps through C code.
- Parses callback arguments uniformly for positional and table/keyword calling forms.

## Key APIs
- `zcp_eval()`
- `zcp_run_info()`
- `zcp_parse_args()`
- `zcp_argerror()`
- `zcp_nvlist_to_lua()`
- `zcp_dataset_hold()`
- `zcp_register_cleanup()`, `zcp_deregister_cleanup()`, `zcp_cleanup()`

## Important Behavior
`zcp_eval()` builds a Lua state with a custom allocator, loads limited core Lua libraries, exposes ZFS-specific modules, compiles the user program, converts the input nvpair, and runs either through `dsl_sync_task_sig()` or an open-context dry-run transaction.

Lua-to-nvlist conversion supports nil, boolean, number, string, and nested tables up to depth 20. It detects string/number/bool key collisions such as `"1"` versus `1`.

The instruction hook checks cancellation and timeout every `zfs_lua_check_instrlimit_interval` instructions. Memory allocation switches from must-succeed setup mode to limit-enforced execution mode before calling user code.

## State and Lifetime
`zcp_run_info_t` owns the Lua state’s execution context, transaction pointer, credential reference, cleanup-handler list, output nvlist, space accounting, timeout/cancel flags, and pending zvol minor list.

## Risks
Fatal Lua errors and limit violations do not roll back work already performed in the same channel program. C callbacks that allocate temporary kernel objects must register cleanup handlers before any path that can longjmp. Numeric Lua values are converted through Lua number/integer APIs, so value-range expectations must match nvlist consumers.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_get.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zcp_get.c

## Summary
Implements the `zfs.get_prop()` Lua binding for channel programs. It retrieves user properties, system properties, user quota properties, and `written@` properties, returning value plus source.

## Main Responsibilities
- Determines dataset type as filesystem, volume, or snapshot.
- Validates whether a property applies to a dataset.
- Retrieves special in-memory or computed properties directly.
- Falls back to DSL property ZAP lookup for ordinary system properties.
- Retrieves user-defined properties.
- Retrieves kernel-only user/group quota and used properties.
- Computes `written@` values between datasets/snapshots.
- Registers `get_prop` into the ZCP Lua namespace.

## Key APIs
- `zcp_load_get_lib()`
- `prop_valid_for_ds()`
- Internal helpers: `zcp_get_prop()`, `zcp_get_system_prop()`, `zcp_get_user_prop()`, `zcp_get_written_prop()`

## Important Behavior
Special properties are handled directly for values such as `used`, `referenced`, `available`, `clones`, `type`, `name`, `mountpoint`, `volsize`, encryption state, `snapshots_changed`, counts, and receive resume tokens.

Property source reporting returns nil for readonly properties and `version`; otherwise it returns `default` for empty setpoints or the setpoint dataset name.

For all-boolean nvlist-like results, such as clone lists, conversion through ZCP can yield Lua arrays rather than key/value tables.

## State and Synchronization
Most lookups hold a `dsl_dataset_t` by name through `zcp_dataset_hold()` and release it before returning. Kernel-only quota lookup creates a transient `zfsvfs_t` around the objset to call userspace accounting helpers.

## Risks
Several errors are fatal Lua errors, while absent/inapplicable properties return no values. Temporary property lookup is kernel-only. User quota parsing accepts numeric IDs and SID-like strings and must free allocated domain strings correctly.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_get.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_global.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zcp_global.c

## Summary
Loads global errno constants into the ZCP Lua environment.

## Main Responsibilities
- Defines the errno names available to channel programs.
- Pushes each errno as a Lua global number.
- Provides the public `zcp_load_globals()` entry point.

## Key APIs
- `zcp_load_globals()`

## Important Behavior
The exported globals include common filesystem and syscall errors such as `EPERM`, `ENOENT`, `EIO`, `EACCES`, `EINVAL`, `ENOSPC`, `EROFS`, `ENOTSUP`, `EDQUOT`, and `ENAMETOOLONG`.

## Risks
The list is explicit, not generated from platform headers at runtime. Scripts can depend only on the errno names included here.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_global.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_iter.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zcp_iter.c

## Summary
Implements the `zfs.list` Lua submodule for channel programs. It returns iterator closures for children, snapshots, clones, user properties, system properties, bookmarks, and holds.

## Main Responsibilities
- Iterates clones of a snapshot.
- Iterates snapshots of a filesystem or volume.
- Iterates child datasets while skipping hidden names.
- Iterates user properties and the compatibility alias `properties`.
- Returns visible valid system-property names.
- Iterates bookmarks on a dataset.
- Iterates holds on a snapshot.
- Registers list functions and metatables into Lua.

## Key APIs
- `zcp_load_list_lib()`
- Internal iterator factories: `zcp_children_list()`, `zcp_snapshots_list()`, `zcp_clones_list()`, `zcp_user_props_list()`, `zcp_system_props_list()`, `zcp_bookmarks_list()`, `zcp_holds_list()`

## Important Behavior
Each list call validates arguments, captures an object id and serialized cursor in Lua upvalues, and returns a closure. Each invocation advances the cursor and returns the next item or no values at end.

`user_properties` materializes all properties into an nvlist and attaches a Lua `__gc` metatable so the nvlist is freed if iteration does not run to completion.

`system_properties` returns a Lua table of names for visible system properties valid for the requested dataset.

## State and Lifetime
Iterators repeatedly re-hold datasets by object id, so they tolerate object lifetime checks at each step. User property iteration stores an nvlist pointer in Lua userdata and frees it either at exhaustion or garbage collection.

## Risks
Datasets can disappear between iterator creation and iteration, producing either empty iteration or fatal errors depending on context. Cursor values are held as Lua numbers. User-property iteration depends on `fnvpair_value_nvlist()` containing `ZPROP_VALUE` and `ZPROP_SOURCE`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_iter.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_set.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zcp_set.c

## Summary
Implements channel-program support for setting user properties.

## Main Responsibilities
- Checks whether a requested property set is currently allowed.
- Restricts support to user properties.
- Applies local user-property values in syncing context.

## Key APIs
- `zcp_set_prop_check()`
- `zcp_set_prop_sync()`

## Important Behavior
`zcp_set_prop_check()` rejects non-user properties with `EINVAL`, builds a one-property nvlist, and delegates validation to `dsl_props_set_check()`.

`zcp_set_prop_sync()` obtains the current ZCP pool from `zcp_run_info()`, holds the dataset, constructs a local-source nvlist, calls `dsl_props_set_sync_impl()`, and releases the dataset.

## Risks
Only user properties are supported. `zcp_set_user_prop()` relies on `zcp_dataset_hold()` longjmp behavior for fatal dataset lookup errors, so callers must be prepared for Lua error unwinding.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_set.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_synctask.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zcp_synctask.c

## Summary
Implements ZCP `zfs.sync` and `zfs.check` submodules. It wraps selected DSL sync tasks so channel programs can dry-run or execute dataset mutations.

## Main Responsibilities
- Provides generic sync-task execution for ZCP callbacks.
- Exposes clone, destroy, promote, rollback, snapshot, rename snapshot, inherit property, bookmark, and set property operations.
- Runs checks in both dry-run and sync modes.
- Enforces sync-context requirements for actual mutation.
- Estimates per-call MOS space usage for channel-program space accounting.
- Returns error codes and optional error-detail nvlists to Lua.

## Key APIs
- `zcp_load_synctask_lib()`
- Internal wrapper: `zcp_synctask_wrapper()`
- Internal operations: `zcp_synctask_clone()`, `zcp_synctask_destroy()`, `zcp_synctask_promote()`, `zcp_synctask_rollback()`, `zcp_synctask_snapshot()`, `zcp_synctask_rename_snapshot()`, `zcp_synctask_inherit_prop()`, `zcp_synctask_bookmark()`, `zcp_synctask_set_prop()`

## Important Behavior
`zcp_sync_task()` first calls the DSL check function. In check mode it returns that result without syncing. In sync mode it requires the enclosing channel program to have been invoked with sync enabled, then calls the sync function when the check succeeds.

Operations that allocate temporary nvlists register ZCP cleanup handlers so Lua errors free them. Snapshot and clone record possible new zvol names in `zri_new_zvols` so minor nodes can be created later in open context.

## State and Synchronization
The module runs inside the transaction supplied by `zcp_eval()`. It uses `zri_space_used` plus static block-modified estimates to avoid exceeding unreserved pool space during a single program.

## Risks
Space use is an approximation based on average block shifts and triple-ditto MOS assumptions. Some operations return structured conflict details, so callers must handle a second return value. Actual `zfs.sync` calls in open-context programs are fatal Lua errors.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zcp_synctask.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfeature.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfeature.c

## Summary
Implements SPA feature-flag persistence, compatibility checks, enablement, refcount changes, and enabled-TXG tracking.

## Main Responsibilities
- Checks active feature support for read or write opens.
- Retrieves feature refcounts from the in-memory cache or MOS ZAP objects.
- Enables features and their dependencies.
- Updates feature refcounts in syncing context.
- Creates feature ZAP objects during pool creation or upgrade.
- Tracks activation/deactivation of MOS features.
- Records feature enable TXG when the `enabled_txg` feature is active.

## Key APIs
- `spa_features_check()`
- `feature_get_refcount()`
- `feature_get_refcount_from_disk()`
- `feature_sync()`
- `feature_enable_sync()`
- `spa_feature_create_zap_objects()`
- `spa_feature_enable()`
- `spa_feature_incr()`, `spa_feature_decr()`
- `spa_feature_is_enabled()`, `spa_feature_is_active()`
- `spa_feature_enabled_txg()`

## Important Behavior
Enabled features are stored in either `features_for_read` or `features_for_write` depending on readonly compatibility, plus descriptions in `feature_descriptions`. Refcount zero means enabled but inactive; nonzero means active.

`feature_enable_sync()` recursively enables dependencies, stores the description, initializes the refcount, optionally records the enabling TXG, handles encryption errata cleanup for `bookmark_v2`, and upgrades the error log when `head_errlog` is enabled.

## State and Synchronization
Refcount updates require syncing context and hold `spa_feat_stats_lock`. The in-memory `spa_feat_refcount_cache` is kept in sync with on-disk ZAP state for normal registered features.

## Risks
Feature refcounts are on-disk compatibility state; incorrect increments or decrements can make pools appear unsupported or writable when they are not. `feature_sync()` is also used by `zhack`, which can pass pseudo-features with `SPA_FEATURE_NONE`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfeature.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_byteswap.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_byteswap.c

## Summary
Provides byteswap routines for ZFS ACL and znode on-disk structures.

## Main Responsibilities
- Byteswaps old fixed `ace_t` ACL entries.
- Byteswaps modern variable-size ZFS ACE layouts.
- Byteswaps embedded ACLs inside old znode physical structures.
- Exports byteswap symbols in kernel builds.

## Key APIs
- `zfs_oldacl_byteswap()`
- `zfs_acl_byteswap()`
- `zfs_znode_byteswap()`
- Internal helpers: `zfs_oldace_byteswap()`, `zfs_ace_byteswap()`

## Important Behavior
`zfs_ace_byteswap()` supports both legacy ACE layout and ZFS ACL layout. It walks a byte buffer, swapping headers first, then chooses entry size based on flags and ACE type, with explicit overrun checks because embedded ACL buffers may be padded.

`zfs_znode_byteswap()` swaps all fixed 64-bit timestamp/stat fields and then swaps embedded ACE data based on ACL version.

## Risks
Variable-size ACE parsing is defensive but still depends on flags and type fields becoming meaningful immediately after byte swap. The old ACL path swaps the entire block because it lacks an exact ACE count.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_byteswap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_chksum.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_chksum.c

## Summary
Benchmarks checksum implementations and exposes results through a raw kstat. It also selects the fastest implementation for algorithms with multiple backends.

## Main Responsibilities
- Defines benchmark result rows for checksum implementations.
- Runs startup and full requested benchmarks over fixed block sizes.
- Benchmarks Edon-R, Skein, SHA-256, SHA-512, and BLAKE3 implementations.
- Selects fastest SHA/BLAKE backend using 256 KiB throughput.
- Installs and removes the `zfs/chksum_bench` kstat.
- Initializes/finalizes BLAKE3 per-CPU context in kernel builds.

## Key APIs
- `chksum_init()`
- `chksum_fini()`

## Important Behavior
Startup performs a lighter 256 KiB benchmark. Reading the kstat triggers `chksum_benchmark()` again for full 1 KiB through 16 MiB results, then marks benchmarking done.

Benchmarks run with preemption disabled while timing and report MiB/s. Large 4 MiB and 16 MiB tests use non-linear ABD buffers.

## State and Lifetime
Global state includes `chksum_stat_data`, `chksum_stat_cnt`, `chksum_stat_limit`, and `chksum_kstat`. Init allocates benchmark rows and installs raw kstat callbacks; fini deletes kstat and frees the rows.

## Risks
Benchmarking runs in kernel context and can consume CPU when the kstat is read. Fastest-backend selection depends on the 256 KiB benchmark, which may not match every workload.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_chksum.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_crrd.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_crrd.c

## Summary
Implements compact round-robin databases mapping timestamps to TXGs for recent, daily, and monthly history.

## Main Responsibilities
- Maintains fixed-size circular RRD arrays.
- Adds timestamp/TXG entries with overwrite-on-full behavior.
- Maintains minute, day, and month databases in one `dbrrd_t`.
- Queries closest TXG using floor or ceiling rounding.

## Key APIs
- `rrd_tail_entry()`
- `rrd_tail()`
- `rrd_len()`
- `rrd_entry()`
- `rrd_get()`
- `rrd_add()`
- `dbrrd_add()`
- `dbrrd_query()`

## Important Behavior
`rrd_add()` updates the tail entry if the timestamp matches and the new TXG is greater; otherwise it appends and advances the circular tail, moving the head when full.

`dbrrd_add()` stores at most one monthly record every 30 days, one daily record every 24 hours, or otherwise a minute-resolution record. It rejects backwards time movement by requiring nonnegative differences from the current tail.

`dbrrd_query()` queries all three databases and chooses the entry closest to the requested timestamp.

## Risks
The data is explicitly approximate. Clock jumps into the future can suppress new entries after time moves back. Query is linear over small fixed arrays rather than binary search.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_crrd.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_debug_common.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_debug_common.c

## Summary
Provides common debug-message helpers, specifically dumping an nvlist tree through `zfs_dbgmsg()`.

## Main Responsibilities
- Splits multi-line strings into individual debug messages.
- Formats an nvlist with indentation.
- Emits each formatted line through the platform debug-message backend.
- Exports the nvlist debug helper in kernel builds.

## Key APIs
- `__zfs_dbgmsg_nvlist()`

## Important Behavior
`__zfs_dbgmsg_nvlist()` first computes the formatted nvlist length with `nvlist_snprintf(NULL, 0, ...)`, allocates a buffer, formats the nvlist, then repeatedly replaces newline characters with NUL terminators and logs one line at a time.

## Risks
The line splitter modifies the formatted buffer in place. Very large nvlists allocate a contiguous buffer sized to the full formatted representation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_debug_common.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_fm.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_fm.c

## Summary
Implements ZFS fault-management ereport and resource-event generation, duplicate suppression, rate limiting, checksum-error annotation, and ereport lifecycle management.

## Main Responsibilities
- Builds ZFS FMA ereports for pool, vdev, I/O, data, device, and checksum events.
- Selects ENA values to correlate related load or logical I/O failures.
- Suppresses duplicate recent IO/data/checksum ereports.
- Rate-limits delay, deadman, and checksum events.
- Annotates checksum ereports with changed byte ranges and bit counts.
- Posts resource events for remove, autoreplace, state change, snapshots, and zvol events.
- Initializes and tears down recent-event tracking.

## Key APIs
- `zfs_ereport_post()`
- `zfs_ereport_start_checksum()`
- `zfs_ereport_finish_checksum()`
- `zfs_ereport_free_checksum()`
- `zfs_ereport_post_checksum()`
- `zfs_event_create()`
- `zfs_post_remove()`, `zfs_post_autoreplace()`, `zfs_post_state_change()`
- `zfs_ereport_init()`, `zfs_ereport_taskq_fini()`, `zfs_ereport_fini()`
- `zfs_ereport_clear()`, `zfs_ereport_is_valid()`

## Important Behavior
`zfs_ereport_start()` constructs the class, detector FMRI, common pool payload, failmode, vdev payload, parent/spare info, ZIO details, logical bookmark fields, and tuning thresholds inherited from vdev properties.

Duplicate detection stores recent event keys in both an AVL tree and a time-ordered list. Duplicates refresh their timestamp and return `EALREADY`; old entries are purged by a delayed task.

Checksum annotation compares good and bad ABD buffers, summarizes changed ranges, counts set/cleared bits, optionally embeds exact bitmasks for small corruptions, and can drop events when buffers are identical.

## State and Synchronization
Ereport construction serializes through `spa_errlist_lock`. Duplicate tracking uses `recent_events_lock`, `recent_events_tree`, `recent_events_list`, and a delayed cleaner task. Checksum reports can be attached to a logical ZIO and finished later.

## Risks
Duplicate suppression and rate limiting intentionally drop events, so diagnostics depend on retention knobs and vdev rate-limit state. Checksum annotation borrows full buffers and can allocate per-report state. Event validity filters out recovery, tryimport, inaccessible vdevs, DTL checksum reads, and bogus delay events.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_fm.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_fuid.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_fuid.c

## Summary
Implements ZFS FUID domain tables and ID translation support. It maps domain/RID identities to compact filesystem IDs, persists domain tables, and supports ACL/owner/group logging.

## Main Responsibilities
- Loads packed FUID domain tables from disk into AVL trees.
- Maintains AVL trees keyed by domain string and index.
- Syncs dirty FUID tables back to a packed nvlist object.
- Allocates new domain indexes when adding FUIDs.
- Maps FUIDs back to platform IDs.
- Tracks FUID domains and IDs created during ACL or ownership changes.
- Supports replay-time FUID reconstruction.
- Holds transaction reservations for FUID table updates.

## Key APIs
- `zfs_fuid_avl_tree_create()`
- `zfs_fuid_table_load()`
- `zfs_fuid_table_destroy()`
- `zfs_fuid_idx_domain()`
- Kernel APIs: `zfs_fuid_sync()`, `zfs_fuid_find_by_idx()`, `zfs_fuid_map_ids()`, `zfs_fuid_map_id()`, `zfs_fuid_node_add()`, `zfs_fuid_create()`, `zfs_fuid_destroy()`, `zfs_fuid_info_alloc()`, `zfs_fuid_info_free()`, `zfs_groupmember()`, `zfs_fuid_txhold()`, `zfs_id_to_fuidstr()`

## Important Behavior
The on-disk FUID table is a packed nvlist containing an array of domain records with index, domain, and offset. Loading creates two AVL indexes over the same `fuid_domain_t` nodes.

Domain index zero is the empty domain and represents ordinary POSIX IDs. New nonempty domains are added only when `addok` is true, marking `z_fuid_dirty` for later sync.

On Linux, FUID mapping is simplified: the port only supports POSIX IDs and returns the passed ID. Other platforms can use SID/kidmap support.

## State and Synchronization
Kernel state is guarded by `z_fuid_lock`. FUID tables are lazily loaded into `zfsvfs`, never remove nodes while active, and are destroyed at filesystem teardown. Temporary `zfs_fuid_info_t` structures own lists of domains and FUID log entries.

## Risks
Replay paths depend on logged FUID info matching the operations being replayed. Domain AVL nodes share ownership between two trees, so destruction releases domains from one traversal and frees nodes from the other. Non-Linux ID mapping behavior depends on platform SID/kidmap availability.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_fuid.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_impl.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_impl.c

## Summary
Provides a small registry for checksum/hash implementation backends.

## Main Responsibilities
- Defines the available implementation backend operation tables.
- Returns backend operations by algorithm name.

## Key APIs
- `zfs_impl_get_ops()`

## Important Behavior
The registry currently contains BLAKE3, SHA-256, and SHA-512 operation tables. Passing a null or empty algorithm name returns the first registered backend. Otherwise, lookup compares against each backend’s `name`.

## Risks
The function asserts on lookup assumptions and returns the matched pointer, or the terminating entry if the name is unknown. Callers are expected to request known algorithm names.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_impl.c -->