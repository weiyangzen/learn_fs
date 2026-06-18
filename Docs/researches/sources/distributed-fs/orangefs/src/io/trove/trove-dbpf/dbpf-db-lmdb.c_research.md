# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-lmdb.c

## Purpose
`dbpf-db-lmdb.c` implements the same DBPF key/value abstraction using LMDB environments and transactions. Each database name is an LMDB environment directory.

## Important APIs, types, and functions
`struct dbpf_db` holds `MDB_env *` and `MDB_dbi`; `struct dbpf_cursor` holds an `MDB_cursor *` and its owning `MDB_txn *`. `dbpf_db_open()` creates the environment, sets map size from server/global filesystem config, optionally creates the directory, opens with `MDB_MAPASYNC|MDB_WRITEMAP`, opens the DBI, and installs comparators. CRUD functions wrap each operation in a read-only or write transaction. Cursor functions keep a transaction open for iteration.

## Control flow and state
Reads begin a read-only transaction, call `mdb_get()`, commit, copy returned memory into caller buffers, and set `val->len`. Writes begin a write transaction, call `mdb_put()` or `mdb_del()`, and commit. `dbpf_db_cursor_get()` maps DBPF cursor constants to LMDB cursor operations and copies key/value bytes into caller buffers before updating lengths.

## Persistence and integration
LMDB persists through memory-mapped environments. `dbpf_db_sync()` calls `mdb_env_sync()`. `MDB_MAPASYNC|MDB_WRITEMAP` favors performance and makes explicit sync policy important for crash durability.

## Dependencies
It depends on `<lmdb.h>`, `server-config.h`, the external `filesystem_configuration_s *cfg_fs`, DBPF keyval entry layout macros, and gossip.

## Risks and test signals
The implementation copies `db_data.mv_size` bytes into `val->data` after using the caller's initial `val->len` only as a copy length in some cursor paths; no explicit buffer-size check is performed, unlike BDB's buffer-small handling. `mdb_txn_commit()` failure in open returns `db_error(errno)` instead of the LMDB return code. `create` requires `mkdir()` success and will error if the directory already exists. Tests should cover map-full behavior, configured map sizes, small caller buffers, cursor iteration/deletion, putonce duplicate errors, explicit sync, and crash-recovery expectations under `MDB_MAPASYNC`.
