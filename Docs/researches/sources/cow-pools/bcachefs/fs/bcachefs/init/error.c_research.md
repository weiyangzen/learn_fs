# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/error.c

This file implements bcachefs runtime inconsistency policy, fsck error handling, bkey validation errors, IO error accounting, and error-state lifecycle.

Runtime inconsistency handling:
- `__bch2_log_msg_start()` adds the bcachefs log prefix/indent.
- `__bch2_inconsistent_error()` sets `BCH_FS_error` and follows the configured `errors=` policy: continue, emergency read-only, or panic.
- `bch2_fs_inconsistent()` and `bch2_trans_inconsistent()` format and print filesystem or transaction inconsistency messages, including pending transaction updates.
- `__bch2_topology_error()` marks topology error state and either requests explicit topology repair during recovery or forces a topology-repair error.
- `bch2_fatal_error()` formats fatal errors and forces emergency read-only.

IO error handling:
- `bch2_io_error()` increments persistent per-device error counters, starts write-error timing, and schedules `io_error_work`.
- `bch2_io_error_work()` sets a device read-only after sustained write errors if safe; otherwise it puts the filesystem emergency read-only.

Fsck prompting and policy:
- `parse_yn_response()` accepts `y/n/Y/N`, where uppercase applies to all errors of that type.
- Kernel fsck prompting uses `stdio_redirect`, temporarily unlocking btree transactions and doing long unlock if user input waits.
- Userspace prompting uses `getline()`.
- `fsck_err_get()` tracks per-error state for deduplication, repeated answers, and rate limiting.
- `bch2_fsck_err_opt()` converts current fsck/mount options and error flags into fix/ignore/ask/exit outcomes.
- `__bch2_fsck_err()` is the central fsck decision engine: formats the message, detects custom action text, counts/rate-limits, asks or auto-decides, logs transaction strings for fixes, and sets global error/fixed flags.
- `__bch2_count_fsck_err()` increments counts and decides whether to print.

Bkey validation errors:
- `__bch2_bkey_fsck_err()` formats invalid bkey context, journal position if relevant, btree/level, key text, and reason; outside write/commit validation it marks the error autofix/delete.

Error formatting helpers:
- `bch2_inum_offset_err_msg_trans_norestart()` and `bch2_inum_offset_err_msg_trans()` format an inode/path plus byte offset, using namei path reconstruction when possible.

Lifecycle:
- `bch2_fs_errors_init_early()` initializes lists, locks, and count arrays.
- `bch2_fs_errors_init()` loads superblock error counts to CPU state.
- `bch2_flush_fsck_errs()` and `bch2_free_fsck_errs()` release per-error message state.
- `bch2_fs_errors_exit()` frees count arrays.

Important behavior:
- Repeated identical fsck messages reuse previous decisions to avoid repeated prompts across transaction restarts.
- Silent errors can still mark “errors fixed silently”.
- Runtime self-healing is allowed only when error flags and mount policy permit it.
