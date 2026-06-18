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
