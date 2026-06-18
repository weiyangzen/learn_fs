# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/methods.rs

Filesystem r0 method implementation for renaming.

Key behavior:
- `set_name_method()` gets mutable pool by parent pool UUID.
- Calls `pool.rename_filesystem`.
- Maps `RenameAction` into D-Bus result tuple:
  - `Renamed` returns changed filesystem UUID.
  - `Identity` returns OK unchanged.
  - `NoSource` returns error.
- Sends filesystem name change signal through manager path lookup after a successful rename.
- Uses `handle_action!` for action logging.

This method is reused by later filesystem revisions.
