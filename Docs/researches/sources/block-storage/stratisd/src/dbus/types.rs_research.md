# File Research: sources/block-storage/stratisd/src/dbus/types.rs

This file defines D-Bus-facing wrapper types, signatures, and conversions for Stratis engine types.

Key definitions:
- `FilesystemSpec<'a>`:
  - D-Bus input type for filesystem creation specs: name plus optional size and optional size limit.
- `ManagerR2<T>` and `ManagerR8<T>`:
  - marker wrappers indicating which manager interface revision a value is returned from.
- `DbusErrorEnum`:
  - numeric method return code enum: `OK = 0`, `ERROR = 1`.

D-Bus type conversions:
- Implements `zvariant::Type` and `From<...> for Value` for:
  - `LockedPoolsInfo`
  - `ManagerR2<StoppedPoolsInfo>`
  - `ManagerR8<StoppedPoolsInfo>`
  - `PoolUuid`
  - `ActionAvailability`

Locked pool representation:
- Converts locked pools into a nested dictionary keyed by pool UUID.
- Per-pool dictionary includes:
  - key description result/option tuple
  - Clevis info result/option tuple
  - devices with devnode and device UUID
  - optional pool name

Stopped pool representation:
- Shared helper `stopped_pools_to_value()` includes stopped and partially constructed pools.
- Always includes devices and optional pool name.
- When metadata is requested, includes:
  - `metadata_version`
  - `features`, including encryption/key-description/Clevis flags when present.
- r2 conversion omits metadata/features.
- r8 conversion includes metadata/features.

Role in architecture:
- This file is the ABI conversion layer for complex manager-returned state. It preserves revision-specific D-Bus payload differences while deriving values from common engine structures.
