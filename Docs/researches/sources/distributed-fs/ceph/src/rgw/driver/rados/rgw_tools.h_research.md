# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_tools.h` declares shared RGW RADOS helper APIs and inline/asynchronous helpers used across the RADOS-backed RGW driver.

## Important APIs, Types, and Functions

The header declares pool/ioctx helpers (`rgw_init_ioctx()`, `rgw_shard_id()`, `rgw_shard_name()`), system object helpers, MIME lookup, attr filtering, RADOS operate/notify wrappers, `rgw_rados_ref`, tool init/cleanup, aio completion helper, `no_change_attrs()`, monitor security and cluster log helpers, and `rgw_list_pool()`. It also defines `rgw::mostly_omap` and `rgw::create` tag types plus Boost.Asio composed operations: `set_mostly_omap()`, `create_pool()`, and several `init_iocontext()` overloads for neorados.

## Control Flow

Inline sharding helpers compute stable shard ids from Ceph string hashes and prime modulo schemes. `rgw_rados_ref` methods forward operations to the declared wrappers. The Asio composed operations perform coroutine-style lookup/create/configure flows: create pool, enable RGW application, optionally set mostly-omap tunables, look up pool ids, set namespaces, and return `neorados::IOContext` or error codes through the completion token.

## State and Persistence Behavior

The header declares helpers that create pools, initialize IO contexts, operate on RADOS objects, and update monitor pool settings. `rgw_rados_ref` instances carry an `IoCtx` and raw object. The inline neorados helpers may persist pool creation and pool configuration through monitor commands.

## Dependencies and Integration Points

Dependencies include Boost.Asio composed operations, fmt, neorados, Ceph hash/types/time/dout, OSD pool types, RGW object/pool/common types, librados, and optional yield contexts. The header is a broad integration point for legacy librados code and newer neorados coroutine code.

## Risks and Edge Cases

Because this header contains template coroutine implementations, compile errors or behavior changes affect many translation units. The monitor command JSON for setting recovery priority appears sensitive to exact formatting. Error handling maps exceptions to generic `EIO` in several paths, which can hide specific causes. Shard modulo constants are compatibility-sensitive and should not change casually.

## Test Signals

Compile coverage across librados and neorados users is essential. Behavioral tests should cover shard distribution compatibility, async pool create/init paths, existing pool handling, namespace propagation, mostly-omap tuning, and error conversion from system exceptions.
