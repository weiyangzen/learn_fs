# File Research: sources/block-storage/stratisd/src/dbus/filesystem/shared.rs

Shared filesystem D-Bus property helpers.

Key functions:
- `set_filesystem_prop()`:
  - Gets mutable pool by UUID.
  - Applies a caller-provided async mutation closure.
  - Drops the lock before sending change signals.
  - Sends signal only when changed.
- `filesystem_prop()`:
  - Gets pool by UUID.
  - Finds filesystem by filesystem UUID.
  - Passes pool name, filesystem name, filesystem UUID, and filesystem reference to an extraction closure.

This centralizes lookup, locking, and signal discipline for filesystem D-Bus properties.
