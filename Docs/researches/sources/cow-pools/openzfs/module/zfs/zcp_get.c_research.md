# File Research: sources/cow-pools/openzfs/module/zfs/zcp_get.c

## Summary
Implements the `zfs.get_prop()` Lua binding for channel programs. It retrieves user properties, system properties, user quota properties, and `written@` properties, returning value plus source.

## Main Responsibilities
- Determines dataset type as filesystem, volume, or snapshot.
- Validates whether a property applies to a dataset.
- Retrieves special in-memory or computed properties directly.
- Falls back to DSL property ZAP lookup for ordinary system properties.
- Retrieves user-defined properties.
- Retrieves kernel-only user/group quota and used properties.
- Computes `written@` values between datasets/snapshots.
- Registers `get_prop` into the ZCP Lua namespace.

## Key APIs
- `zcp_load_get_lib()`
- `prop_valid_for_ds()`
- Internal helpers: `zcp_get_prop()`, `zcp_get_system_prop()`, `zcp_get_user_prop()`, `zcp_get_written_prop()`

## Important Behavior
Special properties are handled directly for values such as `used`, `referenced`, `available`, `clones`, `type`, `name`, `mountpoint`, `volsize`, encryption state, `snapshots_changed`, counts, and receive resume tokens.

Property source reporting returns nil for readonly properties and `version`; otherwise it returns `default` for empty setpoints or the setpoint dataset name.

For all-boolean nvlist-like results, such as clone lists, conversion through ZCP can yield Lua arrays rather than key/value tables.

## State and Synchronization
Most lookups hold a `dsl_dataset_t` by name through `zcp_dataset_hold()` and release it before returning. Kernel-only quota lookup creates a transient `zfsvfs_t` around the objset to call userspace accounting helpers.

## Risks
Several errors are fatal Lua errors, while absent/inapplicable properties return no values. Temporary property lookup is kernel-only. User quota parsing accepts numeric IDs and SID-like strings and must free allocated domain strings correctly.
