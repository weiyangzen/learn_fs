# sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.hh

## Purpose
`lmdb-safe.hh` declares the C++ RAII API used to access LMDB from the POSIX RGW listing cache. It wraps LMDB environments, DBI handles, transactions, cursors, and input/output values with typed helpers and exception-based error handling.

## Important APIs, Types, and Functions
`LMDBError` carries an LMDB error code and message. `MDBDbi` is a lightweight DBI value wrapper. `MDBEnv` exposes `openDB()`, `getRWTransaction()`, `getROTransaction()`, raw `MDB_env*` conversion, and transaction counters.

`MDBInVal` builds `MDB_val` inputs from arithmetic values, strings, string views, output values, or structs. `MDBOutVal` exposes typed getters for arithmetic values, structs, `std::string`, and `string_view`. `MDBROTransactionImpl` implements `get()`, readonly DB open, and readonly cursor creation. `MDBRWTransactionImpl` adds `put()`, `del()`, `clear()`, RW cursor creation, and child transaction creation. `MDBGenCursor` implements cursor movement, find, lower_bound, current/first/last/next/prev, close, and move-only registration. `MDBROCursor` and `MDBRWCursor` specialize cursor behavior, with RW cursor `put()` and `del()`.

## Control Flow
Callers obtain a shared environment with `getMDBEnv()`, open a named DB with `openDB()`, start a transaction, and operate through `get`, `put`, `del`, or cursor methods. Cursors register themselves with their owning transaction so transaction commit/abort can close outstanding cursors before closing the transaction. `MDB_NOTLS` is required so readonly transactions can be managed explicitly.

## State and Persistence Behavior
The header's classes wrap LMDB persistent environment state but do not define a schema. State in the wrapper includes raw LMDB handles, transaction pointers, cursor registries, per-thread transaction counters, input value scratch storage for arithmetic types, and output values pointing into LMDB-managed memory valid only for the transaction lifetime.

## Dependencies and Integration Points
It depends on `lmdb.h`, `lmdb-safe-global.h`, standard C++ containers, mutexes, thread IDs, and either standard or Boost string view. `bucket_cache.h` uses string keys and serialized string values for `rgw_bucket_dir_entry` records.

## Risks
`MDBOutVal::string_view` points into LMDB memory and must not outlive the transaction. `MDBInVal::fromStruct()` references caller-owned memory, so the caller must keep it alive through the LMDB call. Move registration in `MDBGenCursor` is delicate; incorrect registry updates can double-close or leak cursors. Some raw LMDB conversions expose lower-level APIs, allowing callers to bypass wrapper invariants. Exception behavior must be acceptable to all integration paths.

## Test Signals
Compile and runtime tests should cover typed value conversion, missing key returns, exception paths, cursor move construction/assignment, cursor close during transaction close, lower_bound listing semantics, write/delete/clear behavior, and misuse cases such as using closed transactions.
