# sources/distributed-fs/ceph-client/fs/btrfs/messages.c

## Purpose
`messages.c` implements Btrfs logging, filesystem-error handling, fatal panic reporting, and 32-bit logical-address warnings. It centralizes message prefixes, filesystem-state suffixes, rate limiting, and the transition to forced-readonly on serious errors. The source was read as a complete 301-line file.

## Important APIs, Types, and Functions
Important functions are `btrfs_decode_error()`, `__btrfs_handle_fs_error()`, `_btrfs_printk()` under `CONFIG_PRINTK`, `btrfs_warn_32bit_limit()` and `btrfs_err_32bit_limit()` on 32-bit builds, and `__btrfs_panic()`. Internal helpers include `btrfs_state_to_string()`, the state-character table, log-level names, and per-log-level ratelimit states.

## Control Flow
Generic Btrfs printk macros call `_btrfs_printk()`, which formats messages as `BTRFS <level> (device <id><state>): ...`, appends compact state flags when unusual filesystem states are set, and applies per-level ratelimiting unless debug builds disable it. `__btrfs_handle_fs_error()` ignores benign `-EROFS` on an already readonly superblock, logs a critical error with decoded errno and caller location, records `fs_info->fs_error`, and after mount completion stops discard and marks the superblock readonly. `__btrfs_panic()` formats a fatal message and either calls `panic()` when the mount option requests it or logs a critical message before the caller's BUG.

## State and Persistence Behavior
There is no file-backed persistence. Runtime state changes include `fs_info->fs_error`, superblock readonly state, discard state, and one-shot 32-bit warning/error flags. The state-string reflects `fs_info->fs_state` and `BTRFS_FS_ERROR()`.

## Dependencies and Integration Points
The file depends on Btrfs `fs.h`, `messages.h`, `discard.h`, and `super.h`, plus kernel printk, ratelimit, panic, and superblock APIs. It is used by nearly all Btrfs modules through macros in `messages.h`.

## Risks and Edge Cases
Error handling must avoid forcing readonly before the superblock is fully born and must avoid noisy repeated messages. The compact state string intentionally omits non-error RO state but adds emergency/error characters. Device replace is not canceled during forced readonly to avoid deadlock, so status persistence can lag. Rate limiting is per log level globally, which prevents low-severity floods from suppressing critical messages but can still hide repeated same-level diagnostics.

## Test Signals
Signals include printk-prefix tests under normal and stateful filesystems, forced-readonly behavior after injected transaction/metadata errors, no-op behavior for `-EROFS` on readonly mounts, panic-on-fatal-error mount option tests, ratelimit behavior, discard stop observation, and 32-bit threshold warning/error one-shot behavior on 32-bit builds.
