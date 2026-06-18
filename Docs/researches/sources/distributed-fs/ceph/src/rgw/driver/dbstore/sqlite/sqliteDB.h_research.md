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
