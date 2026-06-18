# sources/distributed-fs/ceph/src/librados/RadosClient.cc

## Purpose

`RadosClient.cc` implements the cluster-level librados client. It owns connection setup and teardown, monitor and manager clients, messenger, `Objecter`, OSD map waiting, pool lookup and management, command dispatch, monitor log subscription, service-daemon registration, and runtime config observation for librados threading and monitor-operation timeout.

## Important APIs, Types, and Functions

The implementation covers `RadosClient::connect()`, `shutdown()`, destructor, `create_ioctx()`, `lookup_pool()`, `pool_get_name()`, pool alignment helpers, `get_fsid()`, `ping_monitor()`, `watch_flush()` and async watch flush, compatibility queries, dispatcher callbacks, `wait_for_osdmap()`, `wait_for_latest_osdmap()`, pool list/stats/create/delete/base-tier/self-managed-snap-mode helpers, `get_fs_stats()`, refcount `get()`/`put()`, blocklist helpers, mon/mgr/osd/pg command wrappers, monitor log subscription and delivery, service-daemon registration/update, inconsistent-PG query parsing, and `handle_conf_change()`.

## Control Flow and Data Flow

`connect()` transitions `DISCONNECTED -> CONNECTING -> CONNECTED`. It starts logging, bootstraps monmap/config, starts the async IO context pool, builds the initial monmap, creates a client messenger, requires `CEPH_FEATURE_OSDREPLYMUX`, constructs and starts `Objecter`, wires dispatchers, initializes and authenticates `MonClient`, configures `MgrClient`, starts subscriptions, optionally registers service metadata, starts `Objecter`, and records the monitor-assigned global id. On error it resets state and deletes partially created `Objecter`/messenger.

Normal operations first ensure a valid OSD map with `wait_for_osdmap()` or request the latest map with `wait_for_latest_osdmap()`. Pool and stats calls read `OSDMap` under `objecter->with_osdmap()` or issue Objecter requests with blocked completions. Command wrappers marshal vectors and bufferlists to MonClient, MgrClient, or Objecter and translate `boost::system::error_code` to negative errno. Message dispatch handles OSD map notifications by waking waiters and monitor log messages by invoking registered callbacks.

## State and Persistence Behavior

The object is process-local but controls persistent cluster operations: pool create/delete, blocklist entries, manager service records, monitor commands, and OSD/PG commands. Persistent identity is `instance_id`, the monitor global id assigned after authentication. Local state includes connection state, messenger and objecter pointers, log subscription state, daemon registration metadata, reference count, timeout, and thread pool. `shutdown()` flushes watch callbacks before stopping Objecter, manager, monitor, messenger, and pool threads.

## Dependencies and Integration Points

Dependencies include `CephContext`, `ConfigProxy`, `MonClient`, `MgrClient`, `Messenger`, `Objecter`, Ceph async blocked completions, JSON parsing, message types such as `MLog`, and librados completion types. It integrates with `librados_c.cc` cluster functions, C++ `Rados`, `IoCtxImpl`, watch/notify callback flushing, service-daemon status, monitor log subscriptions, and config observer infrastructure.

## Risks and Edge Cases

State transitions are sensitive: some methods assume `state == CONNECTED`, and `wait_for_osdmap()` returns `-ENOTCONN` otherwise. `connect()` mutates state without holding `lock` throughout, so callers must respect external connection serialization. `mgr_command()` manually unlocks/relocks around waits while using a `lock_guard`, which is unusual and relies on Ceph mutex semantics/macros. OSD map waits can block indefinitely when timeout is zero. Monitor log delivery runs under client lock, so callbacks must avoid deadlocks. `blocklist_add()` falls back to legacy blacklist command on `-EINVAL`.

## Test Signals

Tests should cover connect/shutdown success and injected failures, double connect return codes, create_ioctx by name and id, pool lookup retry after latest map, OSD map wait timeout, pool stats mapping, pool create/delete async completions, mon/mgr/osd/pg commands, monitor log callback versions and stop behavior, blocklist fallback, service registration before and after connect, inconsistent-PG JSON variants, and config changes resizing `poolctx`.
