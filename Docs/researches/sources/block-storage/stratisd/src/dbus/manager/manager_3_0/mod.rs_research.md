# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_0/mod.rs

D-Bus interface `org.storage.stratis3.Manager.r0`.

Exposes:
- Properties:
  - `Version`
  - `LockedPools`
- Methods:
  - `ListKeys`
  - `SetKey`
  - `UnsetKey`
  - `CreatePool`
  - `DestroyPool`
  - `UnlockPool`
  - `EngineStateReport`

Important details:
- Holds engine, connection, manager, and object-path counter.
- `CreatePool` still accepts a `redundancy` argument but does not use it.
- Registers the manager object at `/org/storage/stratis3`.

This is the early top-level D-Bus management API.
