<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_notify.h

Purpose: Declares the RGW notify service interface and callback contract for watch/notify-driven cache coherency.

Important APIs, types, and functions: `RGWSI_Notify` owns zone/RADOS pointers, a `Finisher`, watcher synchronization, control pool, watcher collection, retry settings, callback pointer, and lifecycle helpers. Nested abstract `CB` declares `watch_cb()` and `set_enabled()`. Public API includes constructor, destructor, `distribute()`, and `register_watch_cb()`.

Control flow: The service is initialized by `RGWServices_Def`, started to register watchers, and used by cache services to distribute `RGWCacheNotifyInfo` messages. Registered callbacks receive watch events and enabled-state transitions.

State and persistence: Watcher state is in memory; control objects are persistent RADOS objects in the control pool. The callback is not owned by this service.

Dependencies and integration points: Depends on RGW service base, `Finisher`, RADOS helpers, and `RGWCacheNotifyInfo`. Integrated with `RGWSI_SysObj_Cache`.

Risks and test signals: Callback lifetime must exceed registration or be cleared by service shutdown order. Tests should check startup/shutdown idempotence and callback behavior when watchers are partially registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.h -->
