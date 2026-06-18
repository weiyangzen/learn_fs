# subset-b-008815 research

Grouped research for SQLite tool sources under `sources/storage-engines/sqlite/tool`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mkkeywordhash.c -->
# sources/storage-engines/sqlite/tool/mkkeywordhash.c

## Purpose

Build-time generator for SQLite's SQL keyword lookup code. It starts from the static keyword list, applies `SQLITE_OMIT_*` and feature masks, compresses keyword text, chooses a compact hash table, and prints C code implementing `keywordCode()`, `sqlite3KeywordCode()`, `sqlite3_keyword_name()`, `sqlite3_keyword_count()`, and `sqlite3_keyword_check()`.

## Important APIs, control flow, and dependencies

The central type is `Keyword`, which carries the keyword spelling, token symbol, feature mask, priority, generated hash-chain data, compressed-text offsets, substring embedding metadata, and original spelling. `keywordCompare1()`, `keywordCompare2()`, and `keywordCompare3()` drive the successive qsort passes. `findById()` resolves substring parents, and `reorder()` promotes higher-priority keywords within hash collision chains. `main()` filters disabled keywords, computes hashes using `charMap()` and `HASH_C0/HASH_C1/HASH_C2`, detects embedded keywords and reusable suffix/prefix text, searches hash-table sizes from half to twice the keyword count, then emits arrays and lookup functions to stdout.

## State, persistence, and integration

The program persists nothing itself; its only durable output is generated C source captured by the SQLite build. It depends on parser token names such as `TK_SELECT`, SQLite feature macros, ASCII/EBCDIC branches in generated code, and public keyword APIs expected by SQLite clients. The generated lookup assumes tokens of length at least two for the internal path and returns `TK_ID` for non-keywords through `sqlite3KeywordCode()`.

## Risks and test signals

Risk concentrates in generator determinism and semantic drift: a keyword token or feature mask mismatch changes parser behavior, a bad compression offset corrupts `sqlite3_keyword_name()`, and a weak hash/priority ordering can increase lookup cost or alter token precedence for common keywords. Useful signals are regenerating the keyword source and diffing it, parser tests for all SQL grammar feature combinations, keyword API tests for count/name/check, and builds under omitted features plus ASCII/EBCDIC configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mkkeywordhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mksourceid.c -->
# sources/storage-engines/sqlite/tool/mksourceid.c

## Purpose

Standalone build utility that reads a Fossil manifest and emits SQLite's source id: check-in date plus SHA3-256 of the manifest content. It also verifies every `F` manifest entry against the corresponding working-tree file and marks the source id as modified when any file is missing or hash-mismatched.

## Important APIs, control flow, and dependencies

The file embeds SHA3/Keccak and SHA1 implementations. `SHA3Context`, `KeccakF1600Step()`, `SHA3Init()`, `SHA3Update()`, `SHA3Final()`, and `DigestToBase16()` implement SHA3 output; `SHA1Context`, `SHA1Transform()`, `SHA1Init()`, `SHA1Update()`, `SHA1Final()`, and `sha1sum_file()` support legacy 40-character Fossil hashes. `sha3sum_file()` hashes files for newer manifest entries. `nextToken()` destructively tokenizes manifest lines. `main()` parses `-v`, opens the manifest, excludes lines beginning `# Remove this line` from the manifest hash, extracts the date from `D` records, verifies each `F` file hash, and prints either `date hash` or `date hashalt1` when verification fails.

## State, persistence, and integration

No state is written. The tool reads the manifest and all referenced files by relative path from the current working directory, so it is tightly coupled to the Fossil checkout layout used by SQLite release builds. Endianness handling is embedded in both hash implementations to keep output stable across architectures. The emitted text feeds generated version/source-id constants elsewhere in the SQLite build.

## Risks and test signals

Important risks are manifest parser assumptions, path handling from the current directory, SHA3/SHA1 endianness bugs, and line-buffer truncation for unusual manifest entries. A missing or changed file deliberately changes the suffix rather than failing hard unless verbose diagnostics are requested. Test signals include comparing against Fossil's own manifest hash, running on clean and modified checkouts, verifying legacy SHA1 and SHA3 manifests, and cross-platform byte-for-byte source-id stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/mksourceid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/offsets.c -->
# sources/storage-engines/sqlite/tool/offsets.c

## Purpose

Diagnostic utility that locates TEXT or BLOB payload offsets for one column of one table in an SQLite database file. It prints each rowid, field size, and absolute file offset for the requested column, making it useful for low-level storage inspection and corruption/debug work.

## Important APIs, control flow, and dependencies

`GState` holds the current database file, page size, target root page, target column number, a page stack, and an error string. `ofstRootAndColumn()` opens the database through SQLite, queries `sqlite_schema`, `PRAGMA table_info`, and `PRAGMA page_size`, then the rest of the code reads the file directly with stdio. `ofstPushPage()` and `ofstPopPage()` manage recursive page traversal. `ofst2byte()`, `ofst4byte()`, `ofstVarint()`, `ofstSerialSize()`, and `ofstInFile()` decode SQLite b-tree record structures. `ofstWalkInteriorPage()` follows child pages, `ofstWalkLeafPage()` decodes table leaf cells and serial types, and `main()` optionally enables `--trace` before walking the root page.

## State, persistence, and integration

The tool is read-only. It uses SQLite APIs only for schema discovery and then trusts raw on-disk b-tree layout. It handles table b-tree page types 5 and 13, uses a fixed page stack depth of 20, and explicitly skips rows whose payload overflows by printing an overflow comment instead of following overflow pages. It assumes the requested table has rowid-table leaf records shaped like standard table b-tree cells.

## Risks and test signals

Risks include malformed pages causing out-of-bounds reads, deeply nested b-trees exceeding the stack, overflow columns being unreported, and schema/file races between SQLite schema reads and raw file traversal. Test signals are known databases with fixed page sizes and predictable text/blob offsets, `--trace` output matching page metadata, behavior on overflow payloads, and comparison against `dbstat` or independent page decoders.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/pagesig.c -->
# sources/storage-engines/sqlite/tool/pagesig.c

## Purpose

Small diagnostic program that computes a signature for every page in one or more SQLite database files. It is intended to help analyze logs from `ext/misc/vfslog.c` by producing stable, compact page-content identifiers.

## Important APIs, control flow, and dependencies

`vlogSignature()` emits either a full hex dump for blocks of 16 bytes or less, or the first eight bytes plus a simple 64-bit additive checksum for larger blocks. `computeSigs()` opens a file, reads the database header, decodes the page size from bytes 16 and 17, validates it as a power of two, then reads and signs each full page. `main()` applies `computeSigs()` to each command-line file.

## State, persistence, and integration

The utility is read-only and depends only on stdio. It trusts the SQLite database header enough to determine page size and treats a header value of 1 as 65536 bytes. It does not parse b-trees or journals; the output is a page-number to signature list suitable for comparing page writes with VFS logs.

## Risks and test signals

The checksum is diagnostic, not cryptographic, and includes host-dependent behavior from casting page bytes to `unsigned int *`. Short files, invalid page sizes, and partial final pages are skipped with minimal diagnostics. Test signals include known database files, modified single pages producing changed signatures, invalid page-size handling, and comparison with vfslog page write traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/pagesig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/rollback-test.c -->
# sources/storage-engines/sqlite/tool/rollback-test.c

## Purpose

Utility for creating and checking databases with hot journals, especially across machines with different architectures. It can create a deterministic test database, intentionally exit mid-transaction to leave rollback or WAL recovery state, and later verify that recovery restores correct content.

## Important APIs, control flow, and dependencies

The program links SQLite directly through `sqlite3.h`. `openDb()` opens a database and exits on failure. `execCallback()` accumulates result text in the global `zReply`, and `runSql()` executes SQL and surfaces SQLite errors. `main()` supports `new`, `check`, and `crash`: `new` accepts encoding and page-size options, creates table `t1`, expands it to 1024 rows, updates text values, and creates an index; `check` runs `PRAGMA integrity_check` and verifies all values; `crash` optionally switches journal mode to WAL or DELETE, starts a transaction, updates all rows, and exits without closing/committing.

## State, persistence, and integration

This is deliberately stateful: it creates database content and can leave hot rollback journal or WAL state on disk by terminating abruptly. The `check` command relies on SQLite opening the database and performing normal recovery before running validation SQL. Options let tests vary text encoding, page size, and journal mode.

## Risks and test signals

Risks are intentional: abrupt `exit(0)` can leave files that depend on OS flush semantics, filesystem behavior, and SQLite journaling mode. The fixed-size reply buffer can truncate unexpected query output, though normal checks are small. Test signals are `Ok` from `check`, integrity_check output, row-content validation after moving files across architectures, and separate runs for rollback and WAL journal modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/rollback-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showdb.c -->
# sources/storage-engines/sqlite/tool/showdb.c

## Purpose

Comprehensive SQLite database-file inspection tool. It can dump raw pages, decode database headers, decode b-tree pages and individual cells, inspect freelist trunks, report page usage for every page, and inspect pointer-map coverage.

## Important APIs, control flow, and dependencies

Global `g` stores page geometry, file handles, output options, page-use annotations, and optional timestamp VFS tags. `fileOpen()`, `fileRead()`, `fileGetsize()`, and `fileClose()` abstract reads either through SQLite's VFS file pointer (`SQLITE_FCNTL_FILE_POINTER`) or raw OS APIs with `--raw`. Header and byte output are handled by `print_byte_range()`, `print_page()`, `print_decode_line()`, and `print_db_header()`. B-tree decoding uses `decodeVarint()`, `decodeInt32()`, `localPayload()`, `describeContent()`, `describeCell()`, `decodeCell()`, and `decode_btree_page()`. Freelist and whole-file usage reporting use `decode_trunk_page()`, `page_usage_msg()`, `page_usage_cell()`, `page_usage_btree()`, `page_usage_freelist()`, `page_usage_ptrmap()`, `page_usage_report()`, and `ptrmap_coverage_report()`. `main()` parses switches (`--raw`, `--csv`, `--tmstmp`) and commands including `dbheader`, `pgidx`, `ptrmap`, page ranges, `NNNb*`, and `NNNt*`.

## State, persistence, and integration

The program is read-only, but by default reads via SQLite's VFS so URI filenames and VFS-specific behavior can be honored. It opens a separate SQLite connection during `pgidx` to query `SQLITE_MASTER`, enables `PRAGMA writable_schema=ON`, and then recursively marks b-tree, overflow, freelist, and pointer-map pages. It understands page-1's 100-byte database header, reserved bytes, autovacuum pointer-map pages, and optional 16-byte `tmstmpvfs` tags stored in reserved space.

## Risks and test signals

Risks are mostly parser robustness and stale file-format assumptions: malformed cell offsets can cause confusing output or bounds errors, page usage is heuristic for corrupt pages, and CSV fields are derived from human-readable messages. The default VFS path can observe SQLite-level file views that differ from raw bytes. Test signals include decoding known fixture databases, `pgidx` coverage with no duplicate or out-of-range page errors, `ptrmap` agreement on autovacuum databases, b-tree cell decode matching SQL content, and both raw and VFS read modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showjournal.c -->
# sources/storage-engines/sqlite/tool/showjournal.c

## Purpose

Rollback-journal decoder that prints journal headers and page records from an SQLite rollback journal file.

## Important APIs, control flow, and dependencies

The global state tracks page size, sector size, file handle, file size, and checksum nonce. `read_content()` reads arbitrary byte ranges with zero-fill on short read. `print_decode_line()` displays big-endian integer fields. `decode_journal_header()` reads a 64-byte header at a sector boundary, prints header magic parts, page count, checksum nonce, initial database size, sector size, and page size, and updates global page/sector parameters. `print_page()` prints the page number field for a journal page record. `main()` walks the file by sectors and records until EOF.

## State, persistence, and integration

The tool is read-only and depends only on stdio. It tracks the page and sector sizes from each decoded journal header and uses them to advance through page records. If the header page count is zero, it estimates record count from file size. It does not validate page checksums or restore database pages.

## Risks and test signals

Risks include incomplete checksum coverage, simplistic handling of malformed headers, integer-sized file offsets, and confusing output if sector/page sizes are corrupt. Test signals include journals produced by controlled transactions, matching page numbers and header metadata from SQLite's journal format, behavior with zero page-count journals, and short-read diagnostics on truncated files.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showjournal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showlocks.c -->
# sources/storage-engines/sqlite/tool/showlocks.c

## Purpose

POSIX advisory-lock inspector for a single file. It enumerates lock ranges over the first two billion bytes and reports lock start, length, owning pid, and read/write lock type.

## Important APIs, control flow, and dependencies

`showLocksInRange()` maintains a dynamically resized pending range list. For each range, it calls `fcntl(fd, F_GETLK, ...)` with a write-lock probe, prints any conflicting lock, then schedules the unlocked subranges before and after that lock. `main()` opens the target file read/write, invokes the range scan over `0..MX_LCK`, prints `no locks` if none are found, and closes the descriptor.

## State, persistence, and integration

The tool modifies no file content but requires POSIX `fcntl()` lock semantics and read/write open permissions. It is useful around SQLite because SQLite's Unix VFS uses advisory byte-range locks on database files and related lock bytes. It does not know SQLite lock-byte names; it reports raw ranges.

## Risks and test signals

Risks include platform limitation to POSIX locking, inability to inspect locks without opening the file read/write, integer truncation in printed offsets, and races as locks change while scanning. Test signals are controlled processes holding read/write byte-range locks, output covering split ranges without duplicates, and no-lock output after lock release.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showlocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showshm.c -->
# sources/storage-engines/sqlite/tool/showshm.c

## Purpose

Decoder for SQLite WAL-index shared-memory (`-shm`) files. It prints the two `WalIndexHdr` copies and the `WalCkptInfo` checkpoint/read-mark area from the beginning of the shm file.

## Important APIs, control flow, and dependencies

`getContent()` reads bytes from the opened file descriptor. `print_decode_line()` displays fields as big-endian, native-byte-order, hex, or page-size values using `FG_HEX`, `FG_NBO`, and `FG_PGSZ`. `print_index_hdr()` decodes each 48-byte wal-index header copy, including version, transaction counter, initialization flag, checksum byte order, page size, mxFrame, database page count, frame checksum, salts, and header checksum. `print_ckpt_info()` decodes `nBackfill`, five read marks, lock bytes, `nBackfillAttempted`, and padding. `main()` reads the first 136 bytes and prints all structures.

## State, persistence, and integration

The program is read-only and uses OS file APIs. It assumes the shm file begins with SQLite's wal-index layout and interprets some fields in native byte order because the wal-index is host-local shared memory, not a portable database file format. It does not inspect hash tables or later shm regions.

## Risks and test signals

Risks include native-endian interpretation on a file copied between architectures, short reads not checked, and version/layout drift if SQLite changes wal-index internals. Test signals include live WAL databases with known frame counts, consistency between header copies, read-mark values matching active readers/checkpoints, and comparison against WAL header salts/checksums.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showshm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showstat4.c -->
# sources/storage-engines/sqlite/tool/showstat4.c

## Purpose

Utility that queries and decodes the `sqlite_stat4` table in a database, printing each index sample as raw hex and as decoded record values.

## Important APIs, control flow, and dependencies

`decodeVarint()` decodes SQLite varints from stat4 sample records. `main()` opens the database with SQLite, prepares `SELECT tbl||'.'||idx, nEq, nLT, nDLt, sample FROM sqlite_stat4 ORDER BY 1`, groups output by table/index, prints cardinality strings, hex-dumps the sample blob, then decodes the record header serial types and payload fields. It handles NULL, integer serial types, floating point, zero/one constants, blobs, and printable/escaped text.

## State, persistence, and integration

The utility is read-only and depends on the database already having `sqlite_stat4` rows, typically from `ANALYZE` with STAT4 support. Its binary record decoding mirrors SQLite record serial-type rules, but only for display. It does not alter planner statistics.

## Risks and test signals

Risks include malformed sample blobs, missing `sqlite_stat4`, byte-order subtleties for double printing, and text escaping that is diagnostic rather than full SQL literal reconstruction. Test signals include databases with known ANALYZE output, samples covering all serial types, graceful error display for corrupt blobs, and output grouped by `tbl.idx`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showstat4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showtmlog.c -->
# sources/storage-engines/sqlite/tool/showtmlog.c

## Purpose

Decoder for 16-byte `tmstmpvfs` log records. It renders page and WAL activity either as human-readable text or as CSV.

## Important APIs, control flow, and dependencies

`decodeTimestamp()` converts the six-byte big-endian millisecond timestamp field to `YYYY-MM-DD HH:MM:SS.SSS`, treating zero and far-future values specially. `renderCSV()` and `renderText()` decode record type, transaction flag, page number, frame number, pid, salt, and checkpoint events. Recognized opcodes include open-db, open-wal, wal-page, db-page, checkpoint start/page/end, wal-reset, close-wal, and close-db. `main()` parses `--csv`, `--help`, and one or more log filenames, prints a CSV header when requested, and reads complete 16-byte records until EOF.

## State, persistence, and integration

The tool reads log files only. It is coupled to the binary record layout emitted by SQLite's timestamp VFS extension and can label multiple input files with a sequential file number in CSV output. It shares timestamp decoding logic with `showdb.c`'s optional timestamp page-tag reporting.

## Risks and test signals

Risks include silent ignore of trailing partial records, CSV output that does not escape filenames because filenames are not included, and layout drift with future VFS log versions. Test signals include synthetic records for each opcode, CSV/text parity for the same file, bad-date handling, multi-file numbering, and comparison with observed WAL/page events.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showtmlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showwal.c -->
# sources/storage-engines/sqlite/tool/showwal.c

## Purpose

SQLite WAL-file inspection utility. It prints WAL headers, summarizes frames with checksum verification, dumps full frame content, decodes frame payload pages as b-trees, and can truncate a WAL after a specified frame on non-MSVC builds.

## Important APIs, control flow, and dependencies

Global state tracks WAL page size, file descriptor, frame count, and hex formatting. `Cksum`, `getInt32()`, `swab32()`, and `extendCksum()` implement SQLite WAL checksum accumulation with byte-order detection. `getContent()`, `print_byte_range()`, `print_decode_line()`, `print_wal_header()`, `print_oneline_frame()`, and `print_frame()` handle raw display. The b-tree page decoder reuses local versions of `decodeVarint()`, `localPayload()`, `describeContent()`, `describeCell()`, and `decode_btree_page()`. `main()` reads the page size from WAL header offset 8, computes frame count, and supports `header`, frame ranges, `NNNb*` b-tree decode arguments, and `NNNtruncate`.

## State, persistence, and integration

Most modes are read-only, but the `truncate` suffix intentionally calls `truncate()` to shorten the WAL. The tool depends on the WAL file format: 32-byte header, 24-byte frame headers, salts, commit db-size field, and page payloads. It decodes the frame payload using database b-tree page rules, but page number and frame number are distinct.

## Risks and test signals

Risks include unchecked short reads, host alignment assumptions while checksuming 32-bit words, accidental destructive use of `truncate`, and stale b-tree decode assumptions. Checksum mismatch output is a strong corruption signal, while b-tree decode is diagnostic. Test signals include WALs with known frame counts, valid and intentionally corrupted checksums, page-size boundary cases, frame range dumps, and b-tree frame decoding that matches the database page content.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/showwal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqldiff.c -->
# sources/storage-engines/sqlite/tool/sqldiff.c

## Purpose

Command-line SQLite database differ. It compares DB1 to DB2 and emits SQL that transforms DB1 into DB2, or alternative outputs such as summaries, RBU data tables, or binary changesets.

## Important APIs, control flow, and dependencies

Global `g` carries options, debug flags, schema-compare state, and the main SQLite connection with DB2 attached as `aux`. Error and preparation helpers include `cmdlineError()`, `runtimeError()`, `safeId()`, `db_prepare()`, and `namelistFree()`. `columnNames()` discovers primary-key columns, rowid accessibility, schema-defined versus true primary keys, and special `sqlite_schema` comparison keys. `printQuoted()` formats SQLite values as SQL literals. `dump_table()` recreates tables and rows from `aux`; `diff_one_table()` builds a compound SELECT for changed, deleted, and inserted rows and emits DDL/DML. `checkSchemasMatch()` gates RBU and changeset modes. RBU support uses Fossil delta helpers (`hash_*`, `putInt()`, `checksum()`, `rbuDeltaCreate()`), `getRbudiffQuery()`, and `rbudiff_one_table()`. Summary mode is `summarize_one_table()`. Changeset mode uses `putsVarint()`, `putValue()`, and `changeset_one_table()` to write SQLite changeset-like binary records. Virtual table filtering is handled by `module_name_func()` and `all_tables_sql()`. `main()` parses options, loads extensions, opens and attaches databases read-only, optionally wraps SQL output in a transaction, chooses the diff callback, and iterates selected tables.

## State, persistence, and integration

The input databases are opened read-only. Text SQL modes write to stdout unless `--changeset FILE` opens a binary output file. `--rbu` emits SQL to populate RBU tables and an `rbu_count` table. `--changeset` disables transaction wrapping. `--lib` enables extension loading so virtual table modules or custom collations can be available during comparison. The tool intentionally does not handle trigger or view differences, as noted at the end of `main()`.

## Risks and test signals

Risks include primary-key inference edge cases, inaccessible rowids, schema mismatches causing drop/recreate output, virtual table shadow-table filtering mistakes, control-character SQL literal formatting, binary changeset compatibility, and RBU delta generation for blobs. Large tables can be expensive because comparisons are SQL joins ordered by primary key. Test signals include fixture pairs for inserts/updates/deletes, WITHOUT ROWID and INTEGER PRIMARY KEY tables, hidden rowid-name conflicts, `sqlite_schema` comparisons, virtual tables with `--vtab`, extension loading, `--summary`, `--rbu`, `--changeset`, and applying emitted SQL to DB1 then comparing against DB2.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqldiff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqlite3_analyzer.c.in -->
# sources/storage-engines/sqlite/tool/sqlite3_analyzer.c.in

## Purpose

Template source for the `sqlite3_analyzer` executable, which embeds SQLite, Tcl integration, and the `spaceanal.tcl` script to report database space utilization.

## Important APIs, control flow, and dependencies

The template sets `TCLSH_INIT_PROC` to `sqlite3_analyzer_init_proc`. When `INCLUDE_SQLITE3_C` is active, it includes `sqlite3.c` with analyzer-friendly compile-time options such as `SQLITE_ENABLE_DBSTAT_VTAB`, `SQLITE_THREADSAFE=0`, omitted load extensions, omitted shared cache, and disabled memory status. It always includes `$ROOT/src/tclsqlite.c`, and on Windows includes `sqlite3_stdio` plus a replacement `puts` command, `subst_puts()`, that writes through `sqlite3_fputs()`. `sqlite3_analyzer_init_proc()` installs the Windows `puts` shim when needed and returns the embedded `spaceanal.tcl` script between `BEGIN_STRING` and `END_STRING`.

## State, persistence, and integration

This is not compiled directly as ordinary C; it is processed by SQLite's build/template machinery that expands `INCLUDE`, `IFDEF`, `ELSE`, `ENDIF`, and string markers. Runtime behavior comes from the embedded Tcl script and SQLite's `dbstat` virtual table. The analyzer reads target databases and writes reports to stdout/stderr.

## Risks and test signals

Risks include build-template expansion errors, mismatch between embedded SQLite compile options and the analyzer script's expectations, Tcl command behavior differences on Windows, and stale `spaceanal.tcl` coupling. Test signals include successful generation/compilation both with bundled `sqlite3.c` and external `sqlite3.h`, analyzer execution on known databases, dbstat availability, and Windows output behavior through the substituted `puts`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/tool/sqlite3_analyzer.c.in -->
