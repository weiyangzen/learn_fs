<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.cc

Purpose: Implements creation and startup of RGW sync module instances for the local zone tier type.

Important APIs, types, and functions: `init()` creates `RGWSyncModulesManager` and registers built-in sync modules through `rgw_register_sync_modules()`. `do_start()` reads the zone's public config tier type and zone params tier config, then calls `create_instance()`. The destructor deletes the manager.

Control flow: After initialization with zone service, startup creates the module instance. On `-ENOENT`, it logs registered module names for diagnostics. On success, `sync_module` is available through the header accessor.

State and persistence: In-memory manager and module instance only. Persistent tier config comes from zone params.

Dependencies and integration points: Depends on `RGWSI_Zone`, `RGWSyncModulesManager`, sync module registration, and tier config. Zone startup later queries manager capabilities and module instance behavior.

Risks and test signals: Missing or misspelled tier types prevent RGW startup. Tests should verify default tier starts, invalid tier returns `-ENOENT` with useful diagnostics, and module capability flags match zone decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.cc -->
