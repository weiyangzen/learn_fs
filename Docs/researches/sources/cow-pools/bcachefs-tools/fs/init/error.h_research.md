# File Research: sources/cow-pools/bcachefs-tools/fs/init/error.h

## Purpose
Public error-handling header for bcachefs. It declares inconsistent/topology/fsck/fatal/IO error APIs and defines the macros used throughout the codebase to report, fix, ignore, or propagate filesystem consistency errors.

## Main Contents
- Inconsistent error API:
  - `__bch2_inconsistent_error()`
  - `bch2_inconsistent_error()`
  - `bch2_fs_inconsistent()`
  - `bch2_trans_inconsistent()`
  - condition macros for fs/trans inconsistent checks.
- Topology error declarations.
- `struct fsck_err_state`, storing per-error id, count, ratelimit flag, cached return decision, all-yes/all-no fix mode, and last message.
- Fsck counting and option decision declarations.
- `__bch2_fsck_err()` and `bch2_fsck_err()` generic macro that accepts either `struct bch_fs *` or `struct btree_trans *`.
- Macro families:
  - `fsck_err`, `mustfix_fsck_err`, `log_fsck_err`
  - `_on` condition variants
  - `ret_fsck_err`, `ret_log_fsck_err` return-on-error variants
  - wrappers that convert typed fsck fix/ignore errors into boolean "should fix" decisions.
- Bkey validation fsck error wrapper macros that delete invalid bkeys after a fix/ignore decision.
- Fatal error API and condition macro.
- IO error declarations, latency accounting hook/stub, and inline IO success/failure completion accounting.
- Contextual inum/offset error message declarations.
- Error subsystem lifecycle declarations.

## Integration Notes
This header is used broadly by validators, fsck passes, btree code, namespace code, xattr/quota validation, logged op replay, and IO paths. It gives call sites compact macros while keeping policy centralized in `error.c`. The type-dispatch macro for `bch2_fsck_err()` lets code pass either a filesystem or transaction object.

## Risks and Edge Cases
- `fsck_err_on()` warns if passed a filesystem pointer while a btree transaction is active in the current task, because interactive prompts need transaction unlock/relock support.
- Bkey fsck macros currently handle repair by deleting the entire key; the comment notes this may change.
- Macro control flow uses `goto fsck_err` and `return` variants; call sites must provide the expected labels/variables.
