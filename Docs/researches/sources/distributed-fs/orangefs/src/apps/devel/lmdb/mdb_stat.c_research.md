<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_stat.c -->
## sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_stat.c

**Purpose:** `mdb_stat` reports LMDB environment, database, freelist, and reader-table statistics.

**Important APIs, types, and functions:** `prstat()` prints `MDB_stat` tree/page/entry fields. `main()` parses `-a`, `-s`, `-e`, `-f`, `-r`, `-n`, and `-V`; opens the env read-only; optionally prints `mdb_env_stat`/`mdb_env_info`; lists or clears stale readers with `mdb_reader_list` and `mdb_reader_check`; then starts a read-only transaction for freelist and DB stats.

**Control flow:** Reader info can return early if no DB/freelist stats are requested. Freelist reporting iterates DBI 0 and optionally prints transaction page spans. Normal DB stats use `mdb_open` and `mdb_stat`; all-DB mode iterates main DB keys as subDB names and stats each subDB.

**State and persistence:** Most modes are read-only. `-rr` calls `mdb_reader_check`, which mutates the reader table by clearing stale readers.

**Dependencies and integration points:** It depends on LMDB environment internals and is operationally useful for diagnosing database size, free pages, and stuck readers in components using LMDB.

**Risks and edge cases:** Freelist span logic is low-level and sensitive to LMDB freelist encoding. SubDB name allocations are unchecked. Reader cleanup is a side effect in a tool otherwise named as status. Tests should cover env info, freelist detail levels, reader list/check, subDB selection, all DBs, invalid environments, and `MDB_NOSUBDIR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_stat.c -->
