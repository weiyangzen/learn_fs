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
