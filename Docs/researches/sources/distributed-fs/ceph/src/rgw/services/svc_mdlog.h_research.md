<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.h

Purpose: Declares RGW's metadata log service and its period-history API.

Important APIs, types, and functions: `RGWSI_MDLog` derives from `RGWServiceInstance`, owns a map of per-period `RGWMetadataLog` objects, the current log pointer, sync flags, period puller/history, config store, RADOS and async processor pointers, and service dependencies. It exposes lifecycle setup, oldest-period discovery/init/read/trim coroutine APIs, history read/write, entry add/complete, shard lookup, period pull, and `get_log()`.

Control flow: Consumers initialize the service with zone/sysobj/cls/async dependencies, start it, then use `add_entry()` or `complete_entry()` for current-period mutations and the period-history APIs for sync trimming.

State and persistence: In-memory state tracks loaded period logs and period history helpers. Persistent state is metadata log objects and the metadata log history object in the log pool.

Dependencies and integration points: Depends on RGW period history/puller, metadata log classes, coroutine type, zone/sysobj/cls services, and SAL config store.

Risks and test signals: The API assumes `current_log` is initialized before add/shard calls. Service-order tests should verify zone and sysobj startup precede mdlog use; sync tests should verify coroutine paths update object versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.h -->
