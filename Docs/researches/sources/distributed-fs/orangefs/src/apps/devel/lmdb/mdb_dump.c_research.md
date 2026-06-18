<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_dump.c -->
## sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_dump.c

**Purpose:** `mdb_dump` dumps LMDB databases in Berkeley DB-compatible text or hex format, supporting main DB, named subDB, all subDBs, and listing subDB names.

**Important APIs, types, and functions:** `dbflags[]` maps LMDB DB flags to dump header keys. `text()` and `byte()` emit printable or hex records. `dumpit()` prints headers from `mdb_dbi_flags`, `mdb_stat`, and `mdb_env_info`, then iterates records with an `MDB_cursor`. `main()` handles options `-a`, `-s`, `-l`, `-n`, `-p`, `-f`, and `-V`, opens a read-only env/txn/dbi, and enumerates subDBs when requested.

**Control flow:** After option validation and signal setup, the tool opens the environment, starts a read-only transaction, opens the selected DB, then either dumps it directly or iterates main DB keys as subDB names. A volatile `gotsig` flag causes dump iteration to stop with `EINTR`.

**State and persistence:** It is read-only except for optional output file creation via `freopen`. Dump output includes environment map size, map address, max readers, DB page size, flags, and all key/value pairs.

**Dependencies and integration points:** It depends on LMDB cursor/stat APIs and dump/load format compatibility with `mdb_load`.

**Risks and edge cases:** The loop assignment in `while ((rc = mdb_cursor_get(...) == MDB_SUCCESS))` stores a boolean, so `MDB_NOTFOUND` handling may not work as intended. SubDB name allocation is unchecked. `-l` falls through into `-a`, which is intentional but subtle. Tests should round-trip dump/load for print and bytevalue formats, all-subDB mode, list mode, binary keys, signal interruption, and output-file errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_dump.c -->
