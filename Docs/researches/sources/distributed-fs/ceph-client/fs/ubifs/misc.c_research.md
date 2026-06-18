<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/misc.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/misc.c

## Purpose
`misc.c` contains small global UBIFS helpers that do not belong to a larger subsystem: formatted informational, warning, and error logging, plus conversion of the configured assert action to a readable string.

## Important APIs, Types, and Functions
Exported functions are `ubifs_msg()`, `ubifs_err()`, `ubifs_warn()`, and `ubifs_assert_action_name()`. They use `struct ubifs_info` for UBI volume identifiers and assert configuration, Linux `va_format` for varargs logging, `current->pid`, and `__builtin_return_address(0)` for error/warning call-site reporting.

## Control Flow
Each logging function starts a `va_list`, wraps it in `struct va_format`, emits a prefixed kernel log line, and closes the list. `ubifs_msg()` uses `pr_notice()` with `UBIFS (ubiX:Y)`. `ubifs_err()` uses `pr_err()` and includes pid and caller symbol. `ubifs_warn()` uses `pr_warn()` with the same pid/caller context. `ubifs_assert_action_name()` indexes the static `assert_names[]` table by `c->assert_action`.

## State and Persistence
There is no on-flash persistence and no mutable filesystem state except log output. The only local state is the static mapping for `ASSACT_REPORT`, `ASSACT_RO`, and `ASSACT_PANIC`.

## Dependencies and Integration Points
All UBIFS modules use these helpers for consistent diagnostics. The helpers depend on Linux kernel logging APIs and `ubifs_info.vi` fields. They are especially important on recovery and validation paths where the caller location helps identify which consistency check failed.

## Risks and Test Signals
Risk is low but nonzero: out-of-range `assert_action` would index past `assert_names`, and logging macros must be safe in error paths. Test signals are compile coverage, boot/mount logs including correct ubi/volume ids, warning/error caller symbols, and assert-action configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/misc.c -->
