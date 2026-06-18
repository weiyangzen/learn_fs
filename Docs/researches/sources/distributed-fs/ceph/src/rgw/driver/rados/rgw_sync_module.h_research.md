# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.h

## Purpose
This header defines extension interfaces for RGW sync modules. Modules can provide data-sync behavior, REST filters, metadata handler overrides, write support flags, data export support, and custom object stat callback flows.

## Important APIs, Types, and Functions
- `RGWDataSyncModule` is the data-plane interface with optional `init()`, `init_sync()`, `start_sync()`, and required `sync_object()`, `remove_object()`, and `create_delete_marker()`.
- `RGWSyncModuleInstance` represents a configured module instance and exposes the data handler, REST filter, user-write support, metadata handler allocation, and `should_full_sync()`.
- `RGWSyncModule` is the module factory with write/export capability flags and `create_instance()`.
- `RGWSyncModulesManager` stores named module factories under a mutex, supports default module registration by empty name, lookup, data-export capability checks, instance creation, and listing names.
- `RGWStatRemoteObjCBCR` and `RGWCallStatRemoteObjCR` define a callback-capable remote object stat coroutine pattern.

## Control Flow
Service initialization registers modules in a manager. Zone or sync configuration names a module, and the manager creates an instance from JSON configuration. Data sync calls the instance's data handler for object replication, deletion, and delete-marker creation. Metadata setup can ask the instance to allocate module-specific bucket metadata handlers. REST requests can be filtered by module-provided REST managers.

## State and Persistence Behavior
The manager keeps module factories in memory. Module instances may own configuration and persistent behavior indirectly through data handlers and metadata handlers. `should_full_sync()` defaults to true, so modules opt out only when incremental-only startup is safe.

## Dependencies and Integration Points
The header depends on librados forwards, RGW common types, coroutine support, bucket info, data sync context/environment, bucket sync pipes, REST managers, metadata handlers, bucket services, zone services, bucket index, bucket control, and datalog service. It is the contract used by default, archive, log, Elasticsearch, and cloud sync modules.

## Risks
- Required data-sync methods are pure virtual, but behavioral compatibility is module-specific.
- `get_registered_module_names()` is const and does not lock in the header, so concurrent registration/listing assumptions should be checked.
- Default module registration under empty string gives empty config names special behavior.
- Incorrect write capability flags can expose unsupported paths.

## Test Signals
Tests should cover registration/lookup, default module lookup, missing module instance creation, capability flags, metadata handler overrides, full-sync opt-out behavior, and data-sync coroutine behavior for object copy/delete/delete-marker flows.
