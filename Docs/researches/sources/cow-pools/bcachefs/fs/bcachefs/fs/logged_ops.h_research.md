# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.h

This header declares the logged-operation API and the canonical list of logged operation kinds.

Key elements:
- `BCH_LOGGED_OPS()` currently lists:
  - `truncate`
  - `finsert`
  - `stripe_update`
- `bch2_logged_op_update()` is an inline helper inserting/updating a logged op in `BTREE_ID_logged_ops` using cached iteration.
- Declares start, finish, and recovery entry points:
  - `bch2_resume_logged_ops()`
  - `__bch2_logged_op_start()`
  - `bch2_logged_op_start()`
  - `bch2_logged_op_finish()`

Role:
- Shared by operation producers and recovery dispatch.
- The macro list drives the `logged_op_fns[]` table in `logged_ops.c`, so adding a new logged-op type requires matching resume function naming and on-disk format support.
