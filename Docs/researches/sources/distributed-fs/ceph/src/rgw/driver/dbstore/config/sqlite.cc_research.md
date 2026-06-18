# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.cc

## Purpose
Implements the SQLite-backed `rgw::sal::ConfigStore` for RGW realm, period, zonegroup, zone, default, and period-config metadata. It translates SAL config operations into prepared SQLite statements, encodes complex RGW structures into `bufferlist` blobs, and applies the config schema migrations when a store is opened.

## APIs, Flow, And State
The central type is the private `SQLiteImpl`, a size-one `ConnectionPool<sqlite::Connection, sqlite::ConnectionFactory>`, owned by `SQLiteConfigStore`. Public methods implement the `sal::ConfigStore` virtual API declared in `sqlite.h`: create/read/list/delete defaults, realms, periods, zonegroups, zones, and period configs. `create_sqlite_store()` opens the database with URI/create/readwrite flags, enables `PRAGMA foreign_keys`, runs migrations, and returns a configured store.

Control flow is highly regular: validate required ids/names, fetch a pooled connection, lazily prepare a named statement in `conn->statements`, bind `:1`..`:6`, execute with `sqlite::eval0()` or `eval1()`, translate `sqlite::error` codes into negative errno values, and optionally return a writer object. Listing uses marker-based `Name > marker` or `ID > marker` queries with `LIMIT entries.size()` and sets `ListResult::next` to the last returned value when the result span is full.

State persists in the tables from `sqlite_schema.h`. Realms store plain id/name/current period/epoch plus optimistic concurrency fields. Periods, zonegroups, zones, and period configs store encoded Ceph `bufferlist` payloads in `Data`. `SQLiteRealmWriter`, `SQLiteZoneGroupWriter`, and `SQLiteZoneWriter` enforce read-modify-write semantics with `VersionNumber` and random `VersionTag`; a zero `sqlite3_changes()` result maps to `-ECANCELED` and disables that writer for later writes. Deletes also invalidate the writer.

## Dependencies And Integration
Depends on Ceph logging (`DoutPrefixProvider`, `DoutPrefixPipe`), `rgw_sal_config.h` interfaces, `RGWRealm`, `RGWPeriod`, `RGWZoneGroup`, `RGWZoneParams`, `RGWPeriodConfig`, Ceph `encode/decode`, `gen_rand_alphanumeric()`, and the local SQLite wrappers in `sqlite/connection.h`, `sqlite/error.h`, and `sqlite/statement.h`. It is selected by `config/store.cc` for `file:` URIs when `SQLITE_ENABLED` is compiled.

## Risks And Test Signals
Important risks: `update_latest_epoch()` is a TODO that returns success without persisting anything; realm notification and watchers are unsupported; `read_default_zonegroup()` and `read_default_zone()` ignore their `realm_id` argument and use select SQL without realm filtering; `SQLiteZoneWriter::rename()` formats `zone_rename4` with duplicated placeholder arguments while later binding `P4`, which can break binding; several default-zonegroup/default-zone write paths do not map unique or foreign-key constraints as precisely as realm/zone creation does. Schema migration runs in a transaction and updates `PRAGMA user_version`, but there is only one migration and no downgrade path. Direct test signals in this subset are weak; coverage should include config-store round trips, optimistic writer conflicts, realm-scoped default lookups, no-op latest-epoch behavior, migration idempotence, and busy/constraint translation.
