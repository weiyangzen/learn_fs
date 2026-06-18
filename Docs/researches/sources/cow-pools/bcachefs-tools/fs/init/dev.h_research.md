# File Research: sources/cow-pools/bcachefs-tools/fs/init/dev.h

## Purpose
Public device-management API for bcachefs initialization, online/offline state, add/remove/resize operations, identity reading, and block holder integration.

## Main Contents
- `bch2_devs_list_to_text()` for printing device lists.
- Lookup/membership helpers: `bch2_dev_to_fs()` and `bch2_dev_in_fs()`.
- Low-level lifecycle helpers: IO ref stop, unlink, free, offline, sysfs online, identity read, allocation, and block-device attach.
- State transition helpers: `bch2_dev_state_allowed()`, `__bch2_dev_set_state()`, and `bch2_dev_set_state()`.
- User-visible management operations: add initialize, remove, add, online, offline, resize.
- Mount-time resize allocation helper `__bch2_dev_resize_alloc()`.
- Name lookup `bch2_dev_lookup()`.
- `bch2_sb_handle_bdev_ops`, the block-layer holder callbacks.

## Integration Notes
`chardev.c` calls the user-visible management functions. Mount/recovery code uses allocation and attach functions. Error handling uses `__bch2_dev_set_state()` to demote devices after sustained write errors.

## Risks and Edge Cases
- Functions that take `state_lock` must be paired with the correct device reference type; the implementation distinguishes normal refs from `ref_outer`.
- `__bch2_dev_set_state()` assumes caller already holds `state_lock`, while `bch2_dev_set_state()` acquires it.
