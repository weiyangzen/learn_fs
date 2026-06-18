# sources/distributed-fs/orangefs/src/common/lmdb/lmdb.h

Purpose: Vendored LMDB 0.9.21 public API header for the Lightning Memory-Mapped Database library. It documents and declares the environment, transaction, database, cursor, copy, stats, reader, and error APIs used by LMDB consumers.

Important APIs/types: Opaque handles `MDB_env`, `MDB_txn`, `MDB_cursor`, and `MDB_dbi`; value container `MDB_val`; callback types for comparison, relocation, assertions, and message output; `MDB_stat` and `MDB_envinfo`; version macros and error codes. Major function families include `mdb_env_*` lifecycle/config/sync/copy/status calls, `mdb_txn_*` transaction calls, `mdb_dbi_*` database handle calls, `mdb_get/put/del`, cursor open/get/put/del/count/renew/close, comparison helpers, and reader lock-table inspection/checking.

Control flow contract: Typical use is create environment, set mapsize/maxreaders/maxdbs if needed, open environment, begin transactions, open database handles, perform get/put/cursor operations, commit or abort, close cursors/database handles as required, then close the environment. Read transactions provide snapshots; write transactions are serialized; cursors are transaction-bound.

State/persistence: LMDB persists data in memory-mapped database files plus a lock file. Copy-on-write pages provide MVCC. Header caveats emphasize reader slots, stale readers, mapsize growth, filesystem/locking constraints, and durability tradeoffs controlled by flags such as `MDB_NOSYNC`, `MDB_NOMETASYNC`, `MDB_WRITEMAP`, and `MDB_MAPASYNC`.

Dependencies/integration: Includes `<sys/types.h>` and offers C++ linkage. Platform abstractions define `mdb_mode_t` and `mdb_filehandle_t` for POSIX/Windows. In this repository it sits under `src/common/lmdb`, so OrangeFS code can build against a pinned LMDB API.

Risks: Many APIs return pointers into mmap-owned memory that become invalid after updates or transaction end; callers must not modify them. Long-lived readers can prevent free-page reuse and grow the database. `MDB_NOLOCK`, remote filesystems, mixed `MDB_WRITEMAP` usage, wrong custom compare functions, or closing DB handles while in use can corrupt or destabilize the environment. This header is an older pinned LMDB version, so security/bug fixes depend on the matching implementation version in the tree.

Test signals: Integration tests should cover environment lifecycle, readonly/readwrite transactions, map-full handling, stale reader checks, named DB maxdbs, duplicate-sort cursor paths, backup copy, durability flag combinations, and multi-process reader/writer behavior.
