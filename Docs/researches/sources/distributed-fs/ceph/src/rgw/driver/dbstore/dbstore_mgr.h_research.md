# sources/distributed-fs/ceph/src/rgw/driver/dbstore/dbstore_mgr.h

## Purpose
Declares `DBStoreManager`, a lightweight manager for tenant-scoped dbstore `DB` instances.

## APIs, Flow, And State
The class owns a `std::map<std::string, DB*> DBStoreHandles`, a `DB* default_db`, and a `CephContext*`. Constructors store the context, optionally configure log file/log level, and create `default_tenant` (`"default_ns"`). Public methods expose default DB retrieval, tenant lookup/creation, creation, deletion by tenant or pointer, and destruction of all handles.

## Dependencies And Integration
Includes Ceph context/logging, `common/dbstore.h`, and `sqlite/sqliteDB.h`. The header uses `using namespace rgw::store` and a global `using DB`, which makes it convenient but broadens namespace leakage into includers.

## Risks And Test Signals
Raw ownership and the comments about locking/refcounts are the main design risks. The destructor calls `destroyAllHandles()`, so users must avoid using returned `DB*` after manager destruction. Test signal comes from `dbstore_mgr_tests.cc`; additional tests should exercise repeated create/delete, pointer deletion, and concurrent `getDB(..., true)`.
