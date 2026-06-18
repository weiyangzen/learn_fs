# File Research: sources/cow-pools/bcachefs-tools/fs/init/error.c

## Purpose
Implements bcachefs error policy, fsck error reporting/decision logic, fatal/inconsistent/topology handling, IO error accounting work, interactive fsck prompts, repeated-error memoization/rate limiting, bkey validation error conversion, contextual inode/offset error text, and filesystem error state initialization.

## Main Contents
- `__bch2_log_msg_start()` initializes a printbuf with bcachefs log prefix/indentation.
- Inconsistent error handling:
  - `__bch2_inconsistent_error()` sets `BCH_FS_error` and applies `errors=` policy: continue, fix_safe/read-only, or panic.
  - `bch2_fs_inconsistent()` and `bch2_trans_inconsistent()` format messages and include transaction update details when available.
- Topology/fatal errors:
  - `__bch2_topology_error()` sets topology-error flag and either emergency-ROs or schedules explicit topology recovery.
  - `bch2_fatal_error()` emits a fatal message and triggers emergency read-only.
- IO error handling:
  - `bch2_io_error()` increments per-device persistent error counters, starts write-error timing, queues long work with `ref_outer`.
  - `bch2_io_error_work()` demotes a device to read-only after sustained write errors when possible, otherwise makes the filesystem emergency read-only.
- Interactive fsck prompt support for kernel stdio redirect and userspace tools builds.
- `fsck_err_get()`, `count_fsck_err_locked()`, and `__bch2_count_fsck_err()` track per-error id count, last message, repeated transaction-restart duplicates, and ratelimiting.
- `bch2_fsck_err_opt()` converts fsck flags plus filesystem options into typed repair/ignore/ask/exit decisions.
- `__bch2_fsck_err()` is the central fsck error engine. It formats messages, honors silent-error bits, handles autofix policy, runtime self-healing policy, fsck ask/yes/no/exit modes, transaction relock around prompts, repair action text, logging, state flags for fixed/not-fixed errors, and transaction log strings.
- `__bch2_bkey_fsck_err()` wraps invalid bkey validation failures and usually converts them to "delete key" fsck decisions outside write/commit validation.
- Flush/free functions release tracked fsck error messages.
- `bch2_inum_offset_err_msg_trans_norestart()` and wrapper add path/inode/offset context to errors.
- `bch2_fs_errors_init_early()`, `bch2_fs_errors_init()`, and `bch2_fs_errors_exit()` initialize and clean error list/count structures.

## Integration Notes
`error.h` macros used throughout the filesystem eventually route here. `namei.c`, `str_hash.c`, `quota.c`, `xattr.c`, and logged-op replay all use fsck/inconsistent helpers. Device error demotion calls `__bch2_dev_set_state()` from `dev.c`, with `ref_outer` lifetime rules matching device removal. Bkey validators use `__bch2_bkey_fsck_err()` to report corrupt on-disk keys with validation context.

## Risks and Edge Cases
- `__bch2_fsck_err()` must sometimes unlock a transaction for user input and relock afterward; callers must handle transaction restart returns.
- Silent errors set `BCH_FS_errors_fixed_silent` and return fix/ignore without printing.
- Runtime self-healing is restricted by `errors=` policy; some autofixable errors still force shutdown under `errors=ro`.
- IO error work is intentionally never cancelled; device free drains `ref_outer` instead.
