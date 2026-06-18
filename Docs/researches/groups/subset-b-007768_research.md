# subset-b-007768 Research

Grouped research for OpenAFS backup database server headers and implementation files under `src/budb`. Each section preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_client.h -->
# sources/distributed-fs/openafs/src/budb/budb_client.h

## Purpose
Defines the client-side handles used by OpenAFS backup database consumers. The file is small, but it is the public shape for connecting to the Ubik replicated budb service and for caching typed text payloads.

## Important APIs, Types, And Functions
`udbHandleS` stores the RX security index/object, per-server `rx_connection` array, `ubik_client` handle, and client `instanceId`. `udbClientTextS` names a text object, carries its `textType`, cached `textVersion`, held `lockHandle`, byte size, and optional `FILE *` stream. `UF_SINGLESERVER` and `UF_END_SINGLESERVER` flag single-server Ubik calls.

## Control Flow
The header has no executable flow. Client code initializes a `udbHandleT`, establishes server connections, obtains a lock/instance via RPCs, then uses `udbClientTextT` metadata to fetch, cache, or replace server-side text blocks.

## State And Persistence
All state is client memory, except the fields mirror persistent server state: text versions/locks and Ubik server connections. A stale `lockHandle` or `textVersion` directly affects atomic text updates.

## Dependencies And Integration Points
It depends on `ubik.h`, RX/XDR, `afs/budb.h`, and `budb_errs.h`. It is consumed by backup clients and admin tools that talk to the budb RPC interface.

## Risks And Test Signals
Risks are ABI drift against generated RPC structures and misuse of stale lock handles. Signals are successful authenticated/noauth client connection setup, text version checks, lock acquisition/release, and single-server operation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_client.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_internal.h -->
# sources/distributed-fs/openafs/src/budb/budb_internal.h

## Purpose
Centralizes internal budb server prototypes across allocation, hash, dump, lock, verification, RPC, logging, and structure conversion modules. It is the glue header for the C files in this group.

## Important APIs, Types, And Functions
It declares database allocation (`InitDBalloc`, `AllocStructure`, `FreeStructure`, `AllocBlock`, `FreeBlock`), hash operations (`InitDBhash`, `ht_DBInit`, `ht_HashIn`, `ht_HashOut`, `ht_LookupEntry`, `scanHashTable`, `RemoveFromList`), dump streaming (`writeDatabase`), lock validation (`checkLockHandle`), address validation (`checkDiskAddress`), RPC initialization (`InitProcs`, `callPermitted`, `InitRPC`), and server logging. It also exposes conversion/printing helpers from `struct_ops.c`.

## Control Flow
The declarations reveal the layering: every RPC starts through `InitRPC`, primitive reads/writes live in `database.c`, fixed-size block allocation is in `db_alloc.c`, lookup/indexing goes through `db_hash.c`, and high-level RPCs in `procs.c` compose those pieces.

## State And Persistence
The prototypes operate on the global in-memory `db` cache and persistent Ubik database blocks. Helpers use network-byte-order structures on disk and convert at RPC boundaries.

## Dependencies And Integration Points
The header depends on `database.h` types, generated budb RPC types, Ubik transactions, RX calls, and shared struct conversion helpers. It is included by most budb server modules.

## Risks And Test Signals
Prototype drift can silently corrupt cross-module calls in C. Useful signals are a full budb build with warnings enabled, RPC smoke tests, database create/delete cycles, dump/restore, and online verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_internal.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_prototypes.h -->
# sources/distributed-fs/openafs/src/budb/budb_prototypes.h

## Purpose
Provides a narrower set of budb helper prototypes, mostly for structure conversion, default tape-set generation, and debug printing.

## Important APIs, Types, And Functions
The file declares `structDumpHeader_ntoh`, `DbHeader_ntoh`, `dumpEntry_ntoh`, `tapeEntry_ntoh`, `volumeEntry_ntoh`, `default_tapeset`, and print helpers for dump, tape, and volume RPC entries.

## Control Flow
There is no executable control flow. Consumers include this header when translating RPC/database dump structures from network to host order or when formatting entries for user-visible diagnostics.

## State And Persistence
No state is defined here. The declared conversion functions are persistence-relevant because saved database streams and RPC structs use fixed network-order layouts.

## Dependencies And Integration Points
It integrates with generated `budb.h` structures and `struct_ops.c`. It complements `budb_internal.h`, but only exposes a small public-ish utility surface.

## Risks And Test Signals
Risk is declaration drift against `struct_ops.c` or generated RPC types. Test signals include dump stream decode/encode tests, admin command output for dump/tape/volume entries, and cross-endian structure conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_prototypes.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.c -->
# sources/distributed-fs/openafs/src/budb/database.c

## Purpose
Owns the global in-memory backup database cache and the low-level Ubik read/write wrappers. It initializes allocation/hash subsystems, performs bounds-checked database I/O, and rebuilds or refreshes the cached header through Ubik cache callbacks.

## Important APIs, Types, And Functions
`db_panic` logs and exits via audited `BUDB_EXIT`. `InitDB` clears global `db`, resets `pollCount`, and initializes allocation/hash metadata. `dbwrite`, `dbread`, and `cdbread` wrap `ubik_Seek`, `ubik_Write`, and `ubik_Read`; `cdbread` first calls `checkDiskAddress`. `UpdateCache` reads and validates `db.h`, rebuilds a missing database header when allowed, initializes hash tables with `ht_DBInit`, and invalidates memory hash caches. `CheckInit` registers `UpdateCache` with `ubik_CheckCache`.

## Control Flow
Most server RPCs call `InitRPC`, which calls `CheckInit`; that refreshes `db.h` if Ubik says the cache changed. Reads and writes poll the LWP I/O manager every four operations in non-pthread builds.

## State And Persistence
`struct memoryDB db` is allocated here and mirrors the persistent Ubik database header plus memory hash-table caches. `dbwrite` rejects writes into the header unless the buffer aliases the in-core header field, and rejects writes past `eofPtr`.

## Dependencies And Integration Points
This file is below all budb RPC logic and above Ubik. It depends on `database.h`, `error_macros.h`, `budb_internal.h`, Ubik, auditing, and online verifier address checks.

## Risks And Test Signals
Bounds checks depend on `db.h.eofPtr` being current and network ordered. Header writes require exact pointer aliasing, so misuse of temporary buffers fails. Signals are empty-database initialization, corrupted version/checkVersion rejection, read/write error injection, and verifier-backed `cdbread` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.h -->
# sources/distributed-fs/openafs/src/budb/database.h

## Purpose
Defines the on-disk and in-memory schema for the OpenAFS backup database. This is the core contract for database layout, block allocation, hash tables, text storage, locks, and persistent dump/tape/volume records.

## Important APIs, Types, And Functions
Key types include `dbadr`, `hashTable`, `textBlock`, `db_lockS`, `dbHeader`, fixed-size `block`/`blockHeader`, `htBlock`, `volFragment`, `volInfo`, `tape`, `dump`, `memoryHTBlock`, `memoryHashTable`, and `memoryDB`. Constants define `BUDB_VERSION`, `BLOCKSIZE`, block types, hash function IDs, entry counts, and address helpers such as `BlockBase`. Macros `set_header_word`, `set_word_offset`, and `set_word_addr` update memory and persist a single word through `dbwrite`.

## Control Flow
The header encodes how higher layers work: allocate fixed-size blocks, store homogeneous records per block, index records through hash buckets, and link records through embedded `dbadr` chain fields.

## State And Persistence
The persistent root is `dbHeader` at database offset zero. It stores free lists, EOF, hash-table descriptors, text locks, text block descriptors, last IDs, update time, and check version. All multi-byte fields stored in the database are generally network ordered.

## Dependencies And Integration Points
It depends on OpenAFS backup constants, auth principal types, and Ubik transaction helpers declared elsewhere. Every budb storage module includes it.

## Risks And Test Signals
This is a high-risk layout header: changing structure sizes, padding, counts, byte order, or block constants can break existing databases. Signals include build-time size assumptions, database create/upgrade tests, online verification, dump/restore across architectures, and hash allocation traversal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/database.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_alloc.c -->
# sources/distributed-fs/openafs/src/budb/db_alloc.c

## Purpose
Implements fixed-size block and record allocation for the budb on-disk database. It manages generic free blocks and per-record-type free lists for volume fragments, volume info, tapes, and dumps.

## Important APIs, Types, And Functions
`InitDBalloc` fills `nEntries` and `sizeEntries` from schema constants. `AllocBlock` extends the database at `eofPtr` or removes a block from the generic free list. `FreeBlock` clears a block header and chains the block onto `freePtrs[free_BLOCK]`. `AllocStructure` finds or creates a block for a specific structure type, uses the first word of each record as the allocated/free marker, decrements `nFree`, and returns the record address. `FreeStructure` validates block type, marks the first word zero, increments `nFree`, and adds the block to its type free list if it was previously full.

## Control Flow
Structure allocation first reclaims fully empty typed blocks back to the generic list when possible, then scans the block for the first zero first-word slot. The caller must later write the full structure contents.

## State And Persistence
Persistent state is `db.h.freePtrs[]`, block headers, `eofPtr`, and first-word allocation markers inside records. All updates are written through `set_header_word`, `set_word_offset`, and `dbwrite` in a Ubik transaction.

## Dependencies And Integration Points
Used by `procs.c`, `db_hash.c`, and `db_text.c` to create/free dumps, tapes, volume records, hash blocks, and text blocks.

## Risks And Test Signals
Risks include free-count corruption, mismatched block type, and relying on the first record word as free marker. Signals are allocator stress tests, delete/recreate cycles, verifier free-list checks, and crash-recovery tests around partial transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_alloc.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_dump.c -->
# sources/distributed-fs/openafs/src/budb/db_dump.c

## Purpose
Serializes the budb database into a portable stream for dump/restore clients. It writes network-order headers and records for database metadata, dumps, tapes, volume entries, and text blocks while coordinating a producer thread with an RPC reader through a pipe.

## Important APIs, Types, And Functions
`canWrite`, `haveWritten`, and `doneWriting` synchronize writer/reader state in `dumpSyncPtr`. `writeStructHeader`, `writeTextHeader`, `writeDbHeader`, `writeDump`, `writeTape`, `writeVolume`, `writeText`, and `writeDatabase` generate the dump stream. `checkLock` and `checkText` guard text export.

## Control Flow
`writeDatabase` writes a database header, walks both current and old dump-id hash tables, skips appended dumps as roots, then follows each initial dump's appended chain in restore order. For each dump it writes tapes and volume fragments by following `firstTape` and `firstVol` chains, reading corresponding `volInfo` records. It then writes dump schedule, volume set, and tape host text blocks, followed by an `SD_END` marker.

## State And Persistence
The stream reflects persistent Ubik records but is not itself stored by this file. It preserves IDs, dump/tape/volume metadata, text contents, and header high-water marks. `MAXAPPENDS` and loop-count guards prevent unbounded appended-dump traversal.

## Dependencies And Integration Points
Called by `dbs_dump.c` dump worker. It depends on hash lookup, checked database reads, struct conversion helpers, text locks, `globals.h` dump synchronization, and Ubik read transactions.

## Risks And Test Signals
Risks include stale or held text locks blocking export, partial output on inconsistent chains, circular appended-dump chains, and pipe synchronization deadlocks. Signals are savedb/restoredb round trips, database dumps with appended dumps, text-block export, timeout handling, and online verifier agreement before dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_dump.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_hash.c -->
# sources/distributed-fs/openafs/src/budb/db_hash.c

## Purpose
Implements the persistent hash tables used to locate dumps by id/name, tapes by name, and volume info by name. It also performs incremental hash-table growth and provides generic chain scanning.

## Important APIs, Types, And Functions
Initialization is via `InitDBhash` and `ht_DBInit`. Core operations are `ht_HashEntry`, `ht_GetType`, `ht_LookupEntry`, `ht_HashIn`, `ht_HashOut`, `RemoveFromList`, `scanHashTable`, and `ht_LookupBucket`. Internal helpers allocate/free table blocks, cache table blocks in memory, move entries from old to new tables, and compute string/id hashes.

## Control Flow
Insertions call `ht_MaybeAdjust`; if a table is too dense and small enough to grow, the current table is moved to `oldTable` and a new table is allocated. Each operation moves up to a small quota of buckets from the old table into the current table through `ht_MoveEntries`, so resizing is incremental. Lookups search current then old tables. Deletions remove from old first when present, then current.

## State And Persistence
Persistent hash descriptors live in `db.h` and point to chains of `hashTable_BLOCK` blocks. Record linkage uses embedded chain fields whose offsets are stored in the descriptor. Memory caches in `memoryHashTable` are invalidated on header refresh.

## Dependencies And Integration Points
All high-level RPCs in `procs.c` rely on these indexes. The verifier and dump code traverse the same tables.

## Risks And Test Signals
Risks include bucket-cache invalidation mistakes, incorrect old-table progress, hash entry count drift, and chain corruption from bad offsets. Signals are insert/delete/lookup stress, forced hash growth, verifier hash-table checks, and cross-checks between name/id indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_hash.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.c -->
# sources/distributed-fs/openafs/src/budb/db_lock.c

## Purpose
Implements RPC-visible locks for budb text blocks and allocates client instance IDs. These locks protect multi-call text replacement operations.

## Important APIs, Types, And Functions
RPC wrappers `SBUDB_FreeAllLocks`, `SBUDB_FreeLock`, `SBUDB_GetInstanceId`, and `SBUDB_GetLock` audit calls and delegate to local implementations. `GetLock` validates `lockName`, checks expiration, records `lockState`, `lockTime`, `expires`, and `instanceId`, and returns a one-based handle. `FreeLock` and `FreeAllLocks` clear lock records. `checkLockHandle` validates handle range only.

## Control Flow
Lock acquisition is a write transaction. If an unexpired lock exists, the caller receives `BUDB_SELFLOCKED` for the same instance or `BUDB_LOCKED` for another. Expired locks can be overwritten. Release writes the cleared lock record back into the header.

## State And Persistence
Locks and `lastInstanceId` are persisted in the database header, so server restarts see the stored fields until overwritten/expired. Timestamps are stored in network order except local comparisons convert with `ntohl`.

## Dependencies And Integration Points
Used by `db_text.c` text save/get calls and backup clients managing dump schedules, volume sets, and tape hosts.

## Risks And Test Signals
`checkLockHandle` only checks range, not ownership or expiration, so callers must enforce protocol discipline. Signals are concurrent lock acquisition, self-lock behavior, expiration, freeing all locks for an instance, and text save rejection without a handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.h -->
# sources/distributed-fs/openafs/src/budb/db_lock.h

## Purpose
Declares the lock record layout used for budb text block locking.

## Important APIs, Types, And Functions
`db_lockS` contains `type`, `lockState`, `lockTime`, `expires`, `instanceId`, and `lockHost`. The header typedefs `db_lockT` and `db_lockP`.

## Control Flow
No executable flow is present. The structure is manipulated by `db_lock.c`, `db_text.c`, and database header code.

## State And Persistence
The fields mirror persistent lock slots in `dbHeader.textLocks`. They track whether a text block is locked, when the lock was acquired, when it expires, and which client instance owns it.

## Dependencies And Integration Points
The same structure is also defined in `database.h`, so this header is a narrow compatibility declaration for modules that need lock types without the full database schema.

## Risks And Test Signals
There is a type inconsistency: this file defines `db_lockP` as `db_lockT`, while `database.h` defines it as `db_lockT *`. Compile coverage determines which declaration is actually used. Tests should cover lock RPCs and any consumer including this header directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_text.c -->
# sources/distributed-fs/openafs/src/budb/db_text.c

## Purpose
Manages persistent text objects stored inside the budb database, such as dump schedules, volume sets, and tape hosts. It supports chunked reads and lock-protected chunked replacement.

## Important APIs, Types, And Functions
RPC wrappers audit `GetText`, `GetTextVersion`, and `SaveText`. `GetText` reads a byte range from the committed text chain. `SaveText` builds a replacement chain in `newTextAddr/newsize`, commits it when `BUDB_TEXT_COMPLETE` is set, increments the version, and frees old blocks. `freeOldBlockChain` releases obsolete text blocks. `saveTextToFile` is debug support.

## Control Flow
Readers validate text type, offset, and a syntactically valid lock handle, then skip blocks until the requested offset and copy up to `maxLength`. Writers require a valid lock handle. Offset zero discards any previous staged replacement and starts a new block chain; later calls must append exactly at `newsize`. Completion swaps new and old chains atomically within the transaction.

## State And Persistence
Text contents are linked `text_BLOCK` database blocks. `textBlock` header fields persist committed and staged chains, sizes, and versions. Each `SaveText` chunk is capped at one block data payload.

## Dependencies And Integration Points
Uses `db_alloc.c` block allocation, `database.c` I/O, `db_lock.c` handle validation, and RPC/audit infrastructure. Clients use the fields from `budb_client.h`.

## Risks And Test Signals
Handle validation does not check ownership. Interrupted replacement can leave `newTextAddr` staged until the next offset-zero save frees it. Signals are multi-chunk save/get, version increment, complete vs incomplete save, lock failure, empty text, and verifier text-chain checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_text.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/dbs_dump.c -->
# sources/distributed-fs/openafs/src/budb/dbs_dump.c

## Purpose
Exposes the database dump and header-restore RPCs. It starts a worker to serialize the database through `writeDatabase`, streams chunks to clients, and watches for stalled dump readers.

## Important APIs, Types, And Functions
`DumpDB` implements the streaming RPC; `setupDbDump` runs the writer side; `RestoreDbHeader` merges saved header high-water marks; `dumpWatcher` enforces a timeout; `badEntry` is a placeholder that currently always accepts entries.

## Control Flow
The first `DumpDB` call initializes `dumpSyncPtr`, creates a pipe, starts the database dumper and watcher, and returns data read from the pipe. Subsequent calls read more chunks. A zero-length call refreshes the timeout. End-of-stream closes the read side and clears dump-in-progress state. The watcher cancels/destroys the dumper and aborts the Ubik transaction if clients stop polling.

## State And Persistence
Runtime state lives in global `dumpSync`. The dump itself is generated from a read transaction. `RestoreDbHeader` persists only merged `lastDumpId`, `lastTapeId`, and `lastInstanceId` values after version validation.

## Dependencies And Integration Points
Integrates RPC clients with `db_dump.c`, Ubik transactions, LWP or pthread synchronization, audit events, and `globals.h` dump synchronization fields.

## Risks And Test Signals
Risks include one global dump at a time, pipe/condition synchronization races, timeout cleanup correctness, and pthread path passing `NULL` where the worker expects a write fd. Signals are streaming savedb in chunks, zero-length keepalive, simultaneous dump rejection, timeout abort, and header-restore version mismatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/dbs_dump.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/error_macros.h -->
# sources/distributed-fs/openafs/src/budb/error_macros.h

## Purpose
Defines local error-handling macros used throughout budb server code.

## Important APIs, Types, And Functions
`ERROR(evalue)` assigns `code` and jumps to `error_exit`. `ABORT(evalue)` assigns `code` and jumps to `abort_exit`. `BUDB_EXIT(evalue)` audits a server exit event and calls `exit`.

## Control Flow
The macros standardize the common transaction pattern: validate, perform work, jump to cleanup on errors, and either end or abort the Ubik transaction in labeled cleanup blocks.

## State And Persistence
No direct state is stored. Indirectly, correct use determines whether partial persistent database mutations are committed or aborted.

## Dependencies And Integration Points
Used across database, allocation, hash, text, dump, verify, and RPC modules. `BUDB_EXIT` depends on audit infrastructure.

## Risks And Test Signals
The macros assume a local variable named `code` and matching labels. Misuse can jump past required cleanup or abort the wrong transaction. Compile warnings, static analysis for labels, and transaction error-path tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/error_macros.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/globals.h -->
# sources/distributed-fs/openafs/src/budb/globals.h

## Purpose
Defines global budb server configuration and database-dump synchronization structures shared across server modules.

## Important APIs, Types, And Functions
Configuration includes `DEFAULT_DBPREFIX`, debug flags `DF_NOAUTH`, `DF_RECHECKNOAUTH`, `DF_SMALLHT`, and `DF_TRUNCATEDB`, and `buServerConfS` with database directory/name, host/server list, cell config path, Ubik database handle, and debug flags. Dump synchronization uses `dumpSyncS`, status flags `DS_WAITING`, `DS_DONE`, `DS_DONE_ERROR`, and timeout increment `DUMP_TTL_INC`.

## Control Flow
No executable flow is present, but `dumpSyncS` fields define the producer/consumer protocol between `dbs_dump.c` and `db_dump.c`: pipe fds, status flags, condition variables or LWP process handles, active Ubik transaction, buffered byte count, and TTL.

## State And Persistence
`globalConfPtr` is process-global configuration. `dumpSyncPtr` points to runtime state only. Persistent database location and Ubik membership are derived from configuration fields.

## Dependencies And Integration Points
Included by server initialization, RPC setup, database dump streaming, and authentication configuration code.

## Risks And Test Signals
Risks are global mutable state, noauth debug flags, and synchronization divergence between pthread and LWP builds. Signals are startup with configured server lists, noauth detection, dump streaming under both threading models, and timeout cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/globals.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/ol_verify.c -->
# sources/distributed-fs/openafs/src/budb/ol_verify.c

## Purpose
Performs online consistency verification of the budb database. It walks blocks, hash tables, free lists, text chains, and record relationships to detect corruption while the server is running.

## Important APIs, Types, And Functions
`DbVerify` is the RPC entry, wrapping `verifyDatabase`. `checkDiskAddress` and `ConvertDiskAddress` validate disk addresses and map them to block/entry indexes. Specific validators include `verifyDumpEntry`, `verifyTapeEntry`, `verifyVolFragEntry`, `verifyVolInfoEntry`, `verifyBlocks`, `verifyHashTable`, `verifyEntryChains`, `verifyFreeLists`, `verifyMapBits`, `verifyText`, and `verifyTextChain`. `blockMap` records per-block/per-entry flags such as hash membership, free state, tape/dump linkage, text usage, and appended-dump linkage.

## Control Flow
`verifyDatabase` computes block count from `eofPtr`, allocates a block map, reads all block headers, verifies each current and old hash table, validates record chains, checks text chains, checks free lists, and finally ensures each entry has a compatible combination of map bits.

## State And Persistence
It does not repair data. It builds transient verification state in `miscData` and `blockMap`, reads persistent Ubik blocks, and reports status/error counts. `DbVerify` returns host address and status to the caller.

## Dependencies And Integration Points
Used by admin verification RPCs and by `cdbread` address validation. It depends on `database.h` schema, hash helpers, Ubik read transactions, audit, and logging.

## Risks And Test Signals
Risks include verifier assumptions matching schema exactly, a noted `checkEntry` table comment saying it may not match `typeName[]`, and limited tolerance after 50 errors in normal builds. Signals are clean verification after create/add/delete, deliberate corruption fixtures for bad links/free counts/hash buckets, text chain checks, and old-hash-table migration cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/ol_verify.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/procs.c -->
# sources/distributed-fs/openafs/src/budb/procs.c

## Purpose
Implements the main budb RPC service for dump, tape, and volume metadata. It creates and finishes dumps/tapes, records volumes, deletes database objects, lists/query entries, manages appended dumps, and provides debug dump/hash inspection RPCs.

## Important APIs, Types, And Functions
Initialization and security use `InitProcs`, `AwaitInitialization`, `callPermitted`, and `InitRPC`. Fill/list helpers include `FillVolEntry`, `FillDumpEntry`, `FillTapeEntry`, `returnList`, `AddToReturnList`, and `SendReturnList`. Mutation helpers include `GetVolInfo`, `DeleteVolInfo`, `DeleteVolFragment`, `DeleteTape`, `DeleteDump`, `deleteSomeVolumesFromTape`, `deleteDump`, `getExpiration`, and `makeAppended`. RPC bodies include `AddVolume(s)`, `CreateDump`, `DoDeleteDump`, `DoDeleteTape`, `DeleteVDP`, `FindClone`, `FindDump`, `FindLatestDump`, `FinishDump`, `FinishTape`, `GetDumps`, `GetTapes`, `GetVolumes`, `UseTape`, `MakeDumpAppended`, `FindLastTape`, `T_DumpHashTable`, `T_GetVersion`, and `T_DumpDatabase`.

## Control Flow
Every meaningful RPC opens a Ubik transaction through `InitRPC`, validates permissions/arguments, uses hash tables to locate records, mutates linked on-disk records, updates `lastUpdate` for writes, and ends or aborts the transaction through `ERROR`/`ABORT` labels. Dumps are created in-progress, tapes are attached and marked being written, volumes create fragments linked to both tape and volInfo, then finish calls clear in-progress flags. Deletes are staged in small transactions, removing volume fragments before tapes and dumps.

## State And Persistence
Persistent state is the budb graph: dumps indexed by id/name, tapes indexed by name and linked to dumps, volume fragments linked to tapes and volume info, volume info same-name chains, appended dump chains, and header counters/timestamps. Some query RPCs intentionally allow unauthenticated specific lookups.

## Dependencies And Integration Points
This is the service layer above `database.c`, `db_alloc.c`, `db_hash.c`, and struct conversion helpers. It integrates RX/RXKAD identity, afsconf superuser checks, Ubik replication, audit events, backup client RPC structs, and debug file output under `gettmpdir()`.

## Risks And Test Signals
Risks include complex linked-structure invariants, partial delete progress, unchecked string copies after length validation gaps, appended-dump loop/cycle handling outside verifier, global noauth mode, and broad debug RPC file output. Signals are end-to-end dump lifecycle tests, volume batch add, appended dump chains, delete interruption/retry, list pagination via `nextIndex`, find latest/clone/last tape, verifier after each mutation, and permission/noauth tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/procs.c -->
