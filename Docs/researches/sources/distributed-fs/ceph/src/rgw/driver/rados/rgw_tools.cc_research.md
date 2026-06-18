# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.cc` implements common RGW RADOS utility functions for pool/ioctx initialization, raw object references, synchronous or coroutine-aware RADOS operations, system object access, attribute filtering, monitor security checks, cluster log warnings, and pool listing.

## Important APIs, Types, and Functions

`rgw_init_ioctx()` opens or optionally creates a pool, enables the RGW application, sets mostly-omap/bulk pool flags, applies namespace, and enables pool-full try behavior. `rgw_get_rados_ref()` initializes `rgw_rados_ref`. `rgw_rados_ref::watch()` and `unwatch()` provide blocking or yield-context async watch APIs. `rgw_put_system_obj()`, `rgw_get_system_obj()`, `rgw_stat_system_obj()`, and `rgw_delete_system_obj()` wrap `RGWSI_SysObj` reads/writes/stats/removes. `rgw_rados_operate()` overloads and `rgw_rados_notify()` choose async librados calls when `optional_yield` is present. `rgw_filter_attrset()`, `rgw_complete_aio_completion()`, `rgw_check_secure_mon_conn()`, `rgw_clog_warn()`, and `rgw_list_pool()` provide focused helpers.

## Control Flow

Most functions are thin wrappers. The pool init path attempts `ioctx_create`, creates the pool on `-ENOENT` if allowed, reopens it, enables application metadata, optionally sets pool tunables through monitor commands, applies namespace, and returns errors directly. RADOS operate/notify wrappers branch on `optional_yield`: with a yield context they call async librados and convert error codes; otherwise they warn about blocking and call synchronous APIs. Pool listing parses an object cursor, iterates up to `max`, filters object names, updates the marker, and reports truncation.

## State and Persistence Behavior

The utilities can create pools, set pool properties, write/delete system objects, perform raw object operations, and emit cluster log messages. `no_change_attrs()` returns a static sentinel map used by `rgw_put_system_obj()` to distinguish preserving attributes from clearing attributes. `rgw_rados_ref` stores an ioctx plus raw object reference and may hold watch registrations.

## Dependencies and Integration Points

This file depends on librados, librados_asio, RGW system object service, RGW aio helpers, auth registry, Ceph monitor commands, RGW pool/object types, and optional coroutine yield contexts. It is a shared substrate used by sync, trim, metadata, bucket, and system-object code throughout the RADOS driver.

## Risks and Edge Cases

Pool creation partially succeeds before later monitor tuning commands can fail; mostly-omap tuning failures are logged but not fatal. The async wrappers return negative `ec.value()` while synchronous APIs return librados negatives, so consistency relies on error-code conventions. `rgw_list_pool()` returns `-ENOENT` for an empty/end iterator, which callers must treat appropriately. The `no_change_attrs()` sentinel relies on pointer identity.

## Test Signals

Tests should cover create-existing/missing pool paths, namespace application, mostly-omap and bulk command failures, coroutine versus blocking operate/notify results, system object attr preservation with `no_change_attrs()`, secure/insecure auth method detection, pool listing markers/truncation/filtering, and watch/unwatch with and without yield.
