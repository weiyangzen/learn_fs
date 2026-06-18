# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-db.h

## Purpose
`dbpf-db.h` defines the backend-neutral database abstraction used by DBPF metadata code. It lets DBPF compile against Berkeley DB, LMDB, or another backend with the same API.

## Important APIs, types, and functions
Opaque `dbpf_db` and `dbpf_cursor` hide backend details. `struct dbpf_data` is the shared key/value buffer descriptor. Comparison modes `DBPF_DB_COMPARE_DS_ATTR` and `DBPF_DB_COMPARE_KEYVAL` select key ordering. Cursor operation constants map to backend cursor positioning. The API includes open, close, sync, get, put, putonce, delete, cursor open/close/get/delete.

## Control flow and state
The header defines no state, but it establishes caller-owned buffer semantics: `dbpf_data.data` points to provided storage and `dbpf_data.len` carries size in and actual size out for reads/cursor reads.

## Persistence and integration
Backends persist dspace and keyval metadata. Dspace creation/removal/getattr/setattr and keyval iteration/write paths depend on these functions for durable metadata operations.

## Dependencies
The open call references `struct server_configuration_s`, so backend implementations can use server configuration such as cache size or LMDB map size.

## Risks and test signals
The abstraction does not precisely specify buffer-too-small behavior, and the BDB and LMDB implementations differ. Tests for any backend must validate error sign conventions, caller buffer ownership, cursor mutation of keys, duplicate-key behavior, sync semantics, and comparator consistency across backends.
