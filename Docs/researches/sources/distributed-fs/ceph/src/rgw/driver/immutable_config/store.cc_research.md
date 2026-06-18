# sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.cc

## Purpose

This file implements `ImmutableConfigStore`, a read-only `ConfigStore` that serves one preconstructed `RGWZoneGroup`, one `RGWZoneParams`, and one `RGWPeriodConfig`. It is used when RGW wants config-store semantics without a mutable persistent config backend.

The implementation returns read-only errors for mutating operations, `-ENOENT` for unsupported realm/period lookups, and returns the configured zonegroup/zone/period config for the small subset of reads needed by a single-zone immutable setup.

## Important APIs, Types, and Functions

- `ImmutableConfigStore::ImmutableConfigStore()` copies the supplied zonegroup, zone, and period config into const members.
- Realm methods reject writes with `-EROFS`, return `-ENOENT` for reads, return an empty list for `list_realm_names()`, and return `nullptr` for watchers.
- Period methods reject create/delete/latest-epoch updates with `-EROFS`, return `-ENOENT` for period reads, and list no period ids.
- `ImmutableZoneGroupWriter` and `ImmutableZoneWriter` implement writer interfaces whose `write()`, `rename()`, and `remove()` all return `-EROFS`.
- Zonegroup read methods return the stored zonegroup by id, name, or default access, and can provide an immutable writer wrapper.
- Zone read methods return the stored zone by id, name, or default access, and can provide an immutable writer wrapper.
- `read_period_config()` returns the stored period config for empty realm id.
- `create_immutable_config_store()` constructs the concrete store behind a `std::unique_ptr<ConfigStore>`.

## Control Flow

Construction captures immutable snapshots of the input config objects. Each API method then either rejects mutation, checks whether the requested id/name matches the stored object, or emits a short list result.

The zonegroup path accepts an empty realm id as the implicit realm. `read_default_zonegroup_id()` returns `zonegroup.id` only when `realm_id` is empty, and `read_default_zonegroup()` always returns the stored zonegroup. The zone path is asymmetric: `read_default_zone_id()` returns `zone.id` only when `realm_id` is non-empty, while `read_default_zone()` returns the stored zone only when `realm_id` is empty.

List methods implement marker-based single-entry listing. If the marker sorts before the stored name, they write the name into `entries[0]`, set `result.next`, and expose one entry; otherwise they return an empty span.

## State and Persistence Behavior

There is no external persistence. All state lives in the store object as const value copies:

- `zonegroup`
- `zone`
- `period_config`

No method mutates those members. Mutating calls consistently return `-EROFS` except realm period notification, which returns `-ENOTSUP`, and create watcher, which returns `nullptr`.

## Dependencies and Integration Points

The implementation depends on `rgw_sal_config.h` through the header, `rgw_zone.h` types, and `rgw_realm_watcher.h` for the watcher return type. It implements the `ConfigStore` interface used by RGW realm/zone/period configuration code and is used by the JSON config store factory after JSON parsing and normalization.

## Risks and Edge Cases

- List methods write `entries[0]` without checking whether the provided span is empty. Callers must supply capacity for at least one entry.
- Realm and period support is intentionally absent. Code paths requiring real realm or period records will see `-ENOENT`/empty lists even though zonegroup and zone reads work.
- The realm-id handling is inconsistent between `read_default_zonegroup_id()`, `read_default_zone_id()`, and `read_default_zone()`, which can surprise callers expecting one implicit realm convention.
- Writer objects are returned even though writes always fail. That is consistent with read-only semantics but can defer failures until later writer use.

## Test Signals

No direct tests are in this file. Coverage is likely indirect through config-store users and JSON config store creation. Useful tests would assert mutation failures, id/name lookup behavior, marker listing, empty-span safety, and the realm-id conventions for default zonegroup/zone reads.
