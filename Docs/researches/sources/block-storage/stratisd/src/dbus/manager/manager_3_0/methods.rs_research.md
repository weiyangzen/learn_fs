# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/methods.rs

Method implementations for manager r0/r1 and shared manager operations.

Key behavior:
- Key handling:
  - `list_keys_method()` lists key descriptions.
  - `set_key_method()` stores key material from an fd and reports created/value-changed/identity.
  - `unset_key_method()` removes key mapping.
- Pool creation:
  - Converts D-Bus optional key/Clevis tuples.
  - Parses Clevis JSON.
  - Uses legacy encryption info and default integrity spec.
  - Calls `engine.create_pool`.
  - Registers pool and child filesystem paths on creation.
- Pool destruction:
  - Resolves pool UUID from object path.
  - Captures blockdev/filesystem UUIDs before destruction.
  - Calls `engine.destroy_pool`.
  - Unregisters blockdevs, filesystems, and pool object.
- Unlock:
  - Parses pool UUID.
  - Calls `engine.unlock_pool`.
  - Emits locked-pools signal on start.
- Report:
  - Serializes `engine.engine_state_report()` to JSON string.

D-Bus style:
- All methods return Stratis D-Bus result tuples with `DbusErrorEnum` code and return string.
