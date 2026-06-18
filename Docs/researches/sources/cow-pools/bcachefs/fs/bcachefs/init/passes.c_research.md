# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.c

## Role

Implements bcachefs recovery-pass scheduling, persistence, dependency handling, ratelimiting, rewind, async online-pass execution, and status reporting.

## Major Responsibilities

- Builds `bch2_recovery_passes[]` and the `recovery_passes[]` dispatch table from `BCH_RECOVERY_PASSES()`.
- Converts between execution-order pass IDs and stable superblock IDs with `bch2_recovery_passes_to_stable()` / `from_stable()`.
- Owns the superblock `recovery_passes` field text output and per-pass last-run/runtime tracking.
- Decides whether an explicit pass should be persisted, run immediately, deferred, ratelimited, or cause recovery rewind.
- Runs passes sequentially via `bch2_run_recovery_passes()` and startup selection via `bch2_run_recovery_passes_startup()`.
- Defers eligible `PASS_ONLINE` passes into background work after mount recovery.
- Provides human-readable recovery-pass status.

## Key Control Flow

`bch2_run_recovery_passes_startup()` composes the pass set from always-run passes, unclean-shutdown passes, fsck passes, mount-option requested passes, and superblock-required passes. It applies `recovery_pass_last`, excludes requested passes except `set_may_go_rw`, skips passes before `from`, and defers online-safe passes unless fsck is active.

`bch2_run_recovery_passes()` loops through the lowest set pass bit, runs it, flushes the journal, records completion, and handles rewinds by restoring the original pass set from `rewound_to`.

`__bch2_run_explicit_recovery_pass()` is the central repair hook. It can set persistent superblock bits, set ephemeral bits, mark ratelimited passes, trigger async online passes, or return `restart_recovery` if the requested pass is earlier than the current recovery position.

## Notable Details

- Stable IDs are deliberately separate from enum order; the second field in `BCH_RECOVERY_PASSES()` is the persistent ABI.
- `scan_for_btree_nodes` is never scheduled persistently; `check_topology` invokes it when required.
- `recovery_pass_should_defer()` only defers a pass if it and all scheduled dependents can run online.
- `bch2_recovery_pass_set_no_ratelimit()` appears name-sensitive: the implementation currently calls `SET_BCH_RECOVERY_PASS_NO_RATELIMIT(e, false)` even when entering the branch for a missing no-ratelimit flag.
- After crossing `check_snapshots`, the runner wakes copygc and reconcile work.
