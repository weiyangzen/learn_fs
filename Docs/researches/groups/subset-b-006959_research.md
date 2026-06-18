# subset-b-006959 Research

Grouped research for the listed Ceph RGW dbstore files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.h

## Purpose
Declares `SQLiteConfigStore`, the SQLite implementation of RGW SAL configuration storage, and the `create_sqlite_store()` factory.

## APIs, Flow, And State
`SQLiteConfigStore` derives from `sal::ConfigStore` and overrides the full config surface for default realm ids, realms, periods, default zonegroups, zonegroups, default zones, zones, and period configs. The class stores only a `std::unique_ptr<SQLiteImpl>`; all persistent state and statement caches live behind that implementation pointer in `sqlite.cc`.

## Dependencies And Integration
Depends on `rgw_sal_config.h` for the SAL interface and RGW config object types, plus `DoutPrefixProvider` for logging context. `SQLiteImpl` is forward-declared to hide the SQLite connection pool and statement details from callers. `config/store.cc` calls `create_sqlite_store()` after URI selection.

## Risks And Test Signals
The header exposes support for watchers and latest epoch updates, but the implementation returns `nullptr`/`-ENOTSUP` or no-op success for some of those methods. Consumers must treat returned writer objects as conditional optimistic writers and handle `-ECANCELED`. Compile-time test signal is that this class continues to satisfy `sal::ConfigStore`; runtime signal comes from exercising every override with a real SQLite URI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite_schema.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/sqlite_schema.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.cc

## Purpose
Implements the generic dbstore config-store factory, routing supported URIs to backend-specific `sal::ConfigStore` implementations.

## APIs, Flow, And State
`create_config_store(dpp, uri)` checks compile-time `SQLITE_ENABLED`, accepts only URIs starting with `file:`, and delegates to `config::create_sqlite_store()`. Any unsupported URI throws `std::runtime_error` with the rejected URI. It owns no persistent state.

## Dependencies And Integration
Depends on `store.h`, `fmt/format.h`, and conditionally `sqlite.h`. It is the integration point between RGW code that wants a `sal::ConfigStore` and the SQLite config implementation.

## Risks And Test Signals
URI support is intentionally narrow. If SQLite is not compiled in, even `file:` URIs throw at runtime. Because failure is an exception rather than a negative errno, callers must be exception-aware. Tests should cover SQLite-enabled file URI routing and unsupported URI failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.h

## Purpose
Declares the dbstore config-store factory API.

## APIs, Flow, And State
`rgw::dbstore::create_config_store(const DoutPrefixProvider*, const std::string&)` returns a `std::unique_ptr<sal::ConfigStore>`. The header contains no state and deliberately hides concrete backend classes from users.

## Dependencies And Integration
Includes `rgw_sal_config.h` for `sal::ConfigStore` and forward uses `DoutPrefixProvider`. Implemented by `store.cc`; callers include this when constructing dbstore config storage from a URI.

## Risks And Test Signals
The API does not advertise supported URI schemes, so runtime failure is the discovery mechanism. Compile-time signal is minimal; runtime tests should assert expected backend selection and exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/config/store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_main.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_main.cc

## Purpose
Provides a standalone/manual dbstore exercise binary that creates a `DBStoreManager`, obtains a tenant database handle, and runs user/bucket CRUD-style operations from two pthreads.

## APIs, Flow, And State
`main()` initializes a Ceph context with no monitor config, optionally takes `logfile` and `loglevel`, constructs `DBStoreManager`, fetches a tenant DB with creation enabled, starts two pthreads, joins them, and destroys all handles. `process()` initializes `DBOpParams`, inserts and fetches users, prints placement tags and access keys, inserts/removes buckets/users, and lists all users/buckets through string-named `DB::ProcessOp()` calls.

Persistent state is the SQLite or fallback DB file created by `DBStoreManager` for tenant `Redhat`. Per-thread state is mostly local `DBOpParams`, but both threads share the same `DB*` and therefore shared prepared operations and object maps.

## Dependencies And Integration
Depends on `dbstore_mgr.h`, `common/dbstore.h`, `dbstore_log.h`, Ceph `global_init`, pthreads, and SQLite headers. It exercises the generic DB operation layer rather than the SAL config-store layer.

## Risks And Test Signals
The program is sample/test-like rather than production-grade: it uses raw `new`, `goto out`, shared DB handle access from multiple threads, direct `cout`, and assumes the selected operations are safe under concurrent use. It suppresses Coverity concern about uncaught exceptions in `main`. Useful test signal is manual smoke coverage of manager creation and basic user/bucket operations, but it is not deterministic enough to replace unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.cc

## Purpose
Implements `DBStoreManager`, the tenant-to-DB-handle manager for the older dbstore object/user/bucket backend.

## APIs, Flow, And State
`getDB(tenant, create)` returns the default DB for empty tenant, returns an existing handle from `DBStoreHandles`, optionally creates one, or returns `nullptr`. `createDB(tenant)` builds a path from Ceph config `dbstore_db_dir` and `dbstore_db_name_prefix`, constructs `SQLiteDB` under `SQLITE_ENABLED` or base `DB` otherwise, calls `Initialize("", -1)`, inserts the handle in `DBStoreHandles`, and handles an insertion race by deleting the newly created duplicate. `deleteDB(tenant)`, `deleteDB(DB*)`, and `destroyAllHandles()` destroy and delete DB handles.

State is an in-memory `std::map<std::string, DB*>` plus the persistent per-tenant database files on disk. Handles are raw pointers and ownership is manual. `default_db` is also inserted in the map by construction through `createDB(default_tenant)`.

## Dependencies And Integration
Depends on `SQLiteDB`, `DB`, Ceph `g_conf()` dbstore options, `std::filesystem`, and logging. It is used by dbstore tests and `dbstore_main.cc`, and indirectly by RGW paths that need tenant-specific DB handles.

## Risks And Test Signals
The source itself notes missing map locking and missing refcounting. `createDB()` attempts to handle a duplicate map insert but the check is not protected, so concurrent callers can still race around map access. `deleteDB(DB*)` calls `deleteDB(dbs->getDBname())`, while the map is keyed by tenant, not full DB name, so pointer-based deletion may not find the entry. Tests in `dbstore_mgr_tests.cc` cover path creation, prefixes, default lookup, missing tenant lookup, creation, and deletion, but not concurrency or pointer deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.h

## Purpose
Declares `DBStoreManager`, a lightweight manager for tenant-scoped dbstore `DB` instances.

## APIs, Flow, And State
The class owns a `std::map<std::string, DB*> DBStoreHandles`, a `DB* default_db`, and a `CephContext*`. Constructors store the context, optionally configure log file/log level, and create `default_tenant` (`"default_ns"`). Public methods expose default DB retrieval, tenant lookup/creation, creation, deletion by tenant or pointer, and destruction of all handles.

## Dependencies And Integration
Includes Ceph context/logging, `common/dbstore.h`, and `sqlite/sqliteDB.h`. The header uses `using namespace rgw::store` and a global `using DB`, which makes it convenient but broadens namespace leakage into includers.

## Risks And Test Signals
Raw ownership and the comments about locking/refcounts are the main design risks. The destructor calls `destroyAllHandles()`, so users must avoid using returned `DB*` after manager destruction. Test signal comes from `dbstore_mgr_tests.cc`; additional tests should exercise repeated create/delete, pointer deletion, and concurrent `getDB(..., true)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/CMakeLists.txt

## Purpose
Builds the SQLite DB backend static library for the older dbstore operation layer.

## APIs, Flow, And State
The CMake file requires SQLite3, sets `sqliteDB.h` and `sqliteDB.cc` as `sqlite_db` sources, defines `SQLITE_THREADSAFE=1` through global C++ flags, builds `sqlite_db` as a static library, and links it against `sqlite3`, `dbstore_lib`, and `rgw_common`.

## Dependencies And Integration
Depends on CMake 3.14, `find_package(SQLite3 REQUIRED)`, Ceph build helpers such as `COMPILER_SUPPORTS_VLA_ERROR`, and parent build wiring that enables the dbstore/sqlite subdirectory.

## Risks And Test Signals
Only `sqliteDB.*` is included here; the config-store SQLite wrapper files are built elsewhere. The use of global `CMAKE_CXX_FLAGS` is broader than target-local compile definitions. Build signal is successful `sqlite_db` compilation/linking and unit tests that link the dbstore target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.cc

## Purpose
Implements SQLite database opening for the config-store SQLite wrapper layer.

## APIs, Flow, And State
`open_database(filename, flags)` calls `sqlite3_open_v2()`, throws `std::system_error` on failure using the local SQLite error category, enables extended result codes with `sqlite3_extended_result_codes(db, 1)`, and returns an owning `db_ptr`.

## Dependencies And Integration
Depends on `sqlite3`, `connection.h`, and `error.h`. `ConnectionFactory` in `connection.h` calls this function for the config-store connection pool.

## Risks And Test Signals
Failure handling throws before returning an owning pointer; callers must catch exceptions at a higher boundary. Extended result codes are essential for the implementation’s constraint translation, so tests should verify primary-key/foreign-key/unique errors are distinguishable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.h

## Purpose
Declares RAII connection ownership and the connection factory used by the config-store SQLite connection pool.

## APIs, Flow, And State
`db_ptr` is a `std::unique_ptr<sqlite3, db_deleter>` that closes databases with `sqlite3_close()`. `Connection` owns a `db_ptr` and a `std::map<std::string_view, stmt_ptr>` for lazily prepared statement caching. `ConnectionFactory` captures a URI and flags and returns a `std::unique_ptr<Connection>` when invoked.

## Dependencies And Integration
Depends on SQLite C API, local `sqlite/statement.h`, and `DoutPrefixProvider`. Used by `config/sqlite.cc` through `ConnectionPool`.

## Risks And Test Signals
Statement cache keys are `std::string_view`; current call sites use string literals, which is safe, but dynamic temporary keys would dangle. `sqlite3_close()` can fail if statements remain unfinalized, but the connection member order finalizes `statements` before `db` because members are destroyed in reverse declaration order. Tests should exercise repeated calls to confirm prepared statements are reused and finalized cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.cc

## Purpose
Defines the custom `std::error_category` for SQLite primary and extended result codes.

## APIs, Flow, And State
`error_category()` returns a static category named `dbstore:sqlite`. `message()` delegates to `sqlite3_errstr()`. `default_error_condition()` masks the low eight bits, making extended result codes compare equal to their primary result-code conditions.

## Dependencies And Integration
Used by `sqlite::error`, `open_database()`, and statement helpers to turn SQLite integer results into `std::error_code` and `std::error_condition`.

## Risks And Test Signals
The low-byte masking intentionally groups extended errors by primary code, while still allowing exact extended-code comparison. Tests should assert that `SQLITE_CONSTRAINT_PRIMARYKEY` matches both `errc::primary_key_constraint` and primary `errc::constraint` semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.h

## Purpose
Declares SQLite error wrappers and typed error conditions for the config-store SQLite helper layer.

## APIs, Flow, And State
`sqlite::error` derives from `std::runtime_error` and carries a `std::error_code`, with constructors from message/code, `sqlite3*` plus code, or current extended DB error. `enum class errc` names the primary/extended result codes currently handled: ok, busy, constraint, row, done, primary-key constraint, foreign-key constraint, and unique constraint. Helper functions create error codes/conditions, and `std::is_error_condition_enum` enables comparisons like `e.code() == sqlite::errc::busy`.

## Dependencies And Integration
Depends on `<system_error>` and `sqlite3.h`. Used throughout `config/sqlite.cc` and `sqlite/statement.cc` for exception-based error propagation.

## Risks And Test Signals
Only result codes needed by current code are modeled; new SQLite behaviors may collapse to `-EIO` until added. The category is not a standard generic category, so callers should compare against `sqlite::errc`, not errno. Unit tests should verify condition matching for primary and extended constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/sqliteDB.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/sqliteDB.cc

## Purpose
Implements the SQLite backend for the older RGW dbstore `DB` operation framework: accounts, users, buckets, per-bucket objects/object data, lifecycle entries, and lifecycle heads.

## APIs, Flow, And State
The file defines macro helpers for preparing, binding, encoding/decoding blobs, stepping statements, and serializing operation execution under the `DBOp` mutex. `SQLiteDB::openDB()` opens a FULLMUTEX SQLite database file and enables foreign keys; `InitializeDBOps()` creates base tables and installs shared operation objects into `dbops`; `createTables()` creates account/user/bucket/quota tables; `createObjectTable*()` and `createLCTables()` create bucket-scoped object/object-data/trigger/view and lifecycle tables.

Operation classes follow a three-phase pattern: `Prepare()` builds SQL from inherited schema generators in `common/dbstore.h`, `Bind()` maps `DBOpParams` fields to named parameters, and `Execute()` runs `SQL_EXECUTE`. Read callbacks such as `list_account`, `list_user`, `list_bucket`, `list_object`, `get_objectdata`, `list_lc_entry`, and `list_lc_head` decode SQLite columns back into `DBOpInfo`. Bucket creation installs an `SQLObjectOp` in the static object map and creates object/data tables and triggers; bucket get also reinstalls object ops after restart.

Persistent state is the SQLite database file with global account/user/bucket/quota/lifecycle tables and per-bucket object/object-data tables. Complex RGW fields, attrs, manifests, omap, quotas, times, and buffers are stored as encoded blobs. Prepared statements are retained per operation object until destructor finalization. Object operation dispatch depends on the static bucket-to-`ObjectOp*` map managed by `DB`.

## Dependencies And Integration
Depends on `sqliteDB.h`, `rgw_account.h`, Ceph encode/decode, the inherited DB schema/operation interfaces in `common/dbstore.h`, and SQLite C APIs. `DBStoreManager` constructs `SQLiteDB` when `SQLITE_ENABLED` is set. RGW code reaches these operations through string-named `DB::ProcessOp()` calls.

## Risks And Test Signals
Risk is high because the file is macro-heavy, manually binds many columns, and uses raw `sqlite3_stmt*`. Many APIs return `-1` rather than specific errors; `Step()` treats a no-row `SQLITE_DONE` as success, so not-found semantics must be inferred by callers from empty output state. Several operations mutate input params, for example empty object instance becomes `"null"`. `SQLInsertBucket::Execute()` creates object tables after the bucket insert but does not roll back if later table creation fails. Concurrency depends on an operation mutex plus SQLite FULLMUTEX, while the manager and object map have separate risks. Tests should cover full CRUD round trips for every operation family, blob encode/decode compatibility, no-row behavior, bucket object-table lifecycle, restart reconstruction through `GetBucket`, and concurrent operations on shared handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/sqliteDB.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/sqliteDB.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/sqliteDB.h

## Purpose
Declares the SQLite-backed `DB` subclass and all concrete SQLite operation classes for the older dbstore operation framework.

## APIs, Flow, And State
`SQLiteDB` derives from `DB` and `DBOp`, exposes database open/close, table creation/deletion, list helpers, statement stepping, and prepare-param initialization. `SQLObjectOp` owns the bucket-scoped object operation bundle. Concrete operation classes implement `Prepare`, `Bind`, and `Execute` for account, user, bucket, object, object-data, and lifecycle operations. Each class stores a pointer to the shared `sqlite3*` and one or more cached `sqlite3_stmt*`, finalized in destructors.

State exposed by the declarations includes a raw `sqlite3_stmt* stmt`, inherited `void* db`, a `DBOpPrepareParams PrepareParams`, and many per-operation statement members. Object operation classes can be constructed either from `void**` or `sqlite3**` depending on whether they are global or bucket-scoped.

## Dependencies And Integration
Includes `common/dbstore.h`, `sqlite3.h`, and RGW/Ceph types through the common DB interface. `sqliteDB.cc` implements these declarations, and `DBStoreManager` constructs `SQLiteDB` instances.

## Risks And Test Signals
The header exposes extensive raw pointer ownership and manual statement lifetime. Multiple inheritance from `SQLiteDB` plus operation interfaces is powerful but hard to reason about, especially because each operation object has its own `SQLiteDB` base view of the same raw database pointer. Build tests catch signature drift; runtime tests need to cover destructor/finalization behavior, shared DB pointer lifetime, and operation-specific statement reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/sqliteDB.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.cc

## Purpose
Implements small RAII-friendly helpers for preparing, binding, executing, and reading SQLite statements in the config-store SQLite layer.

## APIs, Flow, And State
`prepare_statement()` wraps `sqlite3_prepare_v2()` and logs SQL on failure. `bind_null`, `bind_text`, and `bind_int` resolve named parameter indices then bind values. `eval0()` expects `SQLITE_DONE`; `eval1()` expects one `SQLITE_ROW`; `read_text_rows()` repeatedly steps into a caller-provided span; `column_int()` and `column_text()` read typed columns; `execute()` wraps raw `sqlite3_exec()` for migrations and pragmas.

State cleanup is handled by pointer wrappers from `statement.h`: binding scopes clear bindings and execution scopes reset statements. Logging can include `sqlite3_expanded_sql()` when the debug subsystem level is high.

## Dependencies And Integration
Depends on `common/dout.h`, local `error.h`, and SQLite. Used by `config/sqlite.cc` and `connection.cc`, not by the older `sqliteDB.cc` operation backend.

## Risks And Test Signals
`bind_text()` uses `SQLITE_STATIC`; current callers keep bound string/blob views alive until immediate execution, but delayed execution would be unsafe. `eval1()` treats `SQLITE_DONE` as an exception, which config-store callers translate to `-ENOENT`. `read_text_rows()` does not detect whether more rows exist beyond a full span; callers use a full result as "maybe more" by setting `next` to the last entry. Tests should include prepare failures, missing named parameters, NULL text handling, span-limited listing, and high-debug expanded SQL paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.h

## Purpose
Declares RAII pointer aliases and helper functions for prepared SQLite statement use in the config-store layer.

## APIs, Flow, And State
`stmt_ptr` owns `sqlite3_stmt*` and finalizes it. `stmt_binding` is non-owning and clears bindings on destruction. `stmt_execution` is non-owning and resets execution state on destruction. Function declarations cover prepare, binding of NULL/text/int values, zero-row and one-row execution expectations, column reads, text-row list reads, and raw query execution.

## Dependencies And Integration
Depends on `sqlite3.h`, `std::span`, strings, and `DoutPrefixProvider`. Included by `connection.h` and used by `config/sqlite.cc`.

## Risks And Test Signals
The non-owning RAII aliases rely on callers never outliving the owning `stmt_ptr`. `stmt_binding` and `stmt_execution` can be constructed around the same raw statement at the same time, so call ordering remains a convention. Tests should verify bindings are cleared between statement reuses and statements are reset after both success and exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/CMakeLists.txt

## Purpose
Defines unit-test targets for the dbstore backend.

## APIs, Flow, And State
Builds `unittest_dbstore_tests` from `dbstore_tests.cc` and `unittest_dbstore_mgr_tests` from `dbstore_mgr_tests.cc`. Links the first target with accumulated `CMAKE_LINK_LIBRARIES` plus gtest, and the manager target with `dbstore` and `gtest_main`. Both are registered with `add_ceph_unittest()` and get VLA warnings as errors when supported.

## Dependencies And Integration
Depends on gtest, Ceph test macros, and the `dbstore` target. It integrates the manager tests read in this work item and broader dbstore tests outside this exact item.

## Risks And Test Signals
The file does not explicitly link SQLite here; that is expected through the `dbstore` target. Coverage is only as broad as the two source files. The primary signal is successful target build and execution under Ceph’s unit-test runner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_mgr_tests.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_mgr_tests.cc

## Purpose
Unit tests `DBStoreManager` database-file naming, default handle creation, tenant lookup, tenant creation, and deletion behavior.

## APIs, Flow, And State
The fixture creates a standalone `CephContext`, sets `g_ceph_context`, moves into the system temp directory, creates `rgw_dbstore_tests`, and removes it on teardown. Helpers compute expected database full paths from `dbstore_db_dir`, `dbstore_db_name_prefix`, tenant, and `.db` suffix, and compute the `DB::getDBname()` tenant path without suffix.

Tests verify default DB file creation when `dbstore_db_dir` is set; prefix customization; the alternate manager constructor with log file/log level; `getDB(default_tenant, false)` and `getDB("", false)` return a DB named for the default tenant; missing tenant lookup returns `nullptr`; `getDB(new_tenant, true)` creates a new tenant handle; and `deleteDB(default_tenant)` removes the map entry so later lookup returns `nullptr`.

## Dependencies And Integration
Depends on `gtest`, `std::filesystem`, `common/ceph_context.h`, and `rgw/driver/dbstore/dbstore_mgr.h`. It exercises real database creation through `DBStoreManager`, so it depends on the dbstore backend compiled into the test target.

## Risks And Test Signals
These tests cover basic lifecycle and path naming but not object/user/bucket operations, concurrent `getDB()`, pointer deletion, repeated delete, or filesystem cleanup of database files. Because tests change current working directory and global Ceph context, isolation matters if more tests are added. The current signal is a good smoke test for manager construction and tenant mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_mgr_tests.cc -->
