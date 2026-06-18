# sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.cc

Purpose: Implements a RADOS watch-backed `RGWRealmWatcher` that listens on a realm control object and dispatches decoded realm notifications to registered watcher handlers.

Important APIs/types/functions: `RadosRealmWatcher` constructor starts the watch unless the realm id is empty. `handle_notify()` acknowledges notifications and decodes a sequence of `RGWRealmNotify` messages from the payload. `handle_error()` restarts the watch. `watch_start()`, `watch_restart()`, and `watch_stop()` manage librados `watch2`/`unwatch2`. `RadosConfigStore::create_realm_watcher()` constructs it.

Control flow: Startup opens an ioctx for `realm.get_pool(cct)`, registers `watch2()` on `realm.get_control_oid()`, and stores the oid/handle. Notifications with nonmatching cookies are ignored; matching notifications are acked then decoded until payload end, dispatching by notification enum. Watch errors trigger unwatch and re-watch on the same oid.

State/persistence: This file does not persist data, but it holds live watcher state: `pool_ctx`, `watch_handle`, and `watch_oid`. The watched object is the control object created by realm storage code.

Dependencies/integration: Depends on librados `WatchCtx2`, `RGWRealmWatcher` base dispatch map, realm pool/control oid helpers, `ConfigImpl`-owned Rados client, and RADOS notify payloads emitted by `realm_notify_new_period()`.

Risks: Startup failures call `rados.shutdown()` on the shared client in some paths, which is sensitive if the client is used elsewhere. Dispatch stops at the first unknown notification. Restart clears the watch on failure and does not schedule later retries. Notify ack errors are ignored.

Test signals: Cover empty realm id disabling, successful watch/notify dispatch, unknown notify handling, corrupt payload decode, cookie mismatch, watch restart success/failure, and shutdown unwatch.
