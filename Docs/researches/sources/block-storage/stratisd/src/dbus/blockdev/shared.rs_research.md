# File Research: sources/block-storage/stratisd/src/dbus/blockdev/shared.rs

Shared blockdev D-Bus property helpers.

Key functions:
- `set_blockdev_prop()`:
  - Gets mutable pool by UUID.
  - Applies a caller-provided async mutation closure.
  - Drops the pool guard before signal emission.
  - Emits a caller-provided signal only when the mutation reports a change.
- `blockdev_prop()`:
  - Gets pool by UUID.
  - Gets blockdev by device UUID.
  - Calls a provided property extraction closure with tier, UUID, and blockdev reference.

This centralizes pool lookup, error mapping, and signal-after-unlock behavior for blockdev interfaces.
