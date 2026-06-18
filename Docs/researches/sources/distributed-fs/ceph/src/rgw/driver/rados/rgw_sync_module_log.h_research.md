# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module_log.h` declares the diagnostic log sync module.

## Important APIs, Types, and Functions

`RGWLogSyncModule` derives from `RGWSyncModule`, reports no data export support, and exposes `create_instance()` for module registration.

## Control Flow

The header has no executable flow. RGW module registration calls into the implementation to create an instance whose data handler logs sync events.

## State and Persistence Behavior

No state is declared in the header. The implementation stores only a log prefix and writes no persistent data.

## Dependencies and Integration Points

It depends on `rgw_sync_module.h` and the generic RGW sync module interface.

## Risks and Edge Cases

The class shape is intentionally minimal. The main risk is accidental use in a path expecting actual data export or deletion behavior.

## Test Signals

Compile coverage and module instantiation from JSON config are sufficient header-level signals; behavior is covered in the `.cc` diagnostic logging tests.
