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
