# File Research: sources/cow-pools/bcachefs-tools/fs/data/io_misc.c

## Purpose
Implements miscellaneous data operations: fallocate, hole punching, truncate, and file insert/collapse. Truncate and insert/collapse are logged operations so they can resume after crash.

## Main Interfaces and Behavior
- `bch2_extent_fallocate()` overwrites a range with zeroes/reservation. If no-COW unwritten extents are supported and requested, it allocates real extent pointers, marks them unwritten, and updates allocation clocks/open buckets. Otherwise it writes a reservation key.
- Fallocate computes missing replicas relative to existing fully allocated pointers, obtains a disk reservation before allocator interaction, and commits via `bch2_extent_update()`.
- `bch2_fpunch_snapshot()` is an fsck helper that deletes/trims extents over a snapshot range using max-sized delete keys and `bch2_extent_trim_atomic()`.
- `bch2_fpunch_at()` punches a file range for a subvolume/inode by resolving the subvolume snapshot, peeking extents up to an end position, constructing delete keys, and applying `bch2_extent_update()` in restart-aware loops.
- `bch2_fpunch()` is the external wrapper that creates a transaction and extent iterator.
- Truncate support includes `bch2_logged_op_truncate_to_text()`, `truncate_set_isize()`, `__bch2_resume_logged_op_truncate()`, `bch2_resume_logged_op_truncate()`, and `bch2_truncate()`. The resume path first updates inode size, then punches extents past rounded-up new size.
- File insert/collapse support includes logged-op rendering, `adjust_i_size()`, `__bch2_resume_logged_op_finsert()`, `bch2_resume_logged_op_finsert()`, and `bch2_fcollapse_finsert()`.
- The insert/collapse state machine has `LOGGED_OP_FINSERT_start`, `shift_extents`, and `finish` states. It updates inode size, optionally punches collapsed range, shifts extents backward or forward, stores progress in `op->v.pos`, and updates inode timestamps/size at finish.
- Both truncate and finsert/fcollapse hold `c->snapshots.create_lock` while starting/resuming/finishing because logged ops are not atomic with snapshot creation.

## Dependencies and Coupling
Depends on extent update, allocator reservations, inode read/write, logged ops, subvolume snapshot lookup, write points, and reconcile trigger support.

## Risks and Invariants
- Restart handling is explicit; some transaction restarts are converted to success at API boundaries after progress has been made.
- Insert/collapse must handle snapshot mismatches by reserving extra space when copying extents into a new snapshot.
- Compressed extent splits may require additional disk reservation because live data has to be rewritten.
