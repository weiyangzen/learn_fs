# sources/distributed-fs/ceph/src/rgw/driver/posix/lmdb-safe.cc

## Purpose
`lmdb-safe.cc` implements the vendored RAII wrapper around LMDB environments, named databases, transactions, and cursors. The POSIX bucket cache uses it to store transient ordered bucket listings while avoiding raw LMDB cleanup mistakes in normal paths.

## Important APIs, Types, and Functions
`MDBDbi::MDBDbi()` opens an LMDB named database inside a transaction. `MDBEnv` creates the environment, sets a fixed 4GB map size, sets `maxdbs`, opens the environment with `MDB_NOTLS`, tracks per-thread RO/RW transaction counts, and serializes named database opens with `d_openmut`.

`getMDBEnv()` caches `MDBEnv` instances by `(dev, ino)` and rejects reopening an existing environment with different flags. `MDBRWTransactionImpl` and `MDBROTransactionImpl` implement transaction creation, commit, abort, child transaction creation, cursor cleanup, `clear()`, and cursor factories.

## Control Flow
Environment creation calls `mdb_env_create`, `mdb_env_set_mapsize`, `mdb_env_set_maxdbs`, and `mdb_env_open`. Opening a DB from a writable environment creates a short RW transaction, opens the named DB, commits, and returns the DBI; readonly environments use an RO transaction.

RO/RW transaction begin loops retry `MDB_MAP_RESIZED` by calling `mdb_env_set_mapsize(env, 0)`. RW begin rejects a duplicate same-thread RW transaction. RO begin rejects starting while a same-thread RW transaction is tracked. Destructors call `abort()`/`commit()` through base-class-safe non-virtual calls and close registered cursors before closing transactions.

## State and Persistence Behavior
The wrapper is durable only through LMDB's own environment files. In this repository, `bucket_cache.h` stores ephemeral listing data and wipes its LMDB directories on startup. The wrapper maintains process-local shared environment cache, per-thread transaction counters, open mutexes, cursor registries, and raw LMDB handles.

## Dependencies and Integration Points
It depends on LMDB C APIs, POSIX `stat`, and C++ mutex/shared pointer containers. `bucket_cache.h` calls `getMDBEnv()`, `openDB()`, `getROTransaction()`, `getRWTransaction()`, `put()`, `del()`, cursor scans, and `mdb_drop()` through the raw transaction conversion operator.

## Risks
The wrapper throws exceptions for most LMDB errors, while POSIX RGW cache callers generally do not catch them. The same-thread transaction count policy prevents RO while RW is open, which can surprise callers trying nested reads. The global environment cache is keyed by inode after creation and stores only flags, not mode or max DB count. Fixed map size and max DB settings may not match large deployments. DBI close is mostly left to callers, so callers must respect LMDB lifetime rules.

## Test Signals
Tests should cover environment reuse, flag mismatch rejection, DB open serialization, RO/RW transaction lifecycle, duplicate RW prevention, cursor auto-close on commit/abort, `MDB_MAP_RESIZED` retry behavior, child transaction cleanup, and bucket-cache listing writes/scans under concurrent list and notify traffic.
