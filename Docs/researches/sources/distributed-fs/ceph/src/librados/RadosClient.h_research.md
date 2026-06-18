# sources/distributed-fs/ceph/src/librados/RadosClient.h

## Purpose

`RadosClient.h` declares the internal cluster client class that underpins librados C and C++ APIs. It exposes cluster lifecycle, pool lookup/management, command routing, watch flushing, service-daemon status, monitor-log subscription, configuration observation, and creation of per-pool `IoCtxImpl` handles.

## Important APIs, Types, and Functions

`librados::RadosClient` inherits from `Dispatcher` and `md_config_obs_t`. Key members are `CephContext` ownership through `cct_deleter`, `conf`, `poolctx`, connection `state`, `MonClient`, `MgrClient`, `Messenger*`, `instance_id`, `Objecter*`, `lock`, `cond`, `refcnt`, monitor-log callback fields, service-daemon metadata, and `rados_mon_op_timeout`. Public methods include `connect()`, `shutdown()`, `ping_monitor()`, `watch_flush()`, `async_watch_flush()`, compatibility queries, `wait_for_latest_osdmap()`, `create_ioctx()`, fsid/pool lookup and alignment helpers, pool list/stats/create/delete, command wrappers, log monitoring, intrusive `get()`/`put()`, blocklist, service-daemon calls, monitor feature query, inconsistent-PG lookup, and config observer overrides.

## Control Flow and Data Flow

The header makes `RadosClient` the owner of the network path. Messages arrive through `Dispatcher` overrides, are filtered by connection state, and are routed to `_dispatch()`. Public wrappers typically validate state, wait for OSD maps, then read from `OSDMap` or submit commands through MonClient, MgrClient, or Objecter. `create_ioctx()` transfers the client/objecter/pool identity into a new `IoCtxImpl`.

## State and Persistence Behavior

Persistent cluster effects are exposed through methods but not stored in the class except as local identity and subscription metadata. The class owns long-lived runtime resources: messenger, objecter, monitor/mgr clients, async thread pool, config observer registration, monitor log watch string, callback pointers, and optional service-daemon metadata that can be registered after connect.

## Dependencies and Integration Points

It depends on Ceph messenger, monitor and manager clients, config observer APIs, common mutex/condition/time helpers, librados public headers, and `IoCtxImpl.h`. It grants friendship to `neorados::detail::RadosClient`, indicating newer neorados internals share access. It is included by `librados_c.cc`, `librados_cxx.cc`, and other librados internals.

## Risks and Edge Cases

The class mixes manual pointer ownership (`messenger`, `objecter`) with RAII ownership (`cct_deleter`), so shutdown/destructor ordering matters. `refcnt` is protected by `lock` and separate from object lifetime controlled by callers. Callback pointers for monitor logs are raw C function pointers and arguments. Methods that expose `rados_t`/`rados_config_t` must not outlive the client. Config changes can stop/start the IO pool while operations are active.

## Test Signals

Header-level coverage comes from API and integration tests that exercise each declared method: connection lifecycle, IoCtx creation, pool metadata, command routing, watch flushing, logging callbacks, service registration, refcount balance, config-change observer behavior, and message dispatch under disconnect.
