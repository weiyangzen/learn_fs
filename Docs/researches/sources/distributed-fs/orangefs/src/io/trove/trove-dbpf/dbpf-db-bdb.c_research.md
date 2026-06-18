# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db-bdb.c

## Purpose
`dbpf-db-bdb.c` implements the `dbpf-db.h` key/value abstraction using Berkeley DB BTREE databases. It stores dspace attributes and keyval records behind a common API used by DBPF metadata code.

## Important APIs, types, and functions
`struct dbpf_db` wraps `DB *`; `struct dbpf_cursor` wraps `DBC *`. `dbpf_db_open()` creates and opens a BTREE database, applies comparison functions, cache size, mmap/NOMMAP flags, and `DB_THREAD`. The file implements get/put/putonce/delete, sync, cursor open/close/get/delete, and `db_error()` mapping BDB status values to Trove errors. `ds_attr_compare()` sorts handles descending, and `keyval_compare()` orders keyval database entries by handle, type, encoded key size, and key bytes.

## Control flow and state
Each operation builds `DBT` wrappers around caller-owned buffers. `dbpf_db_get()` and cursor get use `DB_DBT_USERMEM`; if BDB reports `DB_BUFFER_SMALL`, they allocate temporary storage, retry, copy up to the caller's original buffer length, and update `val->len` to the database value size.

## Persistence and integration
Persistence is Berkeley DB's on-disk BTREE file. `dbpf_db_sync()` calls `DB->sync()`. Dspace and keyval code rely on this backend for durable metadata and cursor iteration.

## Dependencies
It depends on `<db.h>`, `server-config.h`, DBPF keyval entry layout macros, and gossip logging.

## Risks and test signals
`dbpf_db_open()` returns raw `errno` instead of mapped negative Trove error when the initial wrapper malloc fails. Buffer-small retry copies only the caller's original length but advertises the full stored length, so callers must treat larger lengths as truncation. Comparator aborts on corrupt small keys. Tests should cover create/open existing DBs, mmap and NOMMAP config, duplicate putonce, cursor operations, undersized buffers, comparator ordering, and BDB error mapping.
