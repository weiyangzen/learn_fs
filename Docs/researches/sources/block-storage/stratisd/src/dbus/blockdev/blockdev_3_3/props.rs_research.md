# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_3/props.rs

Additional blockdev property helpers for r3+.

Key behavior:
- `new_physical_size_prop()` returns optional detected new size as `(bool, String)`.
- `set_user_info_prop()` compares current user info before mutating, returning whether a property signal is needed.
- Uses `pool.set_blockdev_user_info` for actual mutation.
- `send_user_info_signal_on_change()` resolves the blockdev object path from manager and sends the user-info changed signal.

This file supports the writable-property API introduced in blockdev r3.
