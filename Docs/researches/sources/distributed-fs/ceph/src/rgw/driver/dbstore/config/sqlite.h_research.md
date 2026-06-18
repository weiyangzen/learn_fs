# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.h

## Purpose
Declares `SQLiteConfigStore`, the SQLite implementation of RGW SAL configuration storage, and the `create_sqlite_store()` factory.

## APIs, Flow, And State
`SQLiteConfigStore` derives from `sal::ConfigStore` and overrides the full config surface for default realm ids, realms, periods, default zonegroups, zonegroups, default zones, zones, and period configs. The class stores only a `std::unique_ptr<SQLiteImpl>`; all persistent state and statement caches live behind that implementation pointer in `sqlite.cc`.

## Dependencies And Integration
Depends on `rgw_sal_config.h` for the SAL interface and RGW config object types, plus `DoutPrefixProvider` for logging context. `SQLiteImpl` is forward-declared to hide the SQLite connection pool and statement details from callers. `config/store.cc` calls `create_sqlite_store()` after URI selection.

## Risks And Test Signals
The header exposes support for watchers and latest epoch updates, but the implementation returns `nullptr`/`-ENOTSUP` or no-op success for some of those methods. Consumers must treat returned writer objects as conditional optimistic writers and handle `-ECANCELED`. Compile-time test signal is that this class continues to satisfy `sal::ConfigStore`; runtime signal comes from exercising every override with a real SQLite URI.
