# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/dev.h

This header declares the device-management API.

Key elements:
- Device-list formatting and open-filesystem lookup.
- Membership validation with `bch2_dev_in_fs()`.
- IO ref, sysfs, allocation, attach, offline, free, and unlink helpers.
- State transition helpers:
  - `bch2_dev_state_allowed()`
  - `__bch2_dev_set_state()`
  - `bch2_dev_set_state()`
- Administrative operations:
  - remove
  - add
  - online
  - offline
  - resize
- Mount-time resize allocation helper.
- Name lookup and block holder ops export.

Role:
- Shared by chardev ioctls, error handling, filesystem lifecycle, and block-device holder callbacks.
