# Group Research: group_230_bcachefs_tools_sources_cow_pools_bcachefs_tools_fs_init_fs_c_sources_c65415e2a075

Repository: `/home/sansha/Github/learn_fs`  
Scope: `Docs/research_subset_a.md`  
Source tree: `sources/cow-pools/bcachefs-tools`  
Nested source commit observed: `daebabc`

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/fs.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/fs.c

Primary filesystem setup, open/start/stop, RO/RW transition, and module lifecycle implementation for bcachefs.

Key responsibilities:
- Defines module metadata, global filesystem list, sysfs kobject types, filesystem flag/write-ref string tables, and bcachefs module init/exit.
- Implements logging/printing helpers that honor mount verbosity, kernel loglevel prefixes, and optional stdio redirection.
- Maintains global lookup by filesystem UUID through `bch2_fs_list`, `__bch2_uuid_to_fs()`, and `bch2_uuid_to_fs()`.
- Owns read-only transition in `bch2_fs_read_only()` and `__bch2_fs_read_only()`:
  - Stops EC, open buckets, copygc, write buffer, discard/invalidate scheduling, and journal reclaim.
  - Flushes write buffer, key cache, btree interior updates, journal pins, and btree writes until clean.
  - Handles dead-journal shutdown by cancelling dirty btree writes.
  - Persists error counters/superblock state when shutdown is not clean.
  - Verifies clean accounting, replicas, btree cache, key cache, and write buffers when clean shutdown is expected.
- Owns emergency read-only transition through `bch2_fs_emergency_read_only()` and locked variant:
  - Halts the journal.
  - Queues async read-only work.
  - Wakes allocator waiters and RO waiters.
  - Emits the emergency sequence once.
- Owns read-write transition in `__bch2_fs_read_write()`:
  - Requires `BCH_FS_may_go_rw` and upgrade/downgrade permission.
  - Rejects RW for no alloc info, unfixed errors, unresized small image, or unmigrated default superblock.
  - Initializes RW subsystems, device allocators, write refs, journal reclaim, write buffer, copygc, reconcile, discard/invalidate/stripe-delete repair work, journal scrub repairs, and btree bitmap GC scheduling.
- Provides `bch2_fs_init_rw()` to allocate RW workqueues and initialize RW btree, write IO, journal, VFS, reclaim, write buffer, copygc, and reconcile state.
- Implements filesystem allocation/free/stop/exit:
  - `bch2_fs_init()` initializes early subsystem state, superblock-derived options, devices, btree/journal/data/VFS subsystems, Unicode/casefolding, journal entry reservations, and sysfs exposure.
  - `bch2_fs_stop()` serializes shutdown, transitions RO, stops READ refs, unlinks devices, removes sysfs/debug/chardev state, drains btree reads and interior update work, and reports shutdown error categories.
  - `bch2_fs_exit()` combines stop and free.
- Handles mount-time version/option setup in `bch2_fs_opt_version_init()`:
  - Converts `norecovery` into a limited read-only/nochanges mode.
  - Enables fsck for journal rewind.
  - Sets upgrade/downgrade permission when safe.
  - Logs non-default mount options, features, devices, and incompatible-version allowance.
  - Imports required recovery passes from the superblock.
  - Schedules topology/backpointer repair for topology errors and too-small `extent_bp_shift`.
  - Rejects unsupported initialized filesystems missing `new_extent_overwrite` or with too-old `version_min`.
- Handles metadata version upgrades/downgrades through `check_version_upgrade()` and downgrade helpers.
- Starts a filesystem through `bch2_fs_start()` / `__bch2_fs_start()`:
  - Adds online devices to allocator state.
  - Checks degraded/missing-device policy.
  - Initializes reconcile and late counters.
  - Requests no-superblock-user-data-replicas incompat feature.
  - Pre-initializes RW resources if recovery will go RW.
  - Runs recovery or new filesystem initialization.
  - Transitions to final read-only or read-write state according to mount options.
- Implements device missing/degraded checks via `bch2_fs_may_start()` and `bch2_missing_devs_to_text()`.
- Implements resize-on-mount for devices with `resize_on_mount`, updating member fields, clearing `small_image`, writing the superblock, and resizing allocation metadata if initialized.
- Opens devices and chooses the best superblock in `__bch2_fs_open()`:
  - Reads all supplied superblocks.
  - Picks highest sequence/write-time superblock.
  - Filters removed/splitbrain devices.
  - Allocates the filesystem object.
  - Optionally starts it.
  - Logs initialization/startup messages.
- Defines global module init/exit:
  - Initializes dirent code, global kobject, lock graph, key cache, chardev, VFS, and debug.
  - Exposes debug static-key module parameters.

Important interactions:
- Coordinates almost every major subsystem: allocator, btree, journal, data IO, EC, copygc, reconcile, snapshots, subvolumes, quota, VFS, sysfs, chardev, debug, superblock IO, downgrade/upgrade, and recovery passes.
- `go_rw_in_recovery()` from `passes.h` determines whether RW resources are preloaded during recovery.
- `bch2_fs_recovery()` and `bch2_fs_initialize()` are invoked from startup after options and device availability checks.
- Journal clean/dirty state drives clean shutdown validation and read-only behavior.
- Device IO refs protect devices during mount-time resize, journal allocation, and startup/shutdown.

Notable invariants:
- New foreground writes are blocked before write refs are stopped during RO transition.
- Clean shutdown requires no journal error, no filesystem error, replay done, clean superblock, no dirty btree/key-cache/write-buffer state, and clean accounting/replicas refs.
- RW transition is forbidden before `BCH_FS_may_go_rw`.
- `set_may_go_rw` recovery pass must not be excluded.
- `small_image` and `no_default_sb` force or preserve read-only behavior until fixed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/fs.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/fs.h

Public lifecycle header for filesystem superblock/open/start/stop and RO/RW operations.

Key contents:
- Defines `KTYPE(type)`, a helper macro for constructing kobject type metadata from local release/sysfs/files symbols.
- Declares string tables:
  - `bch2_fs_flag_strs`
  - `bch2_write_refs`
  - `bch2_dev_read_refs`
  - `bch2_dev_write_refs`
- Declares the global open-filesystem list and lock:
  - `bch2_fs_list`
  - `bch2_fs_list_lock`
- Declares UUID lookup:
  - `__bch2_uuid_to_fs()`
  - `bch2_uuid_to_fs()`
- Declares emergency and normal RO/RW transitions:
  - `bch2_fs_emergency_read_only()`
  - `bch2_fs_emergency_read_only_locked()`
  - `bch2_fs_read_only()`
  - `bch2_fs_read_write()`
  - `bch2_fs_read_write_early()`
  - `bch2_fs_init_rw()`
- Declares resize-on-mount, missing-device formatting, lifecycle start/stop/exit, and open:
  - `bch2_fs_resize_on_mount()`
  - `bch2_missing_devs_to_text()`
  - `bch2_fs_start()`
  - `bch2_fs_stop()`
  - `bch2_fs_exit()`
  - `bch2_fs_open()`

Role:
- This is the cross-subsystem API for mounting/opening, startup, shutdown, read-only emergency handling, and RW enabling.
- Included by recovery, journal, and other subsystems that need to force RO, start RW early, or inspect lifecycle state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/passes.c

Recovery-pass registry, scheduler, persistent superblock tracking, rewind support, and async online pass executor.

Key responsibilities:
- Builds `bch2_recovery_passes[]` from `BCH_RECOVERY_PASSES()`.
- Maintains bidirectional mappings between current in-memory pass enum indices and stable persistent pass IDs:
  - `bch2_recovery_passes_to_stable()`
  - `bch2_recovery_passes_from_stable()`
- Implements superblock field operations for `recovery_passes`:
  - Validation is currently a no-op.
  - Text formatting prints pass name, last run timestamp, runtime, and no-ratelimit flag.
- Resizes/accesses the superblock recovery-pass metadata section with `bch2_sb_recovery_pass_entry()`.
- Marks pass completion in `bch2_sb_recovery_pass_complete()`:
  - Clears the stable pass bit from `ext->recovery_passes_required`.
  - Clears silent error masks when no current pass set remains.
  - Records last run time and runtime.
  - Clears the no-ratelimit bit.
  - Writes the superblock.
- Provides recovery-pass ratelimit checks based on prior runtime versus time since last run.
- Defines a fake empty pass so `scan_for_btree_nodes` is not index zero.
- Defines `bch2_lookup_root_inode()` to force root inode readability while recovery can still rewind.
- Builds the executable `recovery_passes[]` table from the macro in `passes_format.h`, including function pointer, name, flags, and dependencies.
- Provides pass-set helpers:
  - `bch2_recovery_passes_match()` returns all passes with matching flags.
  - `bch2_fsck_recovery_passes()` returns fsck pass mask.
  - `pass_dependents()` computes transitive dependents.
  - `recovery_pass_should_defer()` tests if a pass and its scheduled dependents are all online-capable.
- Implements explicit pass scheduling and recovery rewind:
  - `__bch2_run_explicit_recovery_pass()` schedules persistent or ephemeral passes.
  - Refuses to rewind to a pre-`set_may_go_rw` pass after RW is already allowed.
  - During recovery, can add a pass to `current_passes` and return `restart_recovery` when rewinding is needed.
  - Online passes may be scheduled asynchronously.
  - `bch2_require_recovery_pass()` returns success if a pass recently ran, otherwise schedules it and reports that it will run.
- Executes passes:
  - `bch2_run_recovery_pass()` logs non-silent passes, calls the pass function, tracks failing passes, records completion, and flushes the journal at the higher loop level.
  - `bch2_run_recovery_passes()` runs the current bitmask in order, handles rewinds, tracks completed/failing/pass_done, and wakes copygc/reconcile after snapshot checking has passed.
- Runs async online passes through `bch2_async_recovery_passes_work()` and `bch2_run_async_recovery_passes()`, protected by `c->writes` and `recovery.run_lock`.
- Computes startup pass set in `bch2_run_recovery_passes_startup()`:
  - Always/unclean/fsck/option/superblock-required passes.
  - Honors `recovery_pass_last` and exclude masks, except `set_may_go_rw`.
  - Defers eligible online passes when not in fsck.
  - Clears `BCH_FS_in_recovery` after synchronous startup passes.
- Formats recovery pass status in `bch2_recovery_pass_status_to_text()`.
- Initializes recovery pass state locks/work item in `bch2_fs_recovery_passes_init()`.

Important interactions:
- Pass definitions come from `passes_format.h`.
- Pass functions are implemented across allocation, btree, snapshots, fsck, journal, logged ops, reconcile, and initialization subsystems.
- Persistent required passes live in superblock `ext->recovery_passes_required` using stable IDs.
- Ephemeral scheduled passes live in `c->recovery.scheduled_passes_ephemeral`.
- Journal flushing after each pass persists repairs and ordering.

Notable details:
- `scan_for_btree_nodes` is intentionally never scheduled persistently; `check_topology` invokes it when needed.
- Passes that fail are suppressed for the current run until another pass succeeds.
- Online deferral is dependency-aware: a pass is deferred only if all scheduled dependents can also run online.
- `bch2_recovery_pass_set_no_ratelimit()` currently calls `SET_BCH_RECOVERY_PASS_NO_RATELIMIT(e, false)`, matching the completion path’s clear behavior; its name suggests this is worth verifying against macro semantics or intended behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/passes.h

Public API for recovery-pass metadata, scheduling, cancellation checks, and status formatting.

Key contents:
- Declares `bch2_recovery_passes[]` and `bch_sb_field_ops_recovery_passes`.
- Declares stable-ID conversion:
  - `bch2_recovery_passes_to_stable()`
  - `bch2_recovery_passes_from_stable()`
- Declares fsck pass mask helper `bch2_fsck_recovery_passes()`.
- Declares `bch2_recovery_pass_set_no_ratelimit()`.
- Defines explicit-pass flags:
  - `RUN_RECOVERY_PASS_nopersistent`
  - `RUN_RECOVERY_PASS_ratelimit`
- Defines `go_rw_in_recovery()`:
  - Allows early RW during recovery when upgrade/downgrade is allowed and one of several conditions holds: journal keys exist, not read-only, unclean fs, explicit recovery passes, or fsck with alloc info available.
- Defines `recovery_pass_will_run()` to test if a pass is in the active recovery pass mask.
- Defines `bch2_recovery_cancelled()`:
  - Returns `erofs_recovery_cancelled` if filesystem is going RO.
  - Returns `recovery_cancelled` if a kthread should stop.
- Declares pass scheduling/execution APIs:
  - `bch2_recovery_pass_want_ratelimit()`
  - `__bch2_run_explicit_recovery_pass()`
  - `bch2_run_explicit_recovery_pass()`
  - `bch2_require_recovery_pass()`
  - `bch2_recovery_passes_match()`
  - `bch2_run_async_recovery_passes()`
  - `bch2_run_recovery_passes()`
  - `bch2_run_recovery_passes_startup()`
- Declares status formatter and initializer.

Role:
- Shared contract between recovery, fsck checks, allocation checks, journal replay, and mount/startup code for requesting or observing recovery passes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes_format.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/passes_format.h

Canonical recovery-pass declaration file and on-disk format definitions.

Key contents:
- Defines pass behavior flags:
  - `PASS_SILENT`
  - `PASS_FSCK`
  - `PASS_UNCLEAN`
  - `PASS_ALWAYS`
  - `PASS_ONLINE`
  - `PASS_ALLOC`
  - `PASS_NODEFER`
  - `PASS_FSCK_ALLOC`
  - `PASS_FSCK_DEBUG`
- Defines `BCH_RECOVERY_PASSES()` as the single ordered x-macro source for:
  - In-memory enum order.
  - Stable persistent IDs.
  - Execution flags.
  - Dependency masks.
  - Human-readable descriptions.
- The macro explicitly warns that passes may be reordered, but the second field is a persistent ID and must never change.
- Recovery pass list includes:
  - Topology and btree scanning: `scan_for_btree_nodes`, `check_topology`.
  - Accounting/allocator bootstrap: `accounting_read`, `alloc_read`, `check_allocations`, `trans_mark_dev_sbs`, `fs_journal_alloc`, `set_may_go_rw`, `journal_replay`.
  - Allocation consistency: `check_alloc_info`, `check_lrus`, `check_btree_backpointers`, `check_backpointers_to_extents`, `check_extents_to_backpointers`, `check_alloc_to_lru_refs`, `fs_freespace_init`, `bucket_gens_init`.
  - Snapshot/subvolume repair: `reconstruct_snapshots`, `delete_dead_interior_snapshots`, `check_snapshot_trees`, `check_snapshots`, `check_subvols`, `check_subvol_children`, `delete_dead_snapshots`, `fs_upgrade_for_subvolumes`.
  - File metadata fsck: `check_inodes`, `check_extents`, `check_indirect_extents`, `check_dirents`, `check_xattrs`, `check_root`, `check_unreachable_inodes`, `check_subvolume_structure`, `check_directory_structure`, `check_nlinks`.
  - Reconcile/logged/background work: `check_reconcile_work`, `resume_logged_ops`, `delete_dead_inodes`.
  - One-time/migration/maintenance passes: `kill_i_generation_keys`, `fix_reflink_p`, `set_fs_needs_reconcile`, `btree_bitmap_gc`, `lookup_root_inode`.
- Defines `enum bch_recovery_pass` from current ordered passes.
- Defines `enum bch_recovery_pass_stable` from stable pass IDs.
- Defines persistent metadata:
  - `struct recovery_pass_entry` with `last_run`, `last_runtime`, and `flags`.
  - `BCH_RECOVERY_PASS_NO_RATELIMIT` bit in entry flags.
  - `struct bch_sb_field_recovery_passes`.
  - `recovery_passes_nr_entries()` helper.

Role:
- This file is the recovery-pass schema: changing it affects mount/recovery ordering and persistent superblock interpretation.
- Descriptions are detailed enough to serve as operator-facing or documentation text for what each pass repairs/checks.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/passes_types.h

Recovery-pass runtime state structure.

Key contents:
- Defines `struct bch_fs_recovery` with:
  - `scheduled_passes_ephemeral`: non-superblock scheduled passes.
  - `current_passes`: active pass bitmask.
  - `current_pass`: currently running pass.
  - `rewound_from` / `rewound_to`: recovery rewind tracking.
  - `pass_done`: highest pass completed without rewinds.
  - `passes_complete`: passes actually run.
  - `passes_failing`: passes currently failing and suppressed for this iteration.
  - `passes_ratelimiting`: passes delayed due to prior runtime.
  - `lock`: spinlock for pass state.
  - `run_lock`: mutex serializing pass runs.
  - `work`: async online recovery-pass work item.

Role:
- Embedded in `struct bch_fs`.
- Used by `passes.c`, `recovery.c`, fsck/repair callers, and status reporting to coordinate startup and online recovery work.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/passes_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/progress.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/progress.c

Simple mount/recovery progress indicator implementation for btree iteration workloads.

Key responsibilities:
- `bch2_progress_init()`:
  - Clears indicator state.
  - Stores stripped message prefix.
  - Sets first print time to 10 seconds in the future.
  - Estimates total nodes using disk accounting for selected leaf and inner btree masks.
  - Uses metadata replica count and btree node size to estimate nodes when upgraded accounting counters are missing.
- `progress_update_p()`:
  - Prints at most once every 10 seconds.
- `bch2_progress_update_iter()`:
  - Checks for recovery cancellation.
  - Extracts current btree node from the iterator path.
  - Counts a node when it advances past the previous `bbpos`.
  - Emits progress through `bch_info()` if not silent and the interval elapsed.
- `bch2_progress_to_text()`:
  - Formats percentage, nodes seen/total, and current `bbpos`.

Important interactions:
- Reads accounting via `bch2_accounting_mem_read()`.
- Uses btree iterator/path internals to determine the current node.
- Uses `bch2_recovery_cancelled()` so long-running passes stop promptly during RO/shutdown.
- Intended for older or mount-time code paths that cannot yet report progress through richer userspace mechanisms.

Notable behavior:
- Total node count is explicitly approximate because node replica counts may vary.
- Missing/unupgraded accounting degrades to a disk-sector-based estimate or zero rather than using misleading totals.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/progress.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/progress.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/progress.h

Header for lightweight recovery/mount progress indicators.

Key contents:
- Includes `btree/bbpos_types.h`.
- Documents that these indicators are a fallback because dmesg output is spammy and userspace/thread-with-file reporting is preferred.
- Defines `struct progress_indicator`:
  - Message string.
  - Current `bbpos`.
  - Next print jiffies.
  - Nodes seen/total.
  - Last btree node.
  - Silent flag.
- Declares:
  - `bch2_progress_init()`
  - `bch2_progress_update_iter()`
  - `bch2_progress_to_text()`

Role:
- Shared utility for recovery/fsck passes that walk btrees and need coarse progress reporting during mount or non-interactive contexts.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/progress.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/recovery.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/recovery.c

Main recovery orchestration for existing filesystems, journal replay, journal rewind, btree root loading, allocation reconstruction, and new filesystem initialization.

Key responsibilities:
- Handles btree data-loss reporting in `bch2_btree_lost_data()`:
  - Marks `ext->btrees_lost_data`.
  - Schedules topology and allocation repair passes.
  - Silences expected follow-on fsck errors.
  - Schedules btree-specific passes for alloc, backpointers, need_discard, freespace, bucket_gens, lru, accounting, snapshots, or generic topology scan.
- Provides `kill_btree()` to mark a root dead and remove matching journal keys.
- Implements `bch2_reconstruct_alloc()` for `-o reconstruct_alloc` and no-alloc-info recovery:
  - Schedules allocation-related recovery passes.
  - Silences expected allocation/accounting/backpointer/LRU errors.
  - Clears alloc-info compatibility and no-alloc-info feature.
  - Writes the superblock.
  - Kills allocation-related btrees so they are rebuilt.
- Provides `bch2_ignore_journal_rewind_errors()` to silence expected stale allocation/backpointer/accounting errors after rewind.
- Implements `bch2_set_may_go_rw()`:
  - Seals the journal replay key buffer by moving its gap to the end.
  - Sets `BCH_FS_may_go_rw`.
  - Reconstructs alloc info if needed and starts early RW if recovery requires it.
- Implements journal replay:
  - `bch2_journal_replay_accounting_key()` replays accounting deltas first, accumulating against existing accounting keys and preserving original journal sequence for non-allocated keys.
  - `bch2_journal_replay_key()` replays regular keys, handles missing depth during scan recovery, uses cached iterators for alloc leaf keys, disables key-cache coherency for other early replay paths, and stages accounting keys separately.
  - `bch2_journal_replay()`:
    - Logs replay range and key count.
    - Replays accounting keys before write buffer flush can apply accounting.
    - Tries sorted-order replay for locality.
    - Falls back to journal-order replay for keys that cannot be replayed in the fast path.
    - Releases replay pins as journal-order replay progresses.
    - Drops initial journal keys when retention is not requested.
    - Marks replay done and flushes repair-created entries immediately.
- Implements early journal replay of roots/usage/blacklist/clock entries:
  - `journal_replay_entry_early()`
  - `journal_replay_early()`
- Implements `read_btree_roots()`:
  - Reads all alive roots.
  - Records fsck errors for invalid or unreadable roots.
  - Allows reconstructable btrees to continue.
  - Allocates fake roots for missing core btrees.
- Implements `__bch2_fs_recovery()`:
  - Reads clean superblock section for clean shutdowns or reads journal for unclean/retained/rewind/scrub modes.
  - Resumes journal position from member info.
  - Verifies clean superblock against journal if needed.
  - Handles dirty-with-no-journal cases and clean-section fallback.
  - Sets journal replay start/end.
  - Runs early journal replay.
  - Performs resize-on-mount.
  - Forces read-only for unresized image or missing default superblock layout.
  - Reconstructs alloc info for no-alloc-info RW mount or dangerous reconstruct option.
  - Adds and rereads rewind ranges for journal rewind.
  - Disables fix modes that require alloc info when alloc info is unavailable.
  - Skips/blacklists post-crash journal sequences after unclean shutdown.
  - Starts the journal.
  - Advances encrypted key version after unclean shutdown.
  - Sorts journal keys and reads btree roots.
  - Sets `BCH_FS_btree_running`.
  - Runs option hooks and upgrade extra setup.
  - Optionally scrubs recent journal entries and converts detected flush/FUA failure into journal rewind + fsck.
  - Runs startup recovery passes.
  - Sets final recovery flags, flushes async node rewrites, persists repairs, optionally reruns fsck in debug builds, reads quotas, clears superblock error/lost-data markers after successful fsck, GCs blacklist entries, sets `no_stale_ptrs` compatibility when eligible, triggers dead snapshot deletion, and runs replicas accounted GC.
- `bch2_fs_recovery()` wraps recovery with fsck-error flushing and emergency RO on failure.
- `bch2_fs_initialize()` creates a new filesystem:
  - Marks new-fs and compatibility bits.
  - Applies version upgrade if enabled.
  - Marks members pre-usage/freespace-uninitialized.
  - Allocates fake roots.
  - Marks superblock/journal regions.
  - Starts journal at sequence 1.
  - Enables RW/replay path.
  - Initializes subvolumes and snapshots.
  - Creates root inode and `lost+found`.
  - Marks all recovery passes done.
  - Wakes copygc/reconcile.
  - Reads quotas if enabled.
  - Flushes first journal entry.
  - Advances rewind limit beyond initialization entries.
  - Marks superblock initialized and dirty, clears silent errors and required passes, and writes superblock.

Important interactions:
- Central bridge between journal read/replay, btree topology, fsck pass scheduling, allocation reconstruction, quota, snapshots, superblock clean fields, and RO/RW transition.
- Calls `bch2_fs_read_write_early()` from recovery after `set_may_go_rw`.
- Uses `bch2_journal_add_rewind_range()` and `bch2_journal_reread_for_rewind()` for rewind support.
- Relies on `passes.c` to execute ordered repair/check passes.

Notable invariants:
- Journal keys must be sorted before btree-root reading and normal replay.
- Early root/blacklist/clock journal entries must be replayed before btree roots are read.
- After recovery passes, `BCH_FS_may_go_rw` is set even if journal replay did not run, to leave the filesystem in a coherent post-recovery state.
- Initialization disallows rewind into initial journal entries.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/recovery.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/init/recovery.h

Public recovery orchestration header.

Key contents:
- Declares btree lost-data handling:
  - `bch2_btree_lost_data()`
- Declares journal rewind error-silencing helper:
  - `bch2_ignore_journal_rewind_errors()`
- Declares recovery/RW/journal replay entry points:
  - `bch2_set_may_go_rw()`
  - `bch2_journal_replay()`
- Declares filesystem recovery and new-filesystem initialization:
  - `bch2_fs_recovery()`
  - `bch2_fs_initialize()`

Role:
- Consumed by filesystem startup, pass scheduling, journal-related repair code, and btree error paths that need to request recovery or report lost btree data.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/init/recovery.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/init.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/init.c

Journal allocation, startup/shutdown, per-device journal initialization, and journal workqueue/buffer lifecycle.

Key responsibilities:
- Allocates additional journal buckets on a device:
  - `bch2_set_nr_journal_buckets_iter()` allocates buckets transactionally, marks them as journal metadata, inserts them into the device journal bucket ring near `discard_idx`, writes the superblock, and commits in-memory bucket/sequence/index updates under journal lock.
  - On failure after partial allocation, marks new buckets free and releases open buckets.
  - `bch2_set_nr_journal_buckets_loop()` repeats allocation until requested count is reached, with disk reservation for non-new filesystems.
  - `bch2_set_nr_journal_buckets()` is the public runtime resize entry and refuses removed devices.
- Deletes a journal bucket in `bch2_dev_journal_bucket_delete()`:
  - Finds bucket position.
  - Writes updated superblock bucket list.
  - Adjusts journal indices and arrays under journal lock.
  - Recomputes available space.
- Allocates default journal space:
  - `bch2_dev_journal_alloc()` skips devices that disallow journal data, rejects unresized small images, computes default as 1/128 device clamped by minimum and RAM/bucket size, and allocates.
  - `bch2_fs_journal_alloc()` ensures each online member has journal buckets.
- Stops journal writes to a device:
  - `bch2_journal_writing_to_device()` scans in-flight journal buffers for device references.
  - `bch2_dev_journal_stop()` waits until no in-flight journal write targets the device and cancels its discard work.
- Stops filesystem journal in `bch2_fs_journal_stop()`:
  - Stops reclaim.
  - Flushes all pins.
  - Writes metadata journal entry to synchronize clock hands.
  - Quiesces shutdown until write completion bookkeeping drains.
  - Cancels delayed write work.
  - Clears running flag if no journal error.
- Starts journal in `bch2_fs_journal_start()`:
  - Advances `cur_seq` beyond blacklisted sequences.
  - Allocates and initializes pin FIFO sized for replay window plus safety margin.
  - Initializes replay sequence, on-disk sequence, flushed sequence, pin front/back, atomic seq, and in-flight FIFO alignment.
  - Marks unreplayed pin entries.
  - Loads journal replay entries into pin lists, computes replicas from read pointers, validates superblock replica markings, and refs replica entries.
  - Tracks last empty sequence.
  - Initializes reservation index and reclaims referenced replicas.
- Marks replay done in `bch2_journal_set_replay_done()`:
  - Recomputes space.
  - Sets need-flush-write, running, and replay-done flags in the required order.
- Per-device lifecycle:
  - `bch2_dev_journal_init_early()` initializes discard lock/work.
  - `bch2_dev_journal_init()` reads journal bucket lists from v1 or v2 superblock fields, allocates `bucket_seq`, initializes bioset, and expands v2 ranges into the bucket array.
  - `bch2_dev_journal_exit()` frees bioset and arrays.
- Filesystem journal lifecycle:
  - `bch2_fs_journal_init_early()` initializes locks, delayed work, waitqueues, reclaim lock, lockdep map, and closed reservation state.
  - `bch2_fs_journal_init()` allocates free journal buffer, in-flight FIFO storage, journal write workqueue, and discard workqueue.
  - `bch2_fs_journal_exit()` destroys workqueues, frees early entries and rewind ranges, frees leftover in-flight buffers on error paths, and frees pin/free-buffer storage.

Important interactions:
- Journal bucket allocation uses allocator foreground APIs and btree transactional metadata marking.
- Superblock journal fields are updated through `bch2_journal_buckets_to_sb()` and `bch2_write_super()`.
- Startup depends on replay entries from `journal/read.c`.
- Shutdown depends on reclaim and journal write completion logic.
- Replica refs for journal entries integrate with allocation/accounting correctness.

Notable invariants:
- Journal bucket count reduction is not supported by `bch2_set_nr_journal_buckets_loop()` except explicit delete path.
- `bch2_fs_journal_start()` refuses sequence overflow and prevents reuse of blacklisted sequences.
- Pin FIFO front/back must align to journal sequence numbers.
- `JOURNAL_running` is not set until replay completion via `bch2_journal_set_replay_done()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/init.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/init.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/init.h

Public journal allocation and lifecycle header.

Key contents:
- Declares journal bucket management:
  - `bch2_set_nr_journal_buckets()`
  - `bch2_dev_journal_bucket_delete()`
- Declares allocation helpers:
  - `bch2_dev_journal_alloc()`
  - `bch2_fs_journal_alloc()`
- Declares shutdown/startup helpers:
  - `bch2_dev_journal_stop()`
  - `bch2_fs_journal_stop()`
  - `bch2_fs_journal_start()`
  - `bch2_journal_set_replay_done()`
- Declares per-device lifecycle:
  - `bch2_dev_journal_exit()`
  - `bch2_dev_journal_init_early()`
  - `bch2_dev_journal_init()`
- Declares filesystem journal lifecycle:
  - `bch2_fs_journal_exit()`
  - `bch2_fs_journal_init_early()`
  - `bch2_fs_journal_init()`

Role:
- Used by filesystem init/recovery/pass code and device management to allocate, start, stop, and tear down journal state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/init.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/journal.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/journal.c

Core journal reservation, entry lifecycle, flushing, blocking, rewind metadata, stuck detection, and debug formatting implementation.

Key responsibilities:
- Contains extensive embedded documentation describing:
  - Journal as write-ahead log for metadata btree updates.
  - Variable-sized `jset` entries and typed subentries.
  - Ring-buffer bucket layout across devices.
  - Dirty/open journal entry tracking through pins.
  - Journal space pressure and reclaim behavior.
  - Flush versus no-flush writes.
  - Recovery, clean shutdown, sequence blacklisting, user-facing options, and replication.
- Tracks open/closed journal entry state and unwritten entry counts.
- Formats journal buffers and in-flight buffers for debug output.
- Detects stuck journal conditions in `journal_error_check_stuck()`:
  - Only for journal-full or pin-full under reclaim watermark.
  - Requires no unwritten entries and no discard ability.
  - Emits debug state and forces emergency read-only.
- Finalizes journal buffer refs in `bch2_journal_buf_put_final()`:
  - Drops pin-list refs.
  - Updates last sequence.
  - Starts writes if needed.
  - Wakes waiters.
- Closes journal entries in `__journal_entry_close()`:
  - Atomically transitions reservation state to closed/error.
  - Writes final `u64s`, computes dirty bytes and sectors.
  - Validates entry did not overrun reserved space.
  - Sets `last_seq` just before opening the next entry to preserve pin ordering semantics.
  - Cancels delayed write work, recomputes space, and drops the opening pin reference.
- Halts journal through `bch2_journal_halt_locked()` / `bch2_journal_halt()`, closing current entry with error value and recording `err_seq`.
- Provides close wrappers:
  - `bch2_journal_entry_close_locked()`
  - `bch2_journal_entry_close()`
- Opens a new journal entry in `journal_entry_open()`:
  - Rejects blocked/error/full states, pin FIFO full, in-flight FIFO full, max-open limit, sequence overflow, blacklisted next sequence, and missing free buffer.
  - Computes current entry capacity from sectors and reserved overhead.
  - Allocates pin and in-flight FIFO slots.
  - Claims preallocated buffer.
  - Initializes `jset` header, sequence, ring fastpath slot, early journal entries, and reservation state.
  - Arms delayed flush work and wakes waiters/reclaim.
- Quiesces journal:
  - `bch2_journal_quiesce()` waits until `seq == seq_ondisk`.
  - `bch2_journal_shutdown_quiesce()` waits for flushed bookkeeping when healthy, or regular seq-on-disk when in error state.
- Implements auto-commit delayed work through `bch2_journal_write_work()`.
- Maintains preallocated free buffer through `journal_buf_prealloc()`.
- Implements slowpath journal reservation in `__journal_res_get()` and `bch2_journal_res_get_slowpath()`:
  - Rechecks fast path.
  - Opens/closes entries as needed.
  - Grows desired buffer size when current buffer fills before disk capacity.
  - Tracks blocked time stats for journal blocked, max in-flight, max open, full, pin full, buffer ENOMEM, and stuck.
  - Directly invokes reclaim when journal is full/pin-full and caller can block.
  - Emits debug after long waits.
- Resizes reserved per-entry space with `bch2_journal_entry_res_resize()`.
- Implements flush APIs:
  - `bch2_journal_flush_seq_async()` waits for or forces a flush for a sequence, handles already-flushed and error states, skips no-flush entries, opens an empty flush entry when needed, sets `must_flush`, and closes entries to trigger writes.
  - `bch2_journal_flush_seq()` synchronously waits and logs after 10 seconds.
  - `bch2_journal_flush_async()` and `bch2_journal_flush()` provide convenience wrappers.
- Implements metadata flush:
  - `__bch2_journal_meta()` writes an empty must-flush metadata entry.
  - `bch2_journal_meta()` wraps it in a filesystem write ref.
- Implements rewind metadata:
  - `bch2_journal_advance_rewind_seq()` advances rewind discard safety limit.
  - `bch2_journal_add_rewind_range()` records an in-memory rewind range and stages a `BCH_JSET_ENTRY_rewind` early journal entry.
- Implements `bch2_journal_noflush_seq()` to mark unwritten entries in a range as no-flush when feature is enabled and no flush has already crossed the range.
- Blocks/unblocks journal:
  - `bch2_journal_block()` marks open entry blocked, quiesces writes, and prevents new reservations.
  - `bch2_journal_unblock()` restores saved entry offset and wakes waiters.
- Supports write-buffer flushing through `bch2_next_write_buffer_flush_journal_buf()`, optionally blocking an open entry until outstanding refs drain.
- Formats complete journal debug state through `__bch2_journal_debug_to_text()` and `bch2_journal_debug_to_text()`.

Important interactions:
- Reservation fast path is shared with inline helpers in `journal.h`.
- Actual journal writes and space accounting are in `journal/write.c` and `journal/reclaim.c`.
- Emergency RO path calls back into `init/fs.c`.
- Rewind entries are consumed by `journal/read.c` and recovery.
- Write-buffer flush integration coordinates journal ordering with btree write buffer state.

Notable invariants:
- Sequence numbers are monotonic and blacklisted sequences must not be reused.
- Reservation ring slot must be published before reservation counter state changes.
- `last_seq` is set at entry close, before the next entry opens, to preserve crash replay guarantees.
- In error state, flush waiters for not-yet-flushed sequences return an error instead of waiting forever.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/journal.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/journal.h

Core journal API and inline hot-path helpers for reservations, entries, flushing, blocking, and debug.

Key contents:
- Large design comment explaining:
  - Journal purpose as btree update log.
  - Persistence behavior for synchronous/asynchronous metadata updates.
  - `jset` entry structure and sequence numbers.
  - Ring-buffer bucket layout.
  - Dirty/open journal entry tracking through `last_seq`, per-device bucket seqs, and pin refs.
  - Journal-full handling through dirty btree flushing.
- Provides basic state helpers:
  - `journal_wake()`
  - `journal_med_on_space()`
  - `journal_low_on_space()`
  - `journal_cur_seq()`
  - `journal_last_unallocated_seq()`
  - `journal_cur_buf()`
- Provides sequence/buffer lookup:
  - `journal_seq_to_buf()` under journal lock.
  - `journal_res_buf()` and `journal_res_data()` fast path for held reservations.
- Provides reservation state bitfield helpers:
  - `journal_state_count()`
  - `journal_state_seq_count()`
  - `journal_state_inc()`
  - `journal_state_buf_put()`
- Provides journal entry size/overhead helpers:
  - `jset_u64s()`
  - `journal_entry_overhead()`
- Provides entry construction helpers:
  - `bch2_journal_add_entry_noreservation()`
  - `journal_res_entry()`
  - `journal_entry_init()`
  - `journal_entry_set()`
  - `__bch2_journal_add_entry()`
  - `bch2_journal_add_entry()`
  - `journal_entry_empty()`
- Provides error helper:
  - `bch2_journal_error()`
- Provides buffer/ref release helpers:
  - `__bch2_journal_buf_put()`
  - `bch2_journal_buf_put()`
  - `bch2_journal_res_put()`
- Defines reservation flags:
  - `JOURNAL_RES_GET_NONBLOCK`
  - `JOURNAL_RES_GET_CHECK`
- Implements fast reservation acquisition in `journal_res_get_fast()`:
  - Atomically reserves space in the current open journal entry.
  - Checks entry capacity, watermark, and ring-slot refcount overflow.
  - Supports check-only mode.
  - Fills reservation seq/offset/overwrite state on success.
- Implements public inline `bch2_journal_res_get()` wrapper:
  - Asserts journal running.
  - Uses fast path, then slow path.
  - Acquires lockdep shared map for real reservations.
- Declares non-inline journal APIs for close, put-final, slowpath, quiesce, shutdown quiesce, write work, reservation resizing, flushes, rewind, noflush, metadata flush, halt, block/unblock, write-buffer flush selection, and debug formatting.
- Defines RAII class `journal_block` for scoped blocking/unblocking.

Role:
- This is the hot-path interface used by btree transactions and metadata update code to reserve journal space and append entries.
- Keeps lockless/atomic reservation logic inline for performance while delegating slow/error paths to `journal.c`.

Notable invariants:
- Held reservations pin their ring slot, allowing lockless `journal_res_buf()` lookup.
- `bch2_journal_res_put()` pads unused reserved space with empty btree-key entries before dropping the buffer ref.
- `bch2_journal_res_get()` assumes `JOURNAL_running` and no foreign stop thread unless the journal is already in error state.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/read.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/read.c

Journal read/recovery scanner: reads journal buckets across devices, deduplicates entries, validates replay windows, handles fast bucket search, missing entry checks, checksum reporting, rewind rereads, and replay start metadata.

Key responsibilities:
- Persists/resumes per-member journal position:
  - `bch2_journal_pos_from_member_info_set()` writes last journal bucket and offset to member info.
  - `bch2_journal_pos_from_member_info_resume()` restores device journal current index and free sectors.
- Formats journal pointers, pointer lists, entry datetime, and sequence datetime text for diagnostics.
- Validates journal checksums with `jset_csum_good()`.
- Frees or marks replay entries ignored through `journal_replay_free()`.
- Optionally strips overwrite/log entries from replay entries when recovery info retention, rewind, and journal scrub are not active.
- Maintains `struct journal_list`, a closure-coordinated shared read accumulator containing last needed sequence, lock, return code, and full-read mode.
- Adds read entries in `journal_entry_add()`:
  - Computes `last_seq`, adjusted for rewind.
  - Tracks oldest sequence found on disk.
  - Drops entries older than the needed range unless reading entire journal.
  - Establishes a base sequence for genradix indexing.
  - Drops no-longer-needed older entries when a newer flush entry advances `last_seq`.
  - Deduplicates same sequence across devices.
  - Tracks all physical pointers for a sequence.
  - Reports duplicate same-device and non-identical-replica fsck errors.
  - Keeps the good checksum copy when duplicates differ by checksum quality.
- Reads full journal buckets in `journal_read_bucket()`:
  - Reads bucket contents.
  - Walks entries until bucket end or empty/invalid boundary.
  - Handles checksum-error size distrust by advancing one block.
  - Updates per-device highest sequence, current index, sectors free, and bucket sequence.
  - Decrypts entry payload.
  - Adds entries to shared journal list.
- Implements large-journal fast scanning:
  - `journal_peek_bucket()` reads only the first block to get a candidate sequence.
  - `journal_anchor_bucket()` finds any non-empty bucket via bisect-stride descent.
  - `journal_bsearch_head()` binary-searches forward from an anchor to find write head.
  - `journal_walk_inuse()` walks backward from head through live buckets with strictly decreasing sequence numbers.
  - `journal_bsearch_collect()` combines fast path and fallback rebuild from all peeked buckets.
- Reads one device in `bch2_journal_read_device()`:
  - Allocates read buffer.
  - Uses fast header-peek path for journals larger than 32 buckets unless full read requested.
  - Reads live buckets sorted by descending sequence and stops after passing `last_seq`.
  - Checks monotonicity and records fsck count on irregular bucket sequence layout.
  - Falls back to full bucket reads when needed.
  - Sets device dirty/discard indices so reclaim can later reclaim unpinned buckets.
  - Releases device READ ref and closure.
- Prints checksum errors only for journal entries that will actually be used.
- Computes missing non-blacklisted ranges with `bch2_journal_entry_missing_range()`.
- Detects missing entries:
  - `journal_has_any_missing()` checks union of all device reads before deciding fast path missed data.
  - `journal_retry_full_read()` rereads all large journals fully when fast path produced gaps.
  - `bch2_journal_check_for_missing()` emits fsck errors with neighboring pointer diagnostics.
- Implements `bch2_journal_reread_for_rewind()`:
  - Finds oldest `last_seq` needed by rewind ranges.
  - Rereads buckets whose known max sequence could contain needed entries.
  - Un-ignores entries previously dropped as not dirty but now needed for rewind replay.
  - Updates `c->journal_replay_seq_start`.
- Implements `bch2_journal_read()`:
  - Launches per-device reads in parallel using closures.
  - Skips devices without journal data unless reading entire journal/fsck.
  - Marks journal degraded if a readable member cannot be referenced.
  - Finds `cur_seq`, `replay_end`, `last_seq`, and clean/empty state from newest usable flush entry.
  - Drops no-flush entries and torn final flush entry.
  - Handles dirty-but-no-journal after dropping nonflushes.
  - Applies journal rewind constraints and drop-before calculation.
  - Marks blacklisted entries ignored and reports unexpected blacklisted flush entries.
  - Retries full read if bsearch fast path left missing entries.
  - Validates missing sequence coverage.
  - Prints checksum errors, validates each replayed `jset`, builds journal replica device sets, and extracts rewind-limit/rewind entries.

Important interactions:
- Feeds `recovery.c` with populated `c->journal_entries` and `journal_start_info`.
- Uses blacklist helpers to ignore or skip blacklisted sequences.
- Uses validate code to check early and full `jset` structure.
- Uses allocator/replicas code to verify journal entry replication.
- Uses member device refs so journal reads are safe during startup.

Notable invariants:
- The union of all device journal reads must cover every non-blacklisted sequence in the replay window.
- New journal writes must start strictly after every on-disk entry, including no-flush entries that will be blacklisted.
- Fast bsearch is only an optimization; missing-range detection forces full reread before reporting gaps.
- Rewind cannot target entries older than the persisted rewind discard limit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/read.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/read.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/journal/read.h

Public journal read/replay helper header.

Key contents:
- Includes checksum and darray helpers.
- Declares member-info journal position helpers:
  - `bch2_journal_pos_from_member_info_set()`
  - `bch2_journal_pos_from_member_info_resume()`
- Defines `journal_replay_ignore()` for entries ignored due to blacklist or not-dirty filtering.
- Provides typed journal-entry iteration helpers:
  - `__jset_entry_type_next()`
  - `for_each_jset_entry_type`
  - `jset_entry_for_each_key`
  - `for_each_jset_key`
- Defines `jset_datetime()` to extract `BCH_JSET_ENTRY_datetime`.
- Defines `journal_nonce()` for checksum/encryption nonce generation from journal sequence and journal nonce type.
- Declares journal pointer formatting:
  - `bch2_journal_ptrs_to_text()`
- Defines `u64_range` and darray type for sequence ranges.
- Declares missing-range, datetime, reread, and read APIs:
  - `bch2_journal_entry_missing_range()`
  - `bch2_journal_seq_datetime_to_text()`
  - `bch2_journal_reread_for_rewind()`
  - `bch2_journal_read()`

Role:
- Shared by recovery, journal reader, journal validators, and diagnostics for iterating and interpreting read journal entries.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/journal/read.h -->