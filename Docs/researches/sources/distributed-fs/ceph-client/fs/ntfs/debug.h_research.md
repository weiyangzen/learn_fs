# sources/distributed-fs/ceph-client/fs/ntfs/debug.h

## Purpose

`debug.h` declares and wraps NTFS logging helpers. It provides compile-time debug/no-debug behavior while preserving printf-style checking for warning and error functions.

## Important APIs, Types, And Functions

- Under `DEBUG`, `debug_msgs`, `__ntfs_debug()`, `ntfs_debug()`, and `ntfs_debug_dump_runlist()` are active.
- Without `DEBUG`, `ntfs_debug()` and `ntfs_debug_dump_runlist()` compile to no-op blocks that still type-check arguments through unreachable references.
- `__ntfs_warning()` and the `ntfs_warning()` macro emit warnings with caller function context.
- `__ntfs_error()` and the `ntfs_error()` macro emit errors with caller function context.
- `ntfs_handle_error(struct super_block *sb)` is declared as the error-policy hook called by `__ntfs_error()`.

## Control Flow And Usage

Call sites use `ntfs_debug()`, `ntfs_warning()`, and `ntfs_error()` rather than the underscored functions. The macros automatically pass `__func__`, and debug builds also pass `__FILE__` and `__LINE__`.

## State And Persistence Behavior

The header itself has no persistent state. Its macros influence whether debug messages are emitted and whether error calls can trigger the implementation's filesystem error handler.

## Dependencies And Integration Points

It includes Linux `fs.h` for `struct super_block` and `runlist.h` for debug runlist dumping. It is included by most NTFS implementation files and is part of the driver's common diagnostics interface.

## Risks And Edge Cases

- No-op debug macros avoid evaluating runtime logging calls, so side effects must never be embedded in debug arguments.
- Warning/error macros always pass `__func__`; callers that need no function prefix must call underscored functions directly, which is uncommon.
- The declaration of `ntfs_handle_error()` makes logging part of error-state policy, so using `ntfs_error()` for benign messages can have side effects.

## Test Signals

Build tests should cover DEBUG and non-DEBUG configurations, printf-format checking, no-op macro type checking, and linkage of `ntfs_handle_error()`. Runtime tests should verify warning/error paths through `debug.c`.
