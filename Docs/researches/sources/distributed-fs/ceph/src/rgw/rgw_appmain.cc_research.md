# sources/distributed-fs/ceph/src/rgw/rgw_appmain.cc

## Purpose
Implements `rgw::AppMain`, the main orchestration object for RGW process initialization and shutdown: frontends, storage, REST APIs, auth, logs, performance counters, HTTP clients, realm reloaders, Lua, dedup, KMS cache, and service-map registration.

## Important APIs, Types, and Functions
- `init_frontends1()` parses frontend config and handles legacy region-to-zonegroup settings.
- `init_storage()` creates config store, loads site, and creates the storage driver with configured background threads.
- `cond_init_apis()` registers S3, Swift, Swift auth, admin, zero, and related REST resources based on `rgw_enable_apis`.
- `init_frontends2()` creates frontend objects, scheduler/rate limiter/auth registry, starts frontends, registers service map, and installs realm watchers/reloaders.
- `shutdown()` tears subsystems down in dependency order.

## Control Flow
Initialization is staged. Frontend config parsing happens early so global config can be finalized. Storage setup loads site configuration and starts driver-managed services. API registration is conditional on HTTP frontend presence and enabled API names. Frontend startup applies default frontend config, instantiates matching frontend classes (`beast`, `loadgen`, `rgw-nfs`, optional Arrow Flight), initializes and runs each, then registers the daemon in the service map. For RADOS-backed drivers, realm watchers can pause/reload frontends, Lua background work, and dedup background work.

## State and Persistence
`AppMain` owns runtime objects: frontend configs/frontends, config store, site, driver environment, REST registry, auth registry, rate limiter, scheduler context, logs, LDAP helper, KMS cache, Lua/dedup backgrounds, realm watcher/reloader, and IO context pool. Persistent effects include service-map registration, ops log sinks, driver-managed background services, and possible Lua package installation.

## Dependencies and Integration Points
This file integrates much of RGW: global config, DriverManager, REST managers, frontends, auth strategies, dmclock scheduler, curl/HTTP/KMIP clients, perf counters, tracepoints, LDAP, ops logging, Lua, dedup, realm notification, and NFS mode.

## Risks and Edge Cases
Initialization order matters: storage and site must exist before REST/auth, frontends cannot be deleted before IO contexts finish, and request handling must stop before storage closes. Some errors are fatal while service-map registration errors are logged and ignored. Swift-at-root conflicts with S3 registration. `rgw_keystone_admin_password` warning highlights plaintext secret risk. Shutdown assumes `env.driver` exists and follows the expected initialization path.

## Test Signals
Integration tests should cover frontend parsing defaults, bad frontend configs, API enable/disable combinations, Swift-at-root conflicts, storage-driver creation failure, service-map registration failure tolerance, realm reload setup, NFS background-thread flags, and shutdown ordering under active frontends.
