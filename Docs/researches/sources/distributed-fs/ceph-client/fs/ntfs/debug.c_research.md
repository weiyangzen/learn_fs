# sources/distributed-fs/ceph-client/fs/ntfs/debug.c

## Purpose

`debug.c` centralizes NTFS warning, error, and optional debug logging. It formats messages with function names and device identifiers, rate-limits warnings/errors in non-debug builds, invokes filesystem error handling for errors tied to a superblock, and can dump runlists when compiled with `DEBUG`.

## Important APIs, Types, And Functions

- `__ntfs_warning()` formats a warning message using `struct va_format` and emits it through `pr_warn()` or `pr_warn_ratelimited()`.
- `__ntfs_error()` formats an error message through `pr_err()` or `pr_err_ratelimited()` and calls `ntfs_handle_error(sb)` when a superblock is supplied.
- `debug_msgs` is a runtime flag, present only under `DEBUG`, that gates debug messages.
- `__ntfs_debug()` emits debug messages with file, line, and function context when `debug_msgs` is enabled.
- `ntfs_debug_dump_runlist()` prints each runlist element, including special negative LCN states, in debug builds.

## Control Flow And Algorithms

Warning and error functions calculate whether the function name is non-empty, bind varargs to `va_format`, and select device-specific or generic log format based on whether `sb` is non-NULL. Debug builds use non-rate-limited logging; non-debug builds rate-limit warnings and errors. Error logging additionally routes the superblock to `ntfs_handle_error()`.

Runlist dumping iterates until a zero-length terminator, maps negative LCN sentinels to readable labels, and prints VCN, LCN/sentinel, and run length.

## State And Persistence Behavior

The file does not persist NTFS metadata directly. Its only state is `debug_msgs` under `DEBUG`. `__ntfs_error()` can indirectly change filesystem state through `ntfs_handle_error(sb)`, which may mark the volume or mount state according to broader NTFS policy.

## Dependencies And Integration Points

It includes `debug.h`, which includes Linux `fs.h` and `runlist.h`. The functions are called throughout the NTFS driver via macros in `debug.h`, so they are the standard reporting path for corruption, I/O failure, and diagnostic output.

## Risks And Edge Cases

- Passing `NULL` as the superblock avoids `ntfs_handle_error()`, so callers must choose intentionally for corruption that should mark the volume erroneous.
- In non-debug builds, warning/error rate limiting can suppress repeated signals during severe metadata corruption.
- `ntfs_debug_dump_runlist()` assumes the runlist is terminated and caller-provided synchronization protects it; corrupt or concurrently modified runlists can produce invalid reads.

## Test Signals

Tests should verify formatted output paths with and without superblocks, rate-limited vs debug build behavior, `ntfs_handle_error()` invocation for errors, debug message gating by `debug_msgs`, and runlist dump formatting for normal runs, holes, delayed allocation, not-mapped, and terminator entries.
