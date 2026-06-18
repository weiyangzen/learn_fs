# sources/distributed-fs/ceph/src/rgw/rgw_sal_config.h

## Purpose
`rgw_sal_config.h` declares the SAL configuration-store interface for realm, period, zonegroup, zone, and period-config metadata. It abstracts how multisite topology configuration is persisted so RADOS, dbstore, JSON, or other implementations can share higher-level zone/realm logic.

## Important APIs, Types, and Functions
`ListResult<T>` returns a subspan of caller-provided entries plus a next marker. `ConfigStore` groups virtual operations by metadata domain. Realm methods manage default realm id, create/read realm by id/name/default, read a realm id by name, notify new periods, create realm watchers, and list realm names. Period methods create/read/delete/list periods and update latest epoch. Zonegroup methods manage default zonegroup ids, create/read zonegroups, and list names. Zone methods manage default zone ids, create/read zones by id/name/default, and list names. Period-config methods read and write `RGWPeriodConfig`.

`RealmWriter`, `ZoneGroupWriter`, and `ZoneWriter` are optimistic update handles returned by read/create calls. They can write, rename, or remove the object and are documented to fail with `-ECANCELED` if another writer updates the same object after the read.

## Control Flow
Higher-level realm/period/zone management code calls a `ConfigStore` chosen by `DriverManager::create_config_store()`. Reads optionally return a writer handle tied to the object version. Subsequent updates go through that writer to enforce atomicity. Listing APIs use caller-provided spans and markers for pagination.

## State and Persistence Behavior
The interface owns durable multisite configuration metadata: defaults, named records, period epochs, latest epoch pointers, and period configuration. Exclusive flags control create/write conflict behavior. Writer handles represent read-modify-write state and are the main concurrency boundary.

## Dependencies and Integration Points
The header forward-declares RGW realm/period/zone types and depends on `optional_yield`, `DoutPrefixProvider`, spans, string views, and `rgw_sal_fwd.h`. Implementations are selected in `rgw_sal.cc` from RADOS, dbstore/posix, or JSON config stores.

## Risks
Because the interface uses spans supplied by callers, implementations must not outlive the input buffer and must set `ListResult::entries` correctly. Rename operations must enforce id immutability while updating name indexes. Default id operations are scoped by realm where appropriate; mistakes can break multisite bootstrap or period updates. Watcher support may return null, so callers need fallback behavior.

## Test Signals
Tests should cover create/read/list/delete for realm, period, zonegroup, and zone; default id read/write/delete; exclusive create conflicts; writer stale-update returning `-ECANCELED`; rename preserving ids; latest period epoch updates; pagination markers; null watcher behavior; and JSON/RADOS/dbstore implementation parity.
