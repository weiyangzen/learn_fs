# File Research: sources/block-storage/stratisd/src/dbus/pool/shared.rs

This file provides shared D-Bus helper functions for reading and setting pool properties.

Key functions:
- `get_pool()`:
  - resolves a pool by UUID through `Engine::get_pool`;
  - returns a read guard or zbus FDO `Failed` error.
- `get_pool_mut()`:
  - resolves a mutable pool guard through `Engine::get_mut_pool`;
  - returns a write guard or zbus failure.
- `pool_prop()`:
  - generic read-property adapter;
  - gets a read guard and applies a supplied property function.
- `set_pool_prop()`:
  - generic write-property adapter;
  - gets a write guard, calls a supplied async setter, drops the guard, then emits a supplied signal only if the setter reported a change.

Important design point:
- `set_pool_prop()` releases the pool lock before sending D-Bus signals. This avoids holding engine/pool locks while performing object-server signaling work.

Role in architecture:
- This file removes repeated guard-resolution and signal-on-change boilerplate from versioned pool interfaces.
