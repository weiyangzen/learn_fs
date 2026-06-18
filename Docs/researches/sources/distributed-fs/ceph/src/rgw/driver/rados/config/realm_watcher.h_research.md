# sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.h

Purpose: Declares the RADOS-specific realm watcher type used by the config store for dynamic RGW realm reconfiguration.

Important APIs/types/functions: `RadosRealmWatcher` derives from `RGWRealmWatcher` and `librados::WatchCtx2`. Public overrides are `handle_notify()` and `handle_error()`. Private helpers are `watch_start()`, `watch_restart()`, and `watch_stop()`.

Control flow: Construction receives a `DoutPrefixProvider`, `CephContext`, librados client, and realm. The class stores one ioctx, watch handle, and oid, and the destructor stops the watch.

State/persistence: The class is live state only; it watches a persistent realm control object but does not encode or write metadata itself.

Dependencies/integration: Includes `rgw_realm_watcher.h` and librados. It is constructed from `RadosConfigStore` and receives notifications emitted by realm config writes.

Risks: The class owns watch lifecycle but not the Rados client. Lifetime ordering must ensure the shared Rados client and `CephContext` outlive the watcher.

Test signals: Compile-time interface compatibility with `WatchCtx2`; runtime tests for destructor cleanup and callback dispatch through the base watcher registry.
