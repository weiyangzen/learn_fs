<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.h

Purpose: Declares RGW's sync module service.

Important APIs, types, and functions: `RGWSI_SyncModules` derives from `RGWServiceInstance`, owns `RGWSyncModulesManager*`, `RGWSyncModuleInstanceRef`, and a zone service pointer. It exposes `get_manager()`, `init()`, `do_start()`, and `get_sync_module()`.

Control flow: `init()` registers modules, startup creates the configured module instance, and other services query the manager or active module reference.

State and persistence: The service owns only in-memory module registry and module instance. Zone config persists the selected tier type/config.

Dependencies and integration points: Depends on RGW sync module framework and zone service. Zone service uses it to determine write/data-export support and to build sync relationships.

Risks and test signals: Manual `new`/`delete` manager ownership is simple but order-sensitive. Tests should cover destructor after partial initialization and startup failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.h -->
