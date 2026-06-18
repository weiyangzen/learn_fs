# sources/distributed-fs/ceph/src/rgw/driver/posix/posixDB.h

## Purpose
`posixDB.h` declares POSIX RGW database adapter types over the DBStore SQLite backend. It provides user and account DB classes plus operation marker/subclass types that let the POSIX driver reuse SQL user/account operation implementations.

## Important APIs, Types, and Functions
The file defines POSIX-specific aliases/subclasses for DB operation parameter/info structures, including `POSIXUserDBOpUserInfo`, `POSIXUserDBOpPrepareParams`, `POSIXAccountDBOpAccountInfo`, and related types. `POSIXUserDBOp` and `POSIXAccountDBOp` inherit `DBOp`, include static SQL create-table strings matching RGW user/account structures, and carry a mutex intended to protect prepared statements.

`InsertPOSIXUserOp`, `RemovePOSIXUserOp`, `InsertPOSIXAccountOp`, `RemovePOSIXAccountOp`, and `GetPOSIXAccountOp` inherit existing SQL operation classes. `POSIXUserDB` and `POSIXAccountDB` inherit `SQLiteDB` and expose `Initialize()`, `ProcessOp()`, `Destroy()`, `ctx()`, and no-op overrides for lifecycle and listing methods not implemented here.

## Control Flow
The classes are constructed with a database name/path and `CephContext`. Constructors call `DB::set_context(cct)` and derive table names from the database name for account/user tables. Runtime behavior is implemented in `posixDB.cc` and inherited `SQLiteDB`/DBStore methods.

## State and Persistence Behavior
`POSIXUserDB` persists user metadata, access keys, quotas, caps, temp URL keys, MFA IDs, attrs, and versioning fields in SQLite columns, with several maps stored as blobs. `POSIXAccountDB` persists account metadata, quotas, max limits, tenant/name/email fields, and account ID primary key. Several list-all methods are stubs returning success without filling results.

## Dependencies and Integration Points
The header depends on RGW DBStore SQLite/common APIs, Ceph context/logging, RGW common types, multisite headers, and `rgw_obj_manifest.h` for a noted subclass dependency. `POSIXDriver` owns one user DB and one account DB, and POSIX users/accounts call through these adapters.

## Risks
The SQL create-table strings are private static constants but table creation appears delegated to inherited SQLiteDB paths, so schema alignment needs build/runtime verification. Blob-packed complex fields limit queryability. `ListAllBuckets`, `ListAllUsers`, and `ListAllObjects` returning `0` without output can mislead callers if wired in. Table name construction embeds the DB path/name prefix, which may produce awkward SQL identifiers if not sanitized by lower layers.

## Test Signals
Compile tests should instantiate all operation types and DB classes. Integration tests should verify schema creation, insert/get/remove user/account operations, blob round trips for keys/attrs/quotas, version tracker behavior, list-all stub expectations, and table-name handling for configured DB prefixes.
