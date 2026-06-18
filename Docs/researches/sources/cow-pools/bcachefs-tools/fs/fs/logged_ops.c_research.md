# File Research: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops.c

## Purpose
Implements persistent logged operation replay and cleanup. Logged operations are stored in the `BTREE_ID_logged_ops` btree so long-running or multi-step operations can resume after recovery and then delete their log record.

## Main Contents
- `struct bch_logged_op_fn`, mapping logged op key types to resume callbacks.
- `logged_op_fns[]`, generated from `BCH_LOGGED_OPS()` and bound to `bch2_resume_logged_op_truncate`, `bch2_resume_logged_op_finsert`, and `bch2_resume_logged_op_stripe_update`.
- `logged_op_fn()`, a linear type-to-callback lookup.
- `resume_logged_op()`, which reassembles the bkey into a mutable buffer, reports an fsck error if a supposedly clean filesystem still has logged ops, invokes the matching resume callback, and then finishes the logged op.
- `bch2_resume_logged_ops()`, which iterates the logged-ops inode range in the logged ops btree and resumes each key.
- `__bch2_logged_op_start()` and `bch2_logged_op_start()`, which allocate an empty slot and insert a logged op under no-ENOSPC commit rules.
- `bch2_logged_op_finish()`, which deletes the logged op with `no_check_rw` and `no_enospc`, escalating deletion failures to fatal filesystem error because a stale operation would remain replayable.

## Integration Notes
This file depends on individual operation resume implementations from truncate, finsert, and stripe update subsystems. Recovery invokes `bch2_resume_logged_ops()` after mount-time journal/btree setup. Callers that create logged ops are expected to hold an appropriate write reference; finish deliberately bypasses normal read/write checking so cleanup can succeed during shutdown paths.

## Risks and Edge Cases
- If `fn->resume()` returns an error it is currently ignored; the function still proceeds to `bch2_logged_op_finish()`. This may be intentional for idempotent resume callbacks, but it is a notable behavior to audit.
- Failure to delete a logged op is fatal by design.
- Logged ops on a filesystem marked clean are treated as fsck inconsistencies.
