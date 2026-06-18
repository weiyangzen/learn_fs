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
