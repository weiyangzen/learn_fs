<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/target.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/target.c

## Purpose

`target.c` validates and normalizes perf target selection options, parses user IDs, and formats target-related error messages. It resolves conflicts among pid/tid, CPU, system-wide, BPF, and per-thread modes.

## Important APIs, Types, and Functions

`target__validate()` mutates a `struct target` into a consistent mode and returns an `enum target_errno` describing the first override. `parse_uid()` converts a username or numeric UID string to `uid_t`, returning `UINT_MAX` on failure. `target__strerror()` formats either normal errno values or negative target-specific errors into a caller buffer. The local `target__error_str[]` must stay ordered with `enum target_errno`.

## Control Flow and Data Flow

Validation first maps `pid` to `tid` because perf treats pid targeting as thread-list targeting. If a tid is present, it clears `cpu_list` and `system_wide`. If BPF targeting is present, it clears CPU list, tid, and per-thread mode. If per-thread mode conflicts with system-wide or CPU targeting, it clears per-thread mode. Only the first conflict is reported, but all applicable normalizations still run.

`parse_uid()` tries `getpwnam_r()` first, then parses a decimal number and verifies it with `getpwuid_r()`. `target__strerror()` delegates nonnegative errors to `str_error_r()` and handles only the target-specific negative range.

## State and Persistence Behavior

The file does not own persistent global state beyond the static error string table. `target__validate()` intentionally persists normalization by modifying the caller's `struct target` in place. `parse_uid()` reads system passwd database state.

## Dependencies and Integration Points

The code depends on `target.h`, libc passwd APIs, Linux kernel/string helpers, and perf's target error enum. It integrates with perf command option validation before evlist/thread/cpu map creation and with user-facing warning/error formatting.

## Risks and Edge Cases

Because validation mutates the target, callers that need original user intent must preserve it before calling. Only the first override is returned, so multiple conflicts can be normalized with only one reported message. `parse_uid()` uses `strtol()` into `int`, which can mishandle very large numeric UIDs on systems where `uid_t` is wider. User/group database failures are collapsed to `UINT_MAX`.

## Test Signals

Tests should cover every target conflict and verify both mutation and returned first error. Additional tests should verify pid-to-tid normalization, no-op valid targets, username UID parsing, numeric UID parsing, invalid names, nonexistent numeric UIDs, large UID strings, normal errno formatting, target-specific formatting, and invalid target error ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/target.c -->
