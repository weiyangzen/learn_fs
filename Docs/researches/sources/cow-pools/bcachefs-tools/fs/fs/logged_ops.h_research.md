# File Research: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.h

## Purpose
Small public header for the logged operation subsystem.

## Main Contents
- `BCH_LOGGED_OPS()` macro listing supported logged operation families: `truncate`, `finsert`, and `stripe_update`.
- Inline `bch2_logged_op_update()`, which inserts/updates a logged op in `BTREE_ID_logged_ops` using cached iteration.
- Declarations for resuming, starting, and finishing logged operations.

## Integration Notes
`logged_ops.c` expands `BCH_LOGGED_OPS()` to build the resume dispatch table. Other subsystems use `bch2_logged_op_start()`, `bch2_logged_op_update()`, and `bch2_logged_op_finish()` around operations that must survive recovery.

## Risks and Edge Cases
- Any new logged op must be added to `BCH_LOGGED_OPS()` and must provide a matching `bch2_resume_logged_op_<name>()` symbol.
- Updates go directly to the logged ops btree; callers are responsible for transaction/commit context and write-reference requirements.
