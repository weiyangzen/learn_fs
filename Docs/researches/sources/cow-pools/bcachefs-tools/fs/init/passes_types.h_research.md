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
