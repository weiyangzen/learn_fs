# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/methods.rs

D-Bus method implementation for blockdev r0 user info mutation.

Key behavior:
- `set_user_info_method()` gets the mutable pool by UUID.
- Converts D-Bus optional tuple to Rust `Option<&str>`.
- Calls `pool.set_blockdev_user_info`.
- Maps `RenameAction` to D-Bus result tuple:
  - `Renamed` returns changed with blockdev UUID.
  - `Identity` returns OK unchanged.
  - `NoSource` returns error.
- Uses `handle_action!` for action logging.

This is the method-style API used before later revisions make user info a writable property.
