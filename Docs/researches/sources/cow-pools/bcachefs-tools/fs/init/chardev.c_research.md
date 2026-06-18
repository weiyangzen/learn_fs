# File Research: sources/cow-pools/bcachefs-tools/fs/init/chardev.c

## Purpose
Implements the bcachefs character-device ioctl interface. It dispatches global and per-filesystem ioctls, handles device management commands, exposes usage/accounting/superblock queries, runs asynchronous data jobs via file descriptors, and registers `/dev/bcachefs-ctl` plus per-filesystem control devices.

## Main Contents
- Device lookup helpers:
  - `bch2_device_lookup()` resolves by member index or user path and returns a normal device ref.
  - `bch2_device_lookup_outer()` converts to `ref_outer` for operations that acquire `state_lock`, avoiding removal deadlocks.
- `bch2_global_ioctl()` currently handles offline fsck.
- `bch2_ioctl_query_uuid()` returns filesystem user UUID.
- `bch2_copy_ioctl_err_msg()` copies a printbuf error message to v2 ioctl error buffers and appends the error string when needed.
- Device management ioctl handlers for add, remove, online, offline, set-state, resize, and resize-journal, with v1/v2 variants, privilege checks, flag validation, device lookup, and error propagation.
- Asynchronous data job support:
  - `struct bch_data_ctx`
  - `bch2_data_thread()`
  - release/read file operations
  - `bch2_ioctl_data()`, which starts a `thread_with_file` and reports progress events.
- Query handlers:
  - `bch2_ioctl_fs_usage()`
  - `bch2_ioctl_query_accounting()`
  - legacy and v2 device usage
  - `bch2_ioctl_read_super()`
  - `bch2_ioctl_disk_get_idx()`
- `bch2_fs_ioctl()` main command switch. A small set of read/query ioctls can run before `BCH_FS_started`; mutation and deeper query commands require started state.
- Character-device registration:
  - global IDR mapping minors to `struct bch_fs`
  - file ops for unlocked ioctl/open
  - per-filesystem device create/destroy
  - module-level init/exit.

## Integration Notes
This is the userspace control surface for `dev.c`, journal resize, data movement/scrub, fsck, accounting, counters, and superblock reads. It relies heavily on typed bcachefs errors but returns Linux errnos through `bch2_err_class()`. The `ref_outer` lookup variants match the lifetime rules documented in `dev.c`: callers that may block on `state_lock` cannot hold a normal `ca->ref` because removal drains that ref under the same lock.

## Risks and Edge Cases
- Most device mutation ioctls require `CAP_SYS_ADMIN`; query functions still validate started state and buffer sizes.
- V2 ioctls copy detailed error strings back to userspace; v1 ioctls mostly log errors.
- `bch2_ioctl_disk_resize_v2()` uses normal device refs while the older resize path uses outer refs, even though resize takes `state_lock`; this is worth checking against the deadlock comment near `bch2_device_lookup_outer()`.
- Async data jobs hold a write ref and must release it in the worker/error cleanup path.
