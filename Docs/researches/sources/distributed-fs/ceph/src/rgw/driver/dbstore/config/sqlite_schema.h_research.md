# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite_schema.h

## Purpose
Defines the SQLite config-store schema migration and all SQL string templates used by `config/sqlite.cc`.

## APIs, Flow, And State
The main public data is `schema::migrations`, currently one `Migration` that creates `Realms`, `Periods`, `PeriodConfigs`, `ZoneGroups`, `Zones`, `DefaultRealms`, `DefaultZoneGroups`, and `DefaultZones`. Additional `constexpr` SQL templates cover insert/upsert/select/delete/update/list operations for each entity family. Templates use `{}` placeholders filled by `fmt::format()` with SQLite named parameters such as `:1`.

The schema uses primary keys and unique names for realms, zonegroups, and zones; `(ID, Epoch)` as the period primary key; singleton default realm via `DefaultRealms.Empty` as primary key; and realm-keyed defaults for zonegroups/zones. Some tables have `REFERENCES Realms(ID)` but no explicit cascading deletes.

## Dependencies And Integration
Consumed almost exclusively by `config/sqlite.cc`; relies on SQLite SQL dialect including `ON CONFLICT DO UPDATE`, `PRAGMA user_version` migration tracking, and foreign-key enforcement enabled at connection setup.

## Risks And Test Signals
Risk concentrates in SQL text correctness. `zonegroup_select_default0` and `zone_select_default0` are unfiltered joins, so callers passing a realm id cannot get realm-scoped defaults from these templates. Default tables reference realms, but their `ID` fields do not reference zonegroup/zone tables. List queries page by `Name > marker` or `ID > marker`, which is simple but can miss duplicate period ids because `Periods` can hold multiple epochs for one id. Test signal should include migration application, unique/primary-key errors, foreign-key enforcement, and realm-scoped default selection.
