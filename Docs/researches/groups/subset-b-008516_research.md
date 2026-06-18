# subset-b-008516 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_copy.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mdb_copy.c

## Purpose
`mdb_copy.c` implements the LMDB backup/copy command-line tool. It opens an existing environment read-only and copies it either to stdout or to a destination path, optionally using compact-copy mode and optional encrypted-environment hooks.

## Important APIs, types, and functions
The only local helper is an empty `sighandle` used to interrupt blocking writes cleanly. `main` parses `-n`, `-L`, `-v`, `-c`, `-V`, `-m`, and `-w`, creates an `MDB_env`, optionally loads crypto hooks with `mdb_modload`/`mdb_modsetup`, opens the environment with `mdb_env_open`, then calls `mdb_env_copyfd2` or `mdb_env_copy2`. It uses `MDB_CP_COMPACT`, `MDB_NOSUBDIR`, `MDB_NOLOCK`, `MDB_PREVSNAPSHOT`, and platform-specific stdout descriptors.

## Control flow
Argument parsing builds environment and copy flags before validating `srcpath [dstpath]`. Signal handlers are installed for pipe, hangup, interrupt, and terminate signals. The tool then creates the environment, attaches crypto if requested, opens the source read-only, copies to stdout when no destination is provided or to a filesystem destination otherwise, reports the failing action on error, and always closes the environment and unloads a module handle if present.

## State and persistence behavior
The source environment is read-only. The destination receives either a byte-for-byte or compacted LMDB copy. `MDB_PREVSNAPSHOT` allows copying a previous snapshot, while `MDB_NOLOCK` avoids lock-table coordination and shifts consistency responsibility to the caller.

## Dependencies and integration points
The file integrates with public LMDB environment copy APIs and with the local dynamic crypto module helper API. Build integration must link the platform dynamic-loader implementation when module support is used.

## Risks and edge cases
`-m` and `-w` consume the next argv entry without local bounds checks before the final argc validation, so malformed option ordering relies on later usage failure or may read a missing pointer. `MDB_NOLOCK` can produce unsafe copies if writers are active. Copying to stdout depends on SIGPIPE behavior and binary-safe descriptors. Crypto setup must match the source database or open/copy will fail.

## Test signals
Useful tests include copying normal and compact databases, stdout piping, NOSUBDIR environments, previous snapshots, encrypted databases with and without passwords, and interruption or broken-pipe exits.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_drop.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mdb_drop.c

## Purpose
`mdb_drop.c` is the LMDB command-line tool for clearing or deleting the main database or a named subdatabase inside an environment.

## Important APIs, types, and functions
`usage` prints the command syntax. `dumpsig` sets the global `gotsig`, although the main flow does not currently branch on it. `main` uses `getopt` to parse `-d`, `-s`, `-n`, `-L`, `-V`, `-m`, and `-w`; then it calls `mdb_env_create`, optional `mdb_modload`/`mdb_modsetup`, `mdb_env_set_maxdbs`, `mdb_env_open`, `mdb_txn_begin`, `mdb_open`, `mdb_drop`, and `mdb_txn_commit`.

## Control flow
After option validation, the tool installs signal handlers, creates the environment, loads optional crypto hooks, sets `maxdbs` to allow subdatabase opens, and opens the target environment. A write transaction opens either the named subdatabase or main database, then `mdb_drop(txn, dbi, delete)` either empties it or removes it depending on `-d`. Cleanup labels abort an uncommitted transaction and close/unload resources.

## State and persistence behavior
This is a destructive writer. Without `-d`, database contents are removed but the DBI remains. With `-d`, the database itself is deleted from the environment. The change persists only after `mdb_txn_commit`; earlier failures abort the transaction.

## Dependencies and integration points
The tool depends on the LMDB write transaction API, subdatabase metadata semantics, POSIX `getopt`, and optional crypto-module hooks.

## Risks and edge cases
The default target is the main DB, so omitting `-s` can erase primary data. `MDB_NOLOCK` is dangerous for a writer if other processes are active. `gotsig` is set but unused, so a signal does not proactively cancel after handlers run. A failed commit jumps through `txn_abort` with `txn` still non-null; LMDB commit failures should leave the transaction invalid, so this path depends on library behavior.

## Test signals
Tests should cover emptying versus deleting subDBs, main DB drops, encrypted databases, NOSUBDIR, failure to open missing subDBs, and recovery after aborted transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_drop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_dump.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mdb_dump.c

## Purpose
`mdb_dump.c` serializes LMDB databases in a Berkeley DB-compatible dump format, or emits LMDB incremental dumps from a transaction ID.

## Important APIs, types, and functions
`flagbit` maps LMDB DB flags to dump header keywords. `hex`, `text`, and `dobyte` encode keys and values in printable or hex form. `dumpit` emits headers, opens a cursor, iterates records with `MDB_NEXT`, and writes `DATA=END`. `main` handles `-a`, `-s`, `-l`, `-f`, `-i`, `-n`, `-L`, `-p`, `-v`, `-V`, `-m`, and `-w`.

## Control flow
The command parses options, installs signal handlers, creates and optionally crypto-configures an environment, opens it read-only, and branches to incremental dump APIs when `-i` is supplied. Normal dumps optionally redirect stdout, begin a read-only transaction, open a DBI, then either dump one database or scan the main database for subdatabase records with `mdb_cursor_is_db`. `-l` lists subdatabase names instead of dumping their contents.

## State and persistence behavior
All normal database access is read-only and snapshot based. `MDB_PREVSNAPSHOT` requests an older snapshot; `MDB_NOLOCK` bypasses reader locking. Output includes map size, map address, max readers, page size, DB flags, and each key/value pair, so it captures logical database contents and load-critical metadata.

## Dependencies and integration points
The dump format is consumed by `mdb_load.c`. Incremental mode integrates with `mdb_env_incr_dump` and `mdb_env_incr_dumpfd`. Crypto handling uses `module.c` helpers.

## Risks and edge cases
Printable mode only escapes backslash and non-printable bytes, so consumers must use the matching parser. Listing all DBs relies on main-DB entries being named subdatabases. Incremental dumps bypass the text header format. Signal interruption returns `EINTR`, but partial output may already be written. `-L` can expose inconsistent snapshots when used carelessly.

## Test signals
Round-trip tests with `mdb_load`, printable and bytevalue formats, all supported DB flags, all-subDB/list modes, output-file errors, incremental dump/load, encrypted DBs, and interrupted stdout writes are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_load.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mdb_load.c

## Purpose
`mdb_load.c` loads databases from `mdb_dump` text output, plaintext key/value input, or LMDB incremental dump streams.

## Important APIs, types, and functions
`readhdr` parses dump headers into global environment info, page size, subdatabase name, and DB flags. `readline` decodes one key or value in print, bytevalue, no-header, or plaintext mode. `unhex` decodes hex pairs. `greater` is a comparator used to enable append loading without full ordering checks. `main` configures the environment and batches cursor puts.

## Control flow
The command parses input-mode and environment options, optionally reopens stdin, reads the first dump header unless `NOHDR` is set, creates and optionally crypto-configures the environment, and branches to `mdb_env_incr_loadfd` for incremental mode. Normal mode applies header-derived max readers, mapsize, page size, and fixed-map address before opening the environment. It then loops over dump sections: begin write transaction, open/create the DBI, optionally set append comparators, open a cursor, read key/value pairs, put records, commit every 100 records, sync if `MDB_NOSYNC`, close DBI, and continue until EOF.

## State and persistence behavior
The loader mutates the target environment. Header metadata can change environment map size, max readers, page size, and fixed mapping. `-N` avoids overwriting existing records. `-Q`/default `MDB_NOSYNC` accelerates loading but relies on a final forced sync for durability. Incremental mode delegates persistence to LMDB's incremental loader.

## Dependencies and integration points
It is tightly coupled to `mdb_dump.c`'s header and data encoding. It uses LMDB environment setters, DB flag constants, cursor puts, duplicate handling, and optional crypto-module setup.

## Risks and edge cases
Most parsing state is global, so malformed multi-database input can leak prior header values. `readline` resizes buffers but uses C string length, so embedded NUL input in text mode is treated as invalid. Append mode changes comparators to a comparator that always returns greater, relying on the caller's sorted input. A commit every 100 records opens a new transaction but keeps using the earlier DBI handle, which is valid only under LMDB's DBI lifetime rules. Bad dumps can partially load earlier committed batches.

## Test signals
Round trips from bytevalue and printable dumps, multi-subDB dumps, duplicate/fixed/integer flags, no-overwrite behavior, plaintext `-T`, append `-a`, incremental streams, crash between batches, encrypted inputs, and malformed escape/header lines should be covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_stat.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mdb_stat.c

## Purpose
`mdb_stat.c` is the LMDB environment inspection tool. It prints environment information, reader table state, freelist details, and B-tree statistics for the main DB or subdatabases.

## Important APIs, types, and functions
`prstat` formats `MDB_stat` fields. `main` parses `-a`, `-s`, `-e`, repeated `-f`, repeated `-r`, `-n`, `-L`, `-v`, `-V`, `-m`, and `-w`, then uses `mdb_env_stat`, `mdb_env_info`, `mdb_reader_list`, `mdb_reader_check`, `mdb_txn_begin`, `mdb_cursor_open`, `mdb_stat`, and `mdb_dbi_open`.

## Control flow
After opening a read-only environment with optional crypto hooks, the tool prints environment info if requested. Reader-table mode lists readers and, with repeated `-r`, clears stale readers before listing again. Freelist mode scans DBI 0 records to count free pages and optionally prints spans and page IDs. It then opens the requested DBI, prints its stats, and with `-a` scans named subdatabase entries and prints each subDB's stats.

## State and persistence behavior
Most behavior is read-only. The exception is `mdb_reader_check`, which can clean stale reader table slots. `MDB_PREVSNAPSHOT` changes the snapshot inspected. Freelist introspection reads LMDB internal DBI 0 state directly.

## Dependencies and integration points
The tool integrates with LMDB public stat APIs and internal freelist layout conventions where freelist data begins with a count followed by page IDs. Optional encryption support mirrors other LMDB utilities.

## Risks and edge cases
Freelist decoding assumes stable internal record layout and can mislead if that representation changes. `MDB_NOLOCK` affects reader table accuracy. `-r` without DB/stat options exits after reader output. `maxdbs` is set to 4 only for subDB/all modes; environments with many named DBs are still scanned by opening one at a time.

## Test signals
Useful tests include environment info, reader list/check behavior with stale readers, freelist verbosity levels, all-subDB scans, previous snapshot reads, encrypted environments, and corrupted freelist sequence detection output.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mdb_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/midl.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/midl.c

## Purpose
`midl.c` implements LMDB's internal ID-list and ID-to-pointer-list utilities used for page number lists, dirty-page tracking, and related internal structures.

## Important APIs, types, and functions
For `MDB_IDL`, it provides `mdb_midl_search`, `mdb_midl_alloc`, `mdb_midl_free`, `mdb_midl_shrink`, `mdb_midl_need`, append helpers, `mdb_midl_xmerge`, and `mdb_midl_sort`. For `MDB_ID2L`, it provides search, insert, append, alloc/free, and grow helpers. When `MDB_RPAGE_CACHE` is enabled, it also provides `MDB_ID3L` search/insert helpers.

## Control flow
The IDL routines maintain arrays whose visible pointer starts after a hidden allocation-length slot. Searches are binary searches over descending IDLs or ascending ID2L/ID3L lists. Appends grow capacity with `realloc` when needed. Sorting uses quicksort with median selection and insertion sort for small ranges. Merge walks from the tails of two descending IDLs and writes a merged descending result in place.

## State and persistence behavior
The file manages heap memory only; it does not persist data directly. Its data structures represent persistent LMDB page IDs while transactions are being built or reconciled, so ordering and capacity correctness affect database file consistency indirectly.

## Dependencies and integration points
`mdb.c` and other internals include `midl.h` for page-list management. The code depends on `lmdb.h` integer typedefs and on the invariant that `ids[0]` is a count while `ids[-1]` is capacity for allocated IDLs.

## Risks and edge cases
The hidden header pointer convention is efficient but fragile: callers must free the shifted pointer with `mdb_midl_free`, not plain `free`. Several helpers assume enough destination capacity. Sorting is descending for `MDB_IDL` while `MDB_ID2L` is ascending, so mixing assumptions can corrupt search results. Return codes use both `ENOMEM` and negative sentinel values depending on type.

## Test signals
Focused tests should cover duplicate insertion rejection, capacity growth and shrink, search insertion points at boundaries, sort order, merge correctness with adjacent page IDs, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/midl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/midl.h -->
# sources/storage-engines/lmdb/libraries/liblmdb/midl.h

## Purpose
`midl.h` declares LMDB's internal ID-list types, size constants, macros, and helper prototypes for managing page-ID collections and ID-to-pointer collections.

## Important APIs, types, and functions
It defines `MDB_ID`, `MDB_IDL`, IDL size limits (`MDB_IDL_DB_SIZE`, `MDB_IDL_UM_SIZE`, and max variants), macros such as `MDB_IDL_SIZEOF`, `MDB_IDL_FIRST`, `MDB_IDL_LAST`, and `mdb_midl_xappend`, plus prototypes for all `mdb_midl_*` helpers. It also defines `MDB_ID2`, `MDB_ID2L`, and optional `MDB_ID3`/`MDB_ID3L` cache structures under `MDB_RPAGE_CACHE`.

## Control flow
The header has no runtime control flow. It codifies layout and ordering contracts: `MDB_IDL` stores a count in element 0 and IDs from 1..count in descending order, while allocated IDLs also keep capacity at `ids[-1]`; `MDB_ID2L` stores count in `ids[0].mid` and sorted items afterward.

## State and persistence behavior
The header defines in-memory state structures. These structures are used by LMDB internals to describe database page IDs and dirty-page mappings during transactions, indirectly protecting persistent page allocation and free-list correctness.

## Dependencies and integration points
It includes `lmdb.h` for `mdb_size_t` and conditional compile flags, and exposes C linkage for C++ consumers. It is not part of the public user API despite depending on public LMDB typedefs.

## Risks and edge cases
Macros directly index shifted pointers and can read or write out of bounds if callers pass unallocated or undersized arrays. The comment notes many legacy macros are unused; changing constants can affect stack usage, heap growth, and maximum freelist sizes. Optional `MDB_ID3` fields are only available when read-page caching is enabled.

## Test signals
Build tests with and without `MDB_RPAGE_CACHE`, unit tests for macro expectations, and integration tests stressing dirty-page and free-list growth validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/midl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/module.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/module.c

## Purpose
`module.c` provides helper routines for dynamically loading LMDB crypto modules and applying their checksum/encryption hooks to an environment.

## Important APIs, types, and functions
`mdb_modload` loads a shared library and resolves a hook function, defaulting to symbol `MDB_crypto`, then stores the returned `MDB_crypto_funcs`. `mdb_modunload` releases the platform module handle. `mdb_modsetup` installs checksum and encryption callbacks with `mdb_env_set_checksum` and `mdb_env_set_encrypt`, deriving an encryption key from a password when possible.

## Control flow
The implementation branches between Windows `LoadLibrary`/`GetProcAddress`/`FreeLibrary` and POSIX `dlopen`/`dlsym`/`dlclose`. On load failure or missing hook symbol, it sets an error message and releases any partial handle. Setup installs checksum hooks first; if an encryption function and password are provided, it fills a stack key buffer either through `mcf_str2key` or by copying the password, then zeroes the key buffer after configuring the environment.

## State and persistence behavior
The file mutates LMDB environment configuration before `mdb_env_open`. It does not persist data itself, but its hooks determine on-disk encryption, checksum size, and page validation behavior.

## Dependencies and integration points
LMDB utilities and encrypted tests call these helpers. Runtime modules must expose an `MDB_crypto_hooks` function returning `MDB_crypto_funcs`.

## Risks and edge cases
`keybuf` is fixed at 2048 bytes and assumes module key sizes fit. `strncpy` does not guarantee null termination, but the key is binary and sized by `mcf_keysize`. If no password is provided, encryption hooks are not installed even when the module supports encryption. Error messages are static on Windows and less diagnostic than POSIX `dlerror`.

## Test signals
Tests should cover successful module load/unload, missing shared library, missing hook symbol, checksum-only modules, encryption modules with password derivation, oversized key sizes, and cross-platform loader behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mplay.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mplay.c

## Purpose
`mplay.c` replays text logs of LMDB API calls into live child processes, reconstructing environments, transactions, cursors, and data operations for debugging or deterministic reproduction.

## Important APIs, types, and functions
It defines mapping tables `envpair`, `txnpair`, `crspair`, and `pidpair` to translate logged pointer/process IDs to runtime LMDB objects. Lookup helpers add/find/delete environments, transactions, cursors, and child processes. `child` parses replay commands and executes LMDB APIs. `addpid`, `findpid`, `delpid`, and `reaper` manage forked workers. `main` dispatches input lines prefixed with process IDs.

## Control flow
The parent reads log lines, ignores non-command lines, creates a child per logged process ID, writes the LMDB call line to that child over a pipe, and waits for a one-byte acknowledgment. Each child parses commands such as environment create/open/close, transaction begin/commit/abort, DBI open/close, cursor open/put/delete, put, and delete. Hex-encoded keys and data are decoded into reusable buffers before LMDB calls. Logged process kill lines trigger child shutdown.

## State and persistence behavior
Replay creates and mutates actual LMDB environments named in the log. Transactions, cursors, and environments are tracked in fixed-size in-memory arrays. If logged data omits a value payload, generated data uses the current transaction ID text, making replay state partly synthetic.

## Dependencies and integration points
The tool depends on POSIX `fork`, `pipe`, `dup2`, `waitpid`, and signals, so it is not Windows-oriented. It integrates with LMDB's public C API and with log formats that print pointer values and hex payloads in the expected layout.

## Risks and edge cases
Fixed maxima of 16 environments, transactions, cursors, and child processes can assert on larger traces. Parsing is by `strncmp`, `sscanf`, and delimiter mutation, so malformed logs can crash. Signal handling and `killpid` coordination assume one child reap at a time. The tool can overwrite real database paths from logs.

## Test signals
Replay tests should cover multi-process traces, interleaved transactions and cursors, generated data paths, duplicate/notfound tolerances, child exit on env close, max-table assertions, and malformed or truncated command lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mplay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest.c

## Purpose
`mtest.c` is a toy regression program that exercises basic LMDB main-database writes, duplicate-skip behavior, deletes, cursor scans, and cursor restarts.

## Important APIs, types, and functions
The program uses `E`, `RES`, and `CHECK` macros to enforce LMDB return codes. `main` calls environment setup APIs, transaction begin/commit/abort, `mdb_dbi_open`, `mdb_put`, `mdb_del`, `mdb_env_stat`, `mdb_cursor_open`, and cursor traversal operations including `MDB_NEXT`, `MDB_LAST`, `MDB_PREV`, and `MDB_FIRST`.

## Control flow
It generates a random number of integer-derived string records, opens `./testdb` with fixed mapping, inserts records with `MDB_NOOVERWRITE`, prints all records in a read transaction, deletes a random stride of records in individual transactions, then scans forward/backward. It also deletes the first 50 records using a cursor, tests cursor reuse within the same write transaction, and opens a fresh transaction to confirm post-commit traversal.

## State and persistence behavior
The test mutates `./testdb` in the current directory. It uses a 10 MiB map, 1024-byte pages, one max reader, and default synchronous behavior unless code comments are toggled. Random data makes each run nondeterministic.

## Dependencies and integration points
It is a simple executable linked against liblmdb and serves as a smoke test for core B-tree operations.

## Risks and edge cases
The key is declared as `sizeof(int)` bytes but points to a formatted string buffer, so only the first integer-sized bytes of the string key participate. Random stride `rand()%5` can be zero, causing an infinite loop. Fixed-map opening can fail on platforms where the chosen address is unavailable.

## Test signals
The expected signal is successful completion with printed insert/delete/scan output. Sanitizer or repeated stress runs can reveal the zero-stride bug and cursor invalidation issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest2.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest2.c

## Purpose
`mtest2.c` repeats the basic `mtest.c` workflow against a named subdatabase, validating subDB creation and access.

## Important APIs, types, and functions
The macro pattern matches other LMDB tests. `main` uses `mdb_env_set_maxdbs`, opens environment `./testdb`, creates DBI `"id1"` with `MDB_CREATE`, inserts with `MDB_NOOVERWRITE`, reads with a cursor, deletes records with `mdb_del`, and scans forward/backward.

## Control flow
The test generates random values, creates a maxdbs-capable environment, opens subDB `id1` in a write transaction, inserts records, commits, scans in a read-only transaction, deletes random records in separate write transactions, frees input data, and performs final forward and reverse cursor scans before closing.

## State and persistence behavior
It persists data in the `id1` subdatabase inside `./testdb`. The environment uses `MDB_FIXEDMAP|MDB_NOSYNC`, so durability is weaker and address mapping is stricter than default.

## Dependencies and integration points
This executable links directly to LMDB and verifies that named DBs work when `mdb_env_set_maxdbs` is configured before open.

## Risks and edge cases
Like `mtest.c`, delete loop step `rand()%5` can be zero. It also uses `sizeof(int)` key size against a formatted string buffer. `MDB_NOSYNC` can leave a corrupt environment after system crash during testing, and repeated runs reuse an existing `./testdb`.

## Test signals
Successful subdatabase creation, duplicate reporting, cursor traversal, and clean close are the primary signals. Repeating under stress helps expose nondeterministic loop and existing-data interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest3.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest3.c

## Purpose
`mtest3.c` tests sorted duplicate databases using `MDB_DUPSORT`, including duplicate-data insertion, deletion by key/data pair, and cursor traversal.

## Important APIs, types, and functions
It opens subDB `"id2"` with `MDB_CREATE|MDB_DUPSORT`, uses `mdb_put` with `MDB_NODUPDATA`, deletes with `mdb_del(txn, dbi, &key, &data)`, and traverses duplicates with `MDB_NEXT` and `MDB_PREV`.

## Control flow
Random values are generated. Every group of 16 records shares a key derived from the first value in that group, while the data contains each individual value. After insertion and duplicate skip reporting, the test scans all key/data pairs, then deletes selected duplicate values by reconstructing their group key and exact data. It finishes with forward and reverse scans.

## State and persistence behavior
The program mutates `./testdb` subDB `id2` under fixed mapping and nosync mode. Duplicate values are part of the database state and are ordered according to LMDB's duplicate comparator.

## Dependencies and integration points
The test exercises LMDB duplicate-page handling through the public API, especially the distinction between key uniqueness and key/data uniqueness.

## Risks and edge cases
The random delete step can be zero. `kval` has `sizeof(int)` bytes, and formatted keys like `"abc"` include a NUL only if room permits; key-size assumptions are platform-sensitive. Existing data from previous runs can affect duplicate counts.

## Test signals
Signals include `MDB_KEYEXIST` only for true duplicate data, successful deletion of selected key/data pairs, and ordered cursor output in both directions.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest4.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest4.c

## Purpose
`mtest4.c` targets sorted duplicate databases with fixed-size duplicate data, especially duplicate page split paths and `MDB_NEXT_MULTIPLE`.

## Important APIs, types, and functions
The program opens subDB `"id4"` with `MDB_CREATE|MDB_DUPSORT|MDB_DUPFIXED`, inserts fixed-size duplicate values with `MDB_NODUPDATA`, uses aborting transactions to exercise split branches, and reads batches with `MDB_NEXT_MULTIPLE`.

## Control flow
It creates 510 deterministic duplicate values under key `"001"`, which should fill at least one duplicate page. It then tries insertions near the lower half, split point, and upper half of the duplicate set, aborting two and committing one to hit different split code paths. It scans duplicate groups with `MDB_NEXT_MULTIPLE`, deletes a random stride of values, and performs final forward/backward cursor scans.

## State and persistence behavior
The test persists one duplicate-heavy subDB in `./testdb` under `MDB_FIXEDMAP|MDB_NOSYNC`. Aborted insert transactions should leave no state; the committed upper-half insertion should persist.

## Dependencies and integration points
It directly exercises duplicate fixed-size leaf layout, duplicate subpage splitting, and multiple-value cursor retrieval in LMDB internals.

## Risks and edge cases
Deletion stride uses `rand()%3`, which can be zero. Fixed-size buffers and `sizeof(int)` key sizing assume the literal key representation fits. The test is sensitive to page size and duplicate-page thresholds.

## Test signals
Expected output includes successful full duplicate scan, no errors from split-path insertions, `MDB_NEXT_MULTIPLE` returning packed duplicate data, and correct final traversal after deletes.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest5.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest5.c

## Purpose
`mtest5.c` mirrors `mtest3.c` but performs duplicate inserts through `mdb_cursor_put`, validating cursor-based duplicate writes.

## Important APIs, types, and functions
It uses the standard LMDB test macros, opens subDB `"id2"` with `MDB_DUPSORT`, opens a write cursor, inserts via `mdb_cursor_put(..., MDB_NODUPDATA)`, then uses `mdb_del` and cursor scans.

## Control flow
The program creates random values, starts a write transaction, opens the duplicate DBI and cursor, groups records by key every 16 values, inserts duplicate data through the cursor, closes the cursor, and commits. It then scans all records, deletes a random subset by exact key/data pair in separate transactions, and verifies remaining data with forward and reverse scans.

## State and persistence behavior
State is written to `./testdb` subDB `id2` using fixed-map/nosync environment flags. Cursor-put semantics must persist the same logical state as direct `mdb_put` in `mtest3.c`.

## Dependencies and integration points
This is an integration test for cursor insertion paths in duplicate-sorted databases, including duplicate rejection behavior.

## Risks and edge cases
The random delete loop can fail to progress when `rand()%5` is zero. It shares the key-size and existing-environment caveats of `mtest3.c`. Cursor closure before commit is required; missing it would stress cleanup behavior differently.

## Test signals
Important signals are duplicate counts matching direct-put behavior, successful cursor-based insertion, and equivalent traversal/deletion results to `mtest3.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest6.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest6.c

## Purpose
`mtest6.c` is a focused split/merge test for integer-key databases with large values that force B-tree page splits.

## Important APIs, types, and functions
It opens subDB `"id6"` with `MDB_INTEGERKEY`, uses a cursor for `mdb_cursor_put`, formats integer keys with `mdb_dkey` for display, and sizes values from the database page size returned by `mdb_stat`.

## Control flow
The test opens `./testdb`, creates the integer-key DB, allocates a value buffer roughly one quarter of a page, then inserts three waves of 12 records each with interleaved key sequences (`i*5`, `i*5+4`, `i*5+1`). These insertion orders are intended to trigger multiple splits. It scans from first to last and closes. A deletion/merge section remains disabled under `#if 0`.

## State and persistence behavior
It persists subDB `id6` under fixed-map/nosync mode. Large values and integer keys shape page layout and split behavior; the disabled block would have tested merges but is not active.

## Dependencies and integration points
This file depends on LMDB integer-key comparator semantics and internal page-size behavior. It also uses `mdb_dkey`, an LMDB debugging formatter.

## Risks and edge cases
The code does not check `mdb_txn_commit` through `E` at the final commit. `sval` is heap allocated but not freed. The disabled block references variables that are unused in active code, suggesting this is a narrow reproducer rather than a polished test.

## Test signals
Expected signals are successful insertion of all waves, ordered integer-key traversal, and no split-related assertion or corruption. Enabling the disabled block would add merge coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc.c

## Purpose
`mtest_enc.c` adapts the basic main-database test to an encrypted LMDB environment using an in-process ChaCha8 encryption callback.

## Important APIs, types, and functions
`encfunc` calls `chacha8` with source, destination, encryption key material, and IV-like key slots. `main` configures the environment with `mdb_env_set_encrypt`, then follows the same insert, scan, delete, cursor-delete, and cursor-restart pattern as `mtest.c`.

## Control flow
The program generates random values, prepares a fixed 32-byte key, creates an environment, sets max readers and map size, installs encryption before open, inserts random string records with `MDB_NOOVERWRITE`, scans, deletes selected records, scans again, deletes through a cursor, and verifies cursor behavior in and after the write transaction.

## State and persistence behavior
It writes encrypted pages to `./testdb`. The key is static and embedded in the executable. All data persistence depends on the encryption callback producing reversible page transformations compatible with LMDB's page handling.

## Dependencies and integration points
The test includes `chacha8.h` and depends on LMDB's direct encryption callback API. It validates that normal B-tree operations work with encrypted pages.

## Risks and edge cases
The static key is not secure for real use. The delete stride can be zero. Using a custom encryption function without authentication means corruption detection depends on other checks. As with `mtest.c`, string buffer key sizing is unusual.

## Test signals
Successful completion, readable decrypted cursor output, duplicate skips, post-delete scans, and clean close verify encrypted basic operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc2.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc2.c

## Purpose
`mtest_enc2.c` tests encrypted LMDB operation through a dynamically loaded crypto module rather than an in-process encryption callback.

## Important APIs, types, and functions
It calls `mdb_modload("./crypto.lm", NULL, &mcf, &errmsg)`, `mdb_modsetup(env, mcf, password)`, and `mdb_modunload`. The remaining database workflow mirrors `mtest_enc.c`: environment setup, writes with `mdb_put`, cursor scans, deletes, and cursor restart checks.

## Control flow
After generating random values, the program creates an environment, loads `crypto.lm`, applies crypto functions using a passphrase, sets reader/map parameters, opens the DB, inserts records, scans, deletes selected keys, performs cursor deletion and restart checks, then closes DBI/env and unloads the module.

## State and persistence behavior
It writes encrypted data to `./testdb` using the crypto module's checksum/encryption configuration. The passphrase and module behavior define persistent compatibility; future opens must use the same module/key derivation.

## Dependencies and integration points
The file integrates `module.c`'s dynamic-loader API with the standard LMDB C API and requires a built `crypto.lm` in the working directory.

## Risks and edge cases
If `crypto.lm` is missing or exports the wrong hook, the program exits early. The passphrase is hardcoded. Random delete stride can be zero. It does not unload the module on failures after loading unless reaching the normal close path.

## Test signals
This test should be run with a known crypto module, verifying successful module load, encrypted write/read/delete behavior, and clean module unload. Negative tests for missing module and wrong password are also useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc3.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc3.c

## Purpose
`mtest_enc3.c` is an encrypted large-record reproducer for ITS#9920, stressing key/value sizes, encrypted page checksums, and high record counts.

## Important APIs, types, and functions
It defines `KEY_SIZE` as 24 and `MAX_VALUE_SIZE` as 150, uses deterministic `srand(42)`, installs ChaCha8 encryption with `mdb_env_set_encrypt(..., 16)`, writes 64,000 random key/value pairs, prints environment and DB stats, and performs cursor traversals and cursor-delete checks.

## Control flow
The test allocates arrays for key lengths, value lengths, keys, and values; fills them with random uppercase data; opens a 1 GiB encrypted environment; writes every generated record in one transaction with `MDB_NOOVERWRITE`; scans all records; attempts deletions; prints stats; scans forward/backward; deletes with a cursor; then verifies cursor restart behavior.

## State and persistence behavior
The program writes a large encrypted `./testdb`. The encryption checksum size parameter is specifically set to 16, with comments noting the reproduced bug occurs above lower thresholds. It uses deterministic input generation for reproducibility.

## Dependencies and integration points
It depends on `chacha8.h`, LMDB encryption APIs, and B-tree paths handling larger encrypted nodes and checksums.

## Risks and edge cases
After the initial scan, deletion sets `key.mv_data = sval` without reconstructing generated keys, so many deletes are expected to miss and do not strongly validate deletion. It can produce very large console output and requires enough disk/map space. Memory allocation failures are not checked.

## Test signals
Primary signals are no crash or corruption during 64k encrypted inserts, successful full traversal, sensible `mdb_stat` entry/depth output, and reproduction stability for ITS#9920 parameters.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc4.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc4.c

## Purpose
`mtest_enc4.c` creates an encrypted database with varied large value sizes to exercise encrypted overflow-page handling, especially for ITS#10520 and follow-up dump/load/copy validation.

## Important APIs, types, and functions
It uses `mdb_modload`, `mdb_modsetup`, and `mdb_modunload` with `crypto.lm`, sets a 1 GiB map, writes 2,400 records with up to 64 KiB values, commits every 100 records, and uses `MDB_NOOVERWRITE`.

## Control flow
The program loads the crypto module with a hardcoded passphrase, opens `./testdb`, starts a write transaction, repeatedly generates an 8-byte random hex key and random value size, points data at a shared `valbuf`, writes the record, and commits/restarts the transaction every 100 iterations. It prints duplicate counts, commits the final batch, gathers environment stats, then closes and unloads the module.

## State and persistence behavior
The output is an encrypted database containing values large enough to occupy overflow pages. Batching commits means partial progress persists if a later batch fails. The comment directs operators to run dump/load/copy tools afterward to verify encrypted overflow correctness.

## Dependencies and integration points
This file integrates module-based crypto with LMDB overflow-page allocation and with the utility suite (`mdb_dump`, `mdb_load`, `mdb_copy`) as downstream validation.

## Risks and edge cases
`data.mv_size` may be zero because `rand() % MAX_VALUE_SIZE` includes zero. Only the start of `valbuf` is formatted; the rest may contain previous data or zeros. Error paths after module load may skip unload. Random keys can collide.

## Test signals
Successful creation plus successful encrypted dump/load/copy round trips are the main signals. Additional validation should compare record counts and large-value contents after copy/load.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_enc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_remap.c -->
# sources/storage-engines/lmdb/libraries/liblmdb/mtest_remap.c

## Purpose
`mtest_remap.c` repeats the basic main-database tester while opening the environment with `MDB_REMAP_CHUNKS`, exercising LMDB's chunk remapping mode.

## Important APIs, types, and functions
It uses the standard test macros, opens `./testdb` with `MDB_REMAP_CHUNKS`, then uses core APIs including `mdb_put`, `mdb_del`, `mdb_cursor_get`, cursor deletion, and transaction commit/abort.

## Control flow
The workflow matches `mtest.c`: generate random records, configure max readers and map size, open the remapped environment, insert records, scan, delete random records, scan forward/backward, delete initial records through a cursor, restart cursor traversal inside the write transaction, commit, and verify traversal in a new transaction.

## State and persistence behavior
The test persists data in `./testdb` using remapped chunks rather than a single traditional mapping mode. This changes how pages are mapped in memory while preserving LMDB's logical database semantics.

## Dependencies and integration points
It includes `chacha8.h` but does not use encryption; the meaningful integration point is the `MDB_REMAP_CHUNKS` environment flag in liblmdb.

## Risks and edge cases
The same random zero-stride delete risk from `mtest.c` applies. Including an unused crypto header can create unnecessary build dependency. Remap behavior is platform-sensitive and may expose mapping or pointer-lifetime assumptions in cursor code.

## Test signals
Successful completion under remap mode, stable cursor traversal across deletes and transaction boundaries, and comparison with the baseline `mtest.c` behavior are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/lmdb/libraries/liblmdb/mtest_remap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/actions/post-issue/action.yaml -->
# sources/storage-engines/pebble/.github/actions/post-issue/action.yaml

## Purpose
This composite GitHub Action creates a new issue or comments on an existing issue with a matching title, giving nightly workflows a reusable failure-reporting primitive.

## Important APIs, types, and functions
Inputs include `token`, `title`, `body`, optional `unique-title-includes`, and optional `labels`. It uses `actions-cool/issues-helper@v3` for issue search, creation, and comments. A bash step with `jq` extracts the first matching issue number. The action exposes output `issue-number`.

## Control flow
The action searches for issues whose title includes the unique string or title. If a number is found, it records that number in `GITHUB_OUTPUT`; otherwise it creates a new issue. A conditional comment step runs for existing issues. The final step normalizes either found or created issue number into the action output.

## State and persistence behavior
The action mutates GitHub issue state by creating issues or comments. It stores only transient step outputs inside the workflow run.

## Dependencies and integration points
Nightly Pebble workflows call this action on failure. It depends on GitHub token permissions, `jq` availability on the runner, and the third-party `actions-cool/issues-helper` action.

## Risks and edge cases
The title matching is broad and may comment on an unrelated issue if titles overlap. Pulling issue JSON into a heredoc from an action output must remain valid shell/JQ input. Third-party action behavior and permissions are supply-chain and reliability dependencies.

## Test signals
Validation should cover no existing issue, one matching issue, multiple matches, custom unique-title strings, label assignment, and token permission failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/actions/post-issue/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/ci.yaml -->
# sources/storage-engines/pebble/.github/workflows/ci.yaml

## Purpose
`ci.yaml` defines Pebble's pull-request and protected-branch test workflow, including required Linux tests, lint checks, no-cgo/no-invariants variants, race tests, macOS tests, and stress of newly added tests on PRs.

## Important APIs, types, and functions
The workflow triggers on pushes and pull requests to `master`, `crl-release-*`, and `pebble-release-*`. Jobs use `actions/checkout`, `actions/setup-go`, `make` targets such as `test`, `testobjiotracing`, `generate`, `mod-tidy-check`, `format-check`, `testnocgo`, and `testrace`, plus `scripts/stress-new-tests.sh`.

## Control flow
Each job checks out the repository, installs Go 1.26, and runs its target. The main Linux job also asserts a clean workspace after generation. The PR-only stress job fetches full history, installs `cockroachdb/stress`, sets `BASE_BRANCH`, and runs a script to stress tests added by the PR.

## State and persistence behavior
The workflow does not persist repository state, but generation and formatting checks intentionally fail if source changes are produced. It consumes GitHub runner state and may populate Go module/build caches implicitly.

## Dependencies and integration points
It is the primary integration point between repository code and GitHub branch protection. It relies on Makefile targets, Go 1.26, shell scripts, and GitHub-hosted Linux/macOS runners.

## Risks and edge cases
Required jobs must retain stable names. `make generate` can be expensive and must keep the workspace clean. PR stress uses `fetch-depth: 0` and `gh`, which depend on GitHub token behavior. Go version drift must stay aligned with the repo.

## Test signals
Passing required jobs, clean workspace checks, race/no-cgo/no-invariants variants, macOS coverage, and stress-new-tests output are the central CI signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/ci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/cockroach-go.yaml -->
# sources/storage-engines/pebble/.github/workflows/cockroach-go.yaml

## Purpose
This reusable/manual workflow runs Pebble tests with a CockroachDB-maintained Go fork branch, mainly for nightly compatibility with custom Go toolchains.

## Important APIs, types, and functions
Inputs include `sha`, `file_issue_branch`, `bootstrap_go_version`, and required `go_branch`. It uses `git ls-remote` to resolve the fork branch SHA, `actions/cache` for toolchain caching under `~/.cache/cockroachdb-go/<sha>`, `actions/setup-go` for bootstrap Go, `scripts/run-tests-with-custom-go.sh`, and the local `post-issue` action.

## Control flow
The workflow checks out the requested repository SHA, resolves the custom Go branch tip, restores a cache keyed by that SHA, installs bootstrap Go, and runs all tests with invariants tags through the custom toolchain script. On failure and when `file_issue_branch` is provided, it creates or updates a nightly failure issue.

## State and persistence behavior
Persistent external state is the GitHub Actions cache for the custom toolchain and any GitHub issue/comment created on failure. Repository state is read-only within the run.

## Dependencies and integration points
It integrates master nightlies with `nightlies.yaml`, the CockroachDB Go fork repository, Make/script-based test execution, and issue reporting.

## Risks and edge cases
`git ls-remote` can fail or return an empty SHA for invalid branches. Cache poisoning or stale custom toolchains could affect results if the script does not validate contents. Failure filing depends on issue write permissions inherited from the caller.

## Test signals
Signals include successful custom toolchain resolution, cache hit/miss behavior, test completion under `-tags invariants`, and issue creation on forced failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/cockroach-go.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/code-cover-gen.yaml -->
# sources/storage-engines/pebble/.github/workflows/code-cover-gen.yaml

## Purpose
`code-cover-gen.yaml` generates before/after PR coverage artifacts for changed Go packages without requiring repository secrets on untrusted pull-request code.

## Important APIs, types, and functions
It triggers on pull-request open/reopen/synchronize against `master`, checks out the PR head SHA with full history, sets up Go 1.26, uses `gh pr view`, `git rev-parse`, `scripts/changed-go-pkgs.sh`, `scripts/pr-codecov-run-tests.sh`, and uploads `cover-*.json` artifacts.

## Control flow
The workflow computes the PR commit count, derives the base SHA as `HEAD~NUM_COMMITS`, computes changed packages, stores base and package list in `GITHUB_ENV`, copies the coverage script to runner temp, generates "after" coverage at the PR head, checks out the base SHA, generates "before" coverage with the same script copy, and uploads both JSON files as an artifact named `cover`.

## State and persistence behavior
It writes transient artifact files under `artifacts/` and uploads them to GitHub Actions storage. It intentionally does not use secrets.

## Dependencies and integration points
The publish workflow consumes the uploaded artifact. The logic depends on GitHub CLI authentication via `GH_TOKEN`, full git history, and repository coverage scripts.

## Risks and edge cases
Deriving base SHA from commit count can be wrong for complex PR histories. The changed package list is passed through environment variables and shell quoting; packages with unusual whitespace would be risky. Checking out the base after running untrusted PR code is acceptable because the artifact-generation job has no secrets.

## Test signals
Expected signals are two JSON coverage files named with PR/head/base identifiers, correct changed package selection, and successful artifact upload for representative PR shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/code-cover-gen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/code-cover-publish.yaml -->
# sources/storage-engines/pebble/.github/workflows/code-cover-publish.yaml

## Purpose
`code-cover-publish.yaml` publishes PR coverage artifacts from the untrusted generation workflow to a public GCS bucket using repository secrets in a separate trusted workflow.

## Important APIs, types, and functions
It triggers on completed `workflow_run` events for `PR code coverage (generate)`. The job uses `actions/download-artifact`, `google-github-actions/auth`, and `google-github-actions/upload-cloud-storage`.

## Control flow
The job runs only when the source workflow was a pull request and concluded successfully. It downloads the `cover` artifact from the triggering run using the run ID, authenticates to Google Cloud with `CODECOVER_SERVICE_ACCOUNT_KEY`, and uploads `cover-*.json` files to `crl-codecover-public/pr-pebble/`.

## State and persistence behavior
The workflow writes coverage JSON objects into GCS. It does not mutate repository state.

## Dependencies and integration points
It is paired with `code-cover-gen.yaml`, uses GitHub artifact storage as the handoff boundary, and integrates with Reviewable or other consumers reading the public bucket.

## Risks and edge cases
Secrets are exposed only to this trusted workflow, but artifact content originated from untrusted PR code. The upload action must treat files as inert data. Missing artifacts or expired runs cause publish failures.

## Test signals
Signals include correct filtering of workflow_run events, successful artifact download by run ID, GCP authentication, and expected objects in the destination bucket.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/code-cover-publish.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/crossversion.yaml -->
# sources/storage-engines/pebble/.github/workflows/crossversion.yaml

## Purpose
`crossversion.yaml` is a reusable/manual workflow for running Pebble's cross-version smoke test against a chosen SHA and Go version.

## Important APIs, types, and functions
Inputs are `sha`, `file_issue_branch`, and `go_version`. Steps use `actions/checkout` with full history, `git fetch --all`, `actions/setup-go`, `scripts/crossversion_smoke_test.sh`, and the local `post-issue` action.

## Control flow
The workflow checks out the requested SHA, fetches all branches so release references are available, installs the requested Go version, and runs the cross-version smoke script. On failure, reusable nightly callers can file an issue labeled `C-test-failure`.

## State and persistence behavior
No repository state is persisted. Failure issue creation persists in GitHub if enabled by input.

## Dependencies and integration points
This job is called by master nightlies and may be run manually. It depends on release branches being available and on the cross-version script's internal expectations.

## Risks and edge cases
Full branch fetching can be slow or flaky. The smoke script likely depends on branch naming conventions. Missing `file_issue_branch` disables failure reporting, which is useful manually but can hide nightly failures if miswired.

## Test signals
Successful script completion across relevant release branches and correct failure issue creation are the core signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/crossversion.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/instrumented.yaml -->
# sources/storage-engines/pebble/.github/workflows/instrumented.yaml

## Purpose
`instrumented.yaml` defines reusable/manual nightly jobs for high-cost instrumented test variants: race, ASAN, and MSAN.

## Important APIs, types, and functions
Inputs include `sha`, `file_issue_branch`, and `go_version`. Jobs run `make testrace TAGS=`, `make testasan`, and `make testmsan`, with Go installed through `actions/setup-go`. ASAN uses Ubuntu 22.04 due to a noted Ubuntu 24.04/kernel issue. Failures call `post-issue`.

## Control flow
Each job independently checks out the requested SHA, installs Go, runs the relevant Make target, and conditionally files an issue on failure. Race runs on latest Ubuntu, ASAN is pinned to Ubuntu 22.04, and MSAN uses latest Ubuntu with Makefile-provided Clang configuration.

## State and persistence behavior
The workflow is read-only except for potential GitHub issue creation. Test binaries and sanitizer artifacts are transient runner state.

## Dependencies and integration points
Master and release nightlies call this workflow. It depends on Makefile sanitizer targets, Go compiler support for `-race`, `-asan`, and `-msan`, and runner toolchain availability.

## Risks and edge cases
Sanitizer support is sensitive to OS image changes. Race and sanitizer jobs are expensive and can time out if Makefile timeouts drift. `TAGS=` disables invariants for race, so it tests a different code shape than default invariant builds.

## Test signals
Passing race, ASAN, and MSAN jobs provide concurrency and memory-safety signals beyond normal unit tests. Failure issue content should identify branch, job, SHA, and Go version.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/instrumented.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-25.2.yaml -->
# sources/storage-engines/pebble/.github/workflows/nightlies-25.2.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-25.2`.

## Important APIs, types, and functions
It runs on a daily cron at 10:30 UTC and manual dispatch. A `resolve-sha` job checks out history and records `branch` and `sha` outputs. Downstream jobs call reusable `tests.yaml`, `s390x.yaml`, `stress.yaml`, and `instrumented.yaml` with Go 1.23.

## Control flow
The resolver fetches the repository, runs `git rev-parse origin/$BRANCH`, and exposes both branch and SHA. The reusable test jobs then run against that exact SHA and use the branch name for issue filing.

## State and persistence behavior
Workflow state is limited to job outputs and any failure issues/comments created by downstream reusable workflows.

## Dependencies and integration points
It integrates release branch maintenance with the shared nightly test suite and assumes `origin/crl-release-25.2` exists.

## Risks and edge cases
If the branch is removed or renamed, SHA resolution fails and no downstream tests run. Go 1.23 must remain available on setup-go. All child workflows must accept the same input contract.

## Test signals
The signal is a daily pass/fail matrix for normal, s390x, stress, and instrumented coverage on the release branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-25.2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-25.4.yaml -->
# sources/storage-engines/pebble/.github/workflows/nightlies-25.4.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-25.4`.

## Important APIs, types, and functions
It uses the same resolver pattern as other release nightlies: scheduled/manual triggers, `BRANCH=crl-release-25.4`, `git rev-parse origin/$BRANCH`, and calls to `tests.yaml`, `s390x.yaml`, `stress.yaml`, and `instrumented.yaml` with Go 1.23.

## Control flow
The `resolve-sha` job produces stable branch and SHA outputs. Four reusable workflows consume the SHA and branch name, ensuring all jobs test the same release commit and file issues under the release branch label.

## State and persistence behavior
No repository state is changed. Persistent state can be created only through downstream failure issue reporting.

## Dependencies and integration points
It depends on the shared reusable workflow interface and the existence of `origin/crl-release-25.4`.

## Risks and edge cases
The cron string has a trailing space but is otherwise valid YAML text for GitHub scheduling. Go 1.23 availability and reusable workflow compatibility are required for continued release validation.

## Test signals
Nightly pass/fail across standard tests, s390x, stress, and instrumented variants is the expected release health signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-25.4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-26.1.yaml -->
# sources/storage-engines/pebble/.github/workflows/nightlies-26.1.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-26.1`.

## Important APIs, types, and functions
It defines `BRANCH=crl-release-26.1`, resolves `origin/$BRANCH`, and invokes reusable `tests`, `s390x`, `stress`, and `instrumented` workflows with Go 1.25.

## Control flow
On schedule or manual dispatch, the resolver job checks out full history and emits branch/SHA outputs. The four downstream jobs all depend on this resolver and run against the same resolved commit.

## State and persistence behavior
Only workflow outputs and optional failure issues persist. The code checkout itself is not modified by this orchestration file.

## Dependencies and integration points
It integrates the 26.1 release line with the shared nightly workflow suite. It assumes reusable workflows continue to support Go-version and failure-issue inputs.

## Risks and edge cases
Branch resolution is a single point of failure. A mismatch between release branch Go requirements and hardcoded Go 1.25 would cause noisy failures or missed coverage.

## Test signals
Daily success across standard, architecture, stress, and sanitizer/race jobs is the release health signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-26.1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-26.2.yaml -->
# sources/storage-engines/pebble/.github/workflows/nightlies-26.2.yaml

## Purpose
This workflow schedules daily nightly testing for branch `crl-release-26.2`.

## Important APIs, types, and functions
It uses the shared release-nightly pattern with `BRANCH=crl-release-26.2`, a `resolve-sha` job, and calls to `tests.yaml`, `s390x.yaml`, `stress.yaml`, and `instrumented.yaml` using Go 1.25.

## Control flow
The resolver checks out full history and records the branch name plus `git rev-parse origin/$BRANCH`. All child workflows depend on that output and include `file_issue_branch` so failure issues identify the release line.

## State and persistence behavior
The workflow is read-only apart from downstream issue/comment creation on test failure.

## Dependencies and integration points
It connects the latest listed release branch to the repository's reusable nightly test suite and GitHub issue reporting action.

## Risks and edge cases
Hardcoded branch and Go version must track release policy. If reusable workflow names or inputs change, this orchestration file breaks all branch coverage.

## Test signals
The expected signal is consistent daily coverage across normal tests, s390x emulation, stress, race, ASAN, and MSAN for the resolved release SHA.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies-26.2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies.yaml -->
# sources/storage-engines/pebble/.github/workflows/nightlies.yaml

## Purpose
`nightlies.yaml` orchestrates manual master-branch nightly coverage by calling reusable workflows for tests, architecture coverage, stress, instrumented variants, custom Cockroach Go, crossversion, and an `iterv2` tag variant.

## Important APIs, types, and functions
Jobs call `tests.yaml`, `s390x.yaml`, `stress.yaml`, `instrumented.yaml`, `cockroach-go.yaml`, and `crossversion.yaml`, each with a one-element Go 1.26 matrix. The local `linux-iterv2` job runs `make test TAGS="invariants iterv2"`, checks workspace cleanliness, and files an issue on failure.

## Control flow
Manual dispatch runs all jobs independently with `fail-fast: false` where matrices are used. Reusable jobs receive `sha: github.sha` and `file_issue_branch: master`. The Cockroach Go job pins `go_branch: cockroach-go1.26.2`. The `linux-iterv2` job checks out the repository, installs Go, runs tagged tests, asserts clean workspace, and posts issues on failure.

## State and persistence behavior
Persistent state is limited to failure issues/comments. Test outputs are transient runner state.

## Dependencies and integration points
This is the top-level master nightly orchestrator and depends on all reusable workflow files, Makefile targets, the local post-issue action, and the Cockroach Go fork branch.

## Risks and edge cases
It is manual-only, so scheduled master nightly coverage must be triggered elsewhere or by humans. Hardcoded custom Go branch and Go matrix need updates with compiler upgrades. `iterv2` coverage is local to this workflow and not shared with release nightlies.

## Test signals
The workflow aggregates the broadest master health signal: platform tests, stress, sanitizer/race, custom Go, crossversion, and iterator-v2 tagged tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightlies.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightly-code-cover.yaml -->
# sources/storage-engines/pebble/.github/workflows/nightly-code-cover.yaml

## Purpose
`nightly-code-cover.yaml` manually generates and publishes full repository code coverage to Google Cloud Storage.

## Important APIs, types, and functions
It uses `actions/checkout`, `actions/setup-go`, `scripts/code-coverage.sh`, installs `lcov` through apt, authenticates with `CODECOVER_SERVICE_ACCOUNT_KEY`, sets up `gcloud`, and runs `scripts/code-coverage-publish.sh`.

## Control flow
On manual dispatch, the workflow checks out with full history, installs Go 1.26, generates coverage, installs lcov, authenticates to GCP, sets up the Cloud SDK, and publishes coverage.

## State and persistence behavior
Coverage reports are generated locally and then persisted to a GCS destination selected by the publish script. Repository state is not intentionally changed.

## Dependencies and integration points
It integrates repository coverage scripts with GCS and likely external coverage viewers. It depends on apt, lcov, GCP credentials, and Cloud SDK availability.

## Risks and edge cases
The checkout references `github.event.pull_request.head.sha`, which is not defined for `workflow_dispatch`; this may resolve empty or fail depending on GitHub expression handling. Manual full-coverage runs require secrets and can fail if GCP actions versions or credentials change.

## Test signals
Signals include successful coverage script output, lcov installation, GCP auth, and publish script completion with expected remote coverage artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/nightly-code-cover.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/pr-analyzer-threestage.yml -->
# sources/storage-engines/pebble/.github/workflows/pr-analyzer-threestage.yml

## Purpose
This workflow runs a staged Claude Code review on pull requests, escalating from initial bug screening to database-expert review to principal-engineer review before commenting on the PR.

## Important APIs, types, and functions
It triggers on `pull_request_target` synchronize/ready/reopened events unless label `O-No-AI-Review` is present. It uses `actions/checkout@v5`, Google workload identity authentication, `cockroachdb/claude-code-action@v1`, `jq` extraction from execution files, `gh pr comment`, and PR label editing.

## Control flow
The job checks out the PR head SHA, authenticates to Vertex-backed Claude, and runs Stage 1. If Stage 1 output contains potential bug text, Stage 2 runs; if Stage 2 confirms, Stage 3 runs. Each result is extracted from the action execution file into step outputs. A final analysis report always runs. If Stage 3 confirms a potential bug, the workflow posts a PR comment with review instructions and adds a label.

## State and persistence behavior
The workflow can write PR comments and labels. It reads PR code under `pull_request_target`, but tool permissions are restricted mostly to read/diff commands and PR metadata.

## Dependencies and integration points
It integrates GitHub PR events, Google Cloud workload identity, Anthropic Vertex model routing, and CockroachDB's Claude action. The workflow depends on exact marker strings in model outputs for control flow.

## Risks and edge cases
`pull_request_target` with PR head checkout is sensitive; allowed tools must remain restricted because untrusted code is present. String matching on model output is brittle. The prompt contains unusually forceful language that may bias output. Model/version or action changes can break JSON extraction or result formats.

## Test signals
Dry runs should validate skipped behavior with `O-No-AI-Review`, Stage 1 no-bug path, staged escalation path, result extraction from execution files, final report generation, PR comment creation, and label application.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/pr-analyzer-threestage.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/s390x.yaml -->
# sources/storage-engines/pebble/.github/workflows/s390x.yaml

## Purpose
`s390x.yaml` runs Pebble's test suite under s390x emulation to cover big-endian and architecture-specific behavior.

## Important APIs, types, and functions
The reusable/manual workflow accepts `sha`, `file_issue_branch`, and `go_version`. It installs `qemu-user-static`, runs `make test-s390x-qemu S390X_GOVERSION=<go_version>`, and uses the `post-issue` action on failure.

## Control flow
The job checks out the requested SHA, installs QEMU, prints the QEMU version, then invokes the Makefile target that runs a Docker `golang:<version>` container under `--platform=linux/s390x` and executes Go tests.

## State and persistence behavior
No repository state is persisted. Docker images and QEMU setup are transient runner state. Failure issues/comments may persist if configured.

## Dependencies and integration points
It depends on Docker, QEMU user-static support, the Makefile `test-s390x-qemu` target, and GitHub runner privileges for container execution.

## Risks and edge cases
QEMU and Docker image availability can cause infrastructure flakes. The Makefile default includes `slowbuild` tags and a long timeout; changes to Go architecture support can surface here first. Issue permissions are declared as `issues: write`.

## Test signals
Successful emulated `go test` on s390x, including endian-sensitive logic, is the main signal. Failure reporting should include branch, SHA, and Go version.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/s390x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/stale.yml -->
# sources/storage-engines/pebble/.github/workflows/stale.yml

## Purpose
`stale.yml` automatically marks inactive issues stale and eventually closes them, while effectively disabling stale handling for pull requests.

## Important APIs, types, and functions
It runs `actions/stale@v3` on a Monday-Thursday schedule and manual dispatch. Configuration sets operation limits, messages, labels, close labels, `days-before-issue-stale: 540`, `days-before-close: 10`, `days-before-pr-stale: 99999`, and exempt issue label `X-nostale`.

## Control flow
The single job grants issue and pull-request write permissions, then runs the stale action with repo token and policy settings. Inactive issues receive `no-issue-activity`, then `X-stale` on close after the grace period. PR stale timing is set high enough to avoid normal PR stale closure.

## State and persistence behavior
It mutates GitHub issue/PR labels and may close issues. It does not touch repository files.

## Dependencies and integration points
The workflow integrates repository triage policy with GitHub Issues and depends on the third-party stale action.

## Risks and edge cases
Older `actions/stale@v3` behavior may diverge from current GitHub APIs. Broad operation limits can label many issues in one run. Incorrect exempt labels or messages can close still-relevant issues.

## Test signals
Manual dry runs on a test repository or limited labels should confirm stale labeling, exemption behavior, and close timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/stress.yaml -->
# sources/storage-engines/pebble/.github/workflows/stress.yaml

## Purpose
`stress.yaml` runs Pebble unit tests under CockroachDB's `stress` tool for nightly flake discovery.

## Important APIs, types, and functions
Inputs are `sha`, `file_issue_branch`, and `go_version`. Steps use `actions/checkout`, `actions/setup-go`, `go install github.com/cockroachdb/stress@latest`, `scripts/stress.sh`, and the local `post-issue` action.

## Control flow
The workflow checks out the requested SHA, installs Go, installs the stress binary into the Go toolchain path, runs the repository stress script, and conditionally files a failure issue.

## State and persistence behavior
The workflow mutates only transient runner tool state by installing `stress`. Failure issue creation is persistent when enabled.

## Dependencies and integration points
Release and master nightlies call this reusable workflow. It depends on the external stress module, the repository's stress script, and Go version compatibility.

## Risks and edge cases
Installing `stress@latest` can introduce nondeterminism if the tool changes. Stress runs are time/resource intensive and can produce flaky failures that need triage. Missing issue permissions from callers can make failure reporting fail.

## Test signals
Signals include repeated test pass under stress, clear failure logs for flakes, and issue creation with branch/SHA/Go context.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/stress.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/tests.yaml -->
# sources/storage-engines/pebble/.github/workflows/tests.yaml

## Purpose
`tests.yaml` is the reusable/manual broad test workflow for Pebble, covering normal Linux, 32-bit, ARM, crossversion metadata, no-invariants, no-cgo, macOS, Windows, lint checks, and cross-architecture builds.

## Important APIs, types, and functions
Inputs are `sha`, `file_issue_branch`, and `go_version`. Jobs use `actions/checkout`, `actions/setup-go`, Makefile targets (`test`, `testobjiotracing`, `generate`, `crossversion-meta`, `testnocgo`, `mod-tidy-check`, `format-check`), direct `go test`, direct `go build`, and `post-issue`.

## Control flow
Each job checks out the requested SHA and installs the requested Go version. Linux runs main tests plus generation and workspace-clean assertion. Other jobs run architecture/build-mode variants: GOARCH=386, ARM runner tests, crossversion meta, no-invariants tags, no CGO, macOS, Windows, lint checks, and builds for mips/mipsle/mips64le/freebsd/netbsd/openbsd. Most jobs file branch-specific issues on failure.

## State and persistence behavior
The workflow is intended to be read-only; generation, formatting, and mod-tidy jobs fail if they produce diffs. Failure issues/comments may persist.

## Dependencies and integration points
It is called by release and master nightlies and can be manually dispatched. It depends on the Makefile, test scripts, generated-code checks, Git history for crossversion metadata, and platform runners.

## Risks and edge cases
Runner availability for `ubuntu-22.04-arm`, macOS, and Windows can be a source of infrastructure failure. `crossversion-meta` checks out release branches inside the job, so it must restore state correctly. Direct `go build` targets do not run tests but catch portability issues.

## Test signals
This workflow provides the main multi-platform signal. Clean workspace after generation, lint pass, no-cgo and no-invariants variants, and cross-OS/arch builds all indicate repository health beyond the default Linux test.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/.github/workflows/tests.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/Makefile -->
# sources/storage-engines/pebble/Makefile

## Purpose
The Pebble Makefile centralizes common developer and CI commands for tests, coverage, stress, crossversion testing, s390x emulation, Bazel metadata generation, generated test data, docs serving, module updates, cleaning, and formatting.

## Important APIs, types, and functions
Top-level variables include `GO`, `PKG`, `GOFLAGS`, `STRESSFLAGS`, `TAGS`, `TESTS`, and `COVER_PROFILE`. Key targets include `test`, `testcoverage`, `testrace`, `testasan`, `testmsan`, `testnocgo`, `testobjiotracing`, `lint`, `stress`, `stressrace`, `stressmeta`, `crossversion-meta`, `stress-crossversion`, `test-s390x-qemu`, `gen-bazel`, `clean-bazel`, `generate`, `generate-test-data`, `testdocs`, `mod-update`, `clean`, `git-clean-check`, `mod-tidy-check`, `format`, and `format-check`.

## Control flow
Most targets layer extra `testflags`, tags, or variable overrides before delegating to `go test`. Stress targets use `-exec stress`. Crossversion metadata fetches release branches, checks out the latest release, compiles old and head metamorphic binaries, and runs `TestMetaCrossVersion`. s390x invokes Docker under QEMU. Formatting installs `crlfmt` and checks for a clean git diff.

## State and persistence behavior
Targets can create coverage profiles, test binaries, WORKSPACE/BUILD files, generated test fixtures, modified Go module files, formatting changes, and Docker/Go caches. CI check targets intentionally require a clean git tree before running and fail if changes appear.

## Dependencies and integration points
GitHub workflows call many of these targets. The file integrates Go tooling, CockroachDB stress, Bazel Gazelle, Docker/QEMU for s390x, Python docs serving, `go generate`, and internal repository scripts/tools.

## Risks and edge cases
There are two `generate` target declarations; make merges rules but this is easy to misread. `git_dirty` is evaluated at parse time, so cleanliness checks reflect state when Make starts. `crossversion-meta` performs git checkouts inside the working tree and can disrupt local state if interrupted. `clean` removes test binaries by package basename only.

## Test signals
CI relies on this Makefile for the canonical pass/fail signals. Local validation usually starts with `make test`, then adds `make testrace`, `make mod-tidy-check`, `make format-check`, and specialized targets for touched areas.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/Makefile -->
