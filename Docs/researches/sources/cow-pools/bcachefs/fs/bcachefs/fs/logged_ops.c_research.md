# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops.c

This file implements recovery and lifecycle handling for the `BTREE_ID_logged_ops` btree, which stores resumable filesystem operations that must survive crashes.

Key elements:
- `logged_op_fns[]` maps logged operation key types to their resume functions via `BCH_LOGGED_OPS()`.
- `bch2_resume_logged_ops()` scans `BTREE_ID_logged_ops` for `LOGGED_OPS_INUM_logged_ops` and calls `resume_logged_op()` for each entry.
- `resume_logged_op()` reassembles the bkey into a mutable `bkey_buf`, checks for the inconsistency “clean filesystem has logged op”, dispatches the resume callback if recognized, then deletes the logged operation with `bch2_logged_op_finish()`.
- `__bch2_logged_op_start()` allocates an empty slot in the logged-ops btree, assigns the operation position, and updates the btree transaction.
- `bch2_logged_op_start()` wraps start in `commit_do()` with `BCH_TRANS_COMMIT_no_enospc`.
- `bch2_logged_op_finish()` deletes the operation with `BCH_TRANS_COMMIT_no_check_rw | BCH_TRANS_COMMIT_no_enospc`, and treats deletion failure as fatal because a completed operation would remain logged.

Important behavior:
- The finish path is designed to succeed even during shutdown, avoiding spurious `EROFS` on cleanup.
- Recovery detects logged operations on filesystems marked clean via `fsck_err_on(... logged_op_but_clean ...)`.
- Unknown logged operation types are still deleted because `fn` may be `NULL` but `bch2_logged_op_finish()` still runs.

Dependencies:
- Uses btree transaction/update APIs, bkey buffers, EC/data operation resume hooks, and fatal/fsck error handling.
- The operation type list comes from `logged_ops.h`, while on-disk layouts come from `logged_ops_format.h`.
