<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_notify.cc

Purpose: Implements RGW's RADOS watch/notify service for distributing cache invalidation/update messages across RGW instances.

Important APIs, types, and functions: `RGWWatcher` implements `librados::WatchCtx2` and `DoutPrefixProvider`, handling notify callbacks, errors, watch registration, unregistration, and reinitialization. `RGWSI_Notify::init_watch()` creates control objects and registers watchers. `finalize_watch()` unregisters them. `do_start()`, `shutdown()`, `add_watcher()`, `remove_watcher()`, `watch_cb()`, `distribute()`, `robust_notify()`, `register_watch_cb()`, and `schedule_context()` provide the service behavior. `decode_timeouts()` parses librados notify replies to report timed-out watchers.

Control flow: Startup starts zone service, starts a `Finisher`, reads notify timeout injection and retry settings, chooses the control pool, creates control objects, and registers one watcher per configured control oid using spawn throttle. A watcher receiving a notification calls the registered callback and acks. Watch errors remove the watcher, disable the cache if the full watcher set was previously active, and schedule reinit through the finisher. `distribute()` hashes a key to a control object and sends a robust notify. On timeout, `robust_notify()` retries with an invalidation-only payload up to the configured limit.

State and persistence: Control objects live in the zone control pool under `notify` or `notify.<n>`. In-memory state tracks watcher vector, active watcher set, callback, enabled state, retry counters, finisher, and finalized flag. Notification payloads are transient bufferlists.

Dependencies and integration points: Depends on `RGWSI_Zone`, `librados`, `RGWCacheNotifyInfo`, Ceph async spawn throttle, `Finisher`, and object cache callbacks. `RGWSI_SysObj_Cache` registers as a callback consumer.

Risks and test signals: Reinit loops abort after more than 100 retries. Cache is enabled only when all watchers are active and disabled on loss. `distribute()` guards against division by zero before watchers initialize. Tests should cover multi-control-object startup, watcher loss/reinit, cache enable/disable callback propagation, notify timeout retry/invalidation behavior, injected timeout probability, and clean shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.cc -->
