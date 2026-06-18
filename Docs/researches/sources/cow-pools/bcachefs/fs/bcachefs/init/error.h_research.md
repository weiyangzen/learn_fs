# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/error.h

This header declares error handling APIs and many fsck/error macros.

Key elements:
- Declares inconsistency, topology, fatal, IO-error, latency/accounting, inode-offset formatting, and error lifecycle functions.
- Defines `struct fsck_err_state`, which records per-error id, count, cached return decision, fix policy, rate-limit state, and last message.
- `bch2_fs_inconsistent_on()` and `bch2_trans_inconsistent_on()` wrap conditional inconsistency reporting.
- Fsck macro families:
  - `mustfix_fsck_err*`
  - `fsck_err*`
  - `log_fsck_err*`
  - `ret_fsck_err*`
  - `ret_log_fsck_err*`
- `bkey_fsck_err*` macros convert invalid bkeys into delete-key fsck outcomes.
- `bch2_fs_fatal_error()` and `bch2_fs_fatal_err_on()` add function-name context to fatal errors.
- `bch2_account_io_success_fail()` clears write-error timers on success or records IO errors on failure.
- `bch2_account_io_completion()` adds latency accounting and success/failure accounting.

Role:
- Provides the common error/reporting vocabulary used across metadata validation, fsck, btree code, device code, and IO paths.
