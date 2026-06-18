<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_load.c -->
## sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_load.c

**Purpose:** `mdb_load` loads LMDB dump records from stdin or a file into an LMDB environment, supporting full dump headers or plain text key/value input.

**Important APIs, types, and functions:** Globals track mode, subDB name, line number, header version, DB flags, EOF, `MDB_envinfo`, and reusable key/data buffers. `readhdr()` parses dump headers and DB flags. `readline()` reads and decodes print or bytevalue data, growing buffers for long lines. `main()` handles `-f`, `-n`, `-s`, `-N`, `-T`, and `-V`, configures environment maxdbs/readers/mapsize/fixed map, opens/creates DBs, and inserts with `mdb_cursor_put`.

**Control flow:** The loader optionally reads a header, opens the environment, allocates key buffer based on max key size, then loops over dump sections. Each section opens a write transaction and DB, reads key/data pairs until `DATA=END` or EOF, commits every 100 records, and starts a new transaction for the next batch.

**State and persistence:** It mutates the target LMDB environment by creating/opening DBs and inserting records. With `-N`, existing keys/dups are skipped. Headers can influence map size, max readers, fixed map address, and DB flags.

**Dependencies and integration points:** It is the counterpart to `mdb_dump`, depends on LMDB write transactions and cursor APIs, and is included only when internal LMDB tools are built.

**Risks and edge cases:** Header parsing uses `STRLENOF("FORMAT=")` against lowercase `format=` offsets, which happens to be same length but is brittle. Buffer reallocation in `readline()` uses `buf->mv_size+1` after moving the pointer and may be hard to audit. After batch commits, DBI/cursor lifetime is not fully reset/closed in the same pattern as initial open. Tests should cover dump round-trips, `-T` plaintext, no-overwrite behavior, long lines, malformed hex escapes, multiple dump sections, and transactional failure rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/devel/lmdb/mdb_load.c -->
