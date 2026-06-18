# sources/distributed-fs/ceph/src/rgw/rgw_realm.cc

## Purpose

Implements core `RGWRealm` helpers for realm pool selection, control object naming, zone lookup in the current period, and formatter/JSON support.

## Important APIs, Types, and Functions

Defines defaults under `rgw_zone_defaults`: realm info/name object prefixes, default realm info object, and default root pool. Implements `RGWRealm::get_pool()`, `get_info_oid_prefix()`, `get_control_oid()`, `find_zone()`, `generate_test_instances()`, `dump()`, and `decode_json()`.

## Control Flow and Data Flow

`get_pool()` returns configured `rgw_realm_root_pool` or `rgw.root`. `get_control_oid()` appends the realm id to the realm info prefix and `.control`. `find_zone()` reads the current period from the config store, asks the period to find the requested zone, and returns the period and zonegroup only when found.

## State and Persistence Behavior

The file does not mutate realm state. It reads period metadata through `rgw::sal::ConfigStore::read_period()` using `current_period`. Realm fields `id`, `name`, `current_period`, and `epoch` are serialized through JSON formatter/decode helpers elsewhere in the type.

## Dependencies and Integration Points

Depends on zone/period types, realm watcher declarations, config store, system object service, Ceph JSON and formatter helpers, and logging. Integrated with multisite period/zone discovery and realm notification object naming.

## Risks and Edge Cases

`get_info_oid_prefix(bool old_format)` ignores `old_format`, so callers expecting legacy naming behavior should be checked. `find_zone()` requires `pfound`, `pperiod`, and `cfgstore` to be valid pointers. If period read fails, zone lookup is skipped and the error propagates.

## Test Signals

Cover default versus configured root pool, control object naming, period read failure, zone found/not found, JSON decode/dump fields, and compatibility expectations for old-format prefix callers.
